"""Представления приложения orders."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render

from apps.applications.forms import ApplicationForm
from apps.users.mixins import customer_required

from .forms import OrderForm, OrderSearchForm, OrderUpdateForm
from .models import Category, Order

VISIBLE_STATUSES_EXCLUDE = [Order.Status.DRAFT]


def order_list(request):
    """Список заказов с поиском, фильтрацией и пагинацией."""
    form = OrderSearchForm(request.GET or None)
    queryset = (
        Order.objects.select_related("category", "owner")
        .annotate(applications_total=Count("applications"))
        .exclude(status__in=VISIBLE_STATUSES_EXCLUDE)
    )
    if form.is_valid():
        queryset = form.filter_queryset(queryset)
    else:
        queryset = queryset.order_by("-created_at")

    paginator = Paginator(queryset, 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "orders/order_list.html",
        {
            "form": form,
            "page_obj": page_obj,
            "total": paginator.count,
            "is_filtered": bool(request.GET),
            "categories": Category.objects.all(),
        },
    )


def order_detail(request, pk):
    """Карточка заказа: описание, заказчик, отклики (для владельца), форма отклика."""
    order = get_object_or_404(
        Order.objects.select_related("category", "owner").annotate(
            applications_total=Count("applications")
        ),
        pk=pk,
    )
    is_owner = order.can_be_edited_by(request.user)
    if order.status == Order.Status.DRAFT and not is_owner:
        return redirect("orders:list")

    user = request.user
    can_apply = (
        user.is_authenticated
        and not is_owner
        and (user.is_freelancer or user.is_superuser)
        and order.is_open
        and not order.applications.filter(freelancer=user).exists()
    )
    already_applied = (
        user.is_authenticated
        and order.applications.filter(freelancer=user).exists()
    )
    is_favorite = user.is_authenticated and order.favorites.filter(pk=user.pk).exists()

    context = {
        "order": order,
        "is_owner": is_owner,
        "can_apply": can_apply,
        "already_applied": already_applied,
        "is_favorite": is_favorite,
        "application_form": ApplicationForm(order=order) if can_apply else None,
        "applications": (
            order.applications.select_related("freelancer").order_by("-created_at")
            if is_owner
            else None
        ),
        "project": getattr(order, "project", None),
        "similar_orders": Order.objects.filter(category=order.category)
        .exclude(pk=order.pk)
        .exclude(status=Order.Status.DRAFT)
        .select_related("category", "owner")[:4],
    }
    return render(request, "orders/order_detail.html", context)


@login_required
@customer_required
def order_create(request):
    """Создание заказа (только для заказчиков)."""
    form = OrderForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.instance.owner = request.user
        order = form.save()
        messages.success(
            request,
            "Черновик сохранён."
            if order.status == Order.Status.DRAFT
            else "Заказ опубликован!",
        )
        return redirect("orders:detail", pk=order.pk)
    return render(
        request,
        "orders/order_form.html",
        {"form": form, "page_title": "Новый заказ"},
    )


@login_required
def order_update(request, pk):
    """Редактирование заказа его владельцем."""
    order = get_object_or_404(Order, pk=pk)
    if not order.can_be_edited_by(request.user):
        raise PermissionDenied("Редактировать заказ может только его автор.")
    if hasattr(order, "project"):
        raise PermissionDenied(
            "Заказ уже принят в работу — изменение недоступно, сначала завершите проект."
        )

    form = OrderUpdateForm(request.POST or None, instance=order)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Изменения заказа сохранены.")
        return redirect("orders:detail", pk=order.pk)
    return render(
        request,
        "orders/order_form.html",
        {"form": form, "order": order, "page_title": "Редактирование заказа"},
    )


@login_required
def order_delete(request, pk):
    """Удаление заказа владельцем."""
    order = get_object_or_404(Order, pk=pk)
    if not order.can_be_edited_by(request.user):
        raise PermissionDenied("Удалить заказ может только его автор.")
    if hasattr(order, "project"):
        raise PermissionDenied("Нельзя удалить заказ, по которому идёт проект.")

    if request.method == "POST":
        order.delete()
        messages.success(request, "Заказ удалён.")
        return redirect("orders:my")
    return render(request, "orders/order_confirm_delete.html", {"order": order})


@login_required
def order_toggle_favorite(request, pk):
    """Добавить/убрать заказ в избранное."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    order = get_object_or_404(Order, pk=pk)
    if order.favorites.filter(pk=request.user.pk).exists():
        order.favorites.remove(request.user)
        messages.info(request, "Заказ убран из избранного.")
    else:
        order.favorites.add(request.user)
        messages.success(request, "Заказ добавлен в избранное.")
    return redirect("orders:detail", pk=order.pk)


@login_required
def order_my(request):
    """Мои заказы и история заказов."""
    orders = (
        Order.objects.filter(owner=request.user)
        .select_related("category")
        .annotate(applications_total=Count("applications"))
        .order_by("-created_at")
    )
    status_param = request.GET.get("status")
    if status_param and status_param in dict(Order.Status.choices):
        orders = orders.filter(status=status_param)
    paginator = Paginator(orders, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "orders/order_my.html",
        {
            "page_obj": page_obj,
            "statuses": Order.Status.choices,
            "current_status": status_param or "",
        },
    )


@login_required
def favorites(request):
    """Избранные заказы пользователя."""
    orders = (
        request.user.favorite_orders.select_related("category", "owner")
        .annotate(applications_total=Count("applications"))
        .order_by("-created_at")
    )
    paginator = Paginator(orders, 9)
    return render(
        request,
        "orders/order_favorites.html",
        {"page_obj": paginator.get_page(request.GET.get("page"))},
    )


def category_list(request):
    """Страница со всеми категориями и количеством заказов."""
    categories = (
        Category.objects.annotate(
            orders_total=Count("orders"),
            orders_open=Count("orders", filter=Q(orders__status=Order.Status.OPEN)),
        )
        .order_by("name")
    )
    return render(request, "orders/category_list.html", {"categories": categories})
