"""Представления приложения users: регистрация, кабинет, профили, портфолио, уведомления."""
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator

from apps.applications.models import Application
from apps.orders.models import Category, Order
from apps.projects.models import Project
from apps.reviews.models import Review

from .forms import (
    PortfolioItemForm,
    ProfileForm,
    RegisterForm,
    StyledPasswordChangeForm,
)
from .models import Notification, PortfolioItem, User, notify


def home(request):
    """Главная страница: витрина открытых заказов и краткая статистика биржи."""
    open_orders = Order.objects.filter(status=Order.Status.OPEN)
    categories = (
        Category.objects.annotate(
            open_orders_count=Count("orders", filter=Q(orders__in=open_orders))
        )
        .order_by("-open_orders_count", "name")[:8]
    )
    completed_projects = Project.objects.filter(status=Project.Status.COMPLETED)
    context = {
        "latest_orders": open_orders.select_related("category", "owner").order_by(
            "-created_at"
        )[:6],
        "categories": categories,
        "stats": {
            "orders": open_orders.count(),
            "freelancers": User.objects.filter(role=User.Role.FREELANCER).count(),
            "projects": completed_projects.count(),
            "reviews": Review.objects.count(),
        },
    }
    return render(request, "users/home.html", context)


def register(request):
    """Регистрация нового пользователя с выбором роли."""
    if request.user.is_authenticated:
        return redirect("users:dashboard")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        notify(
            user,
            title="Добро пожаловать в Taskly!",
            body="Заполните профиль и портфолио — это повысит доверие заказчиков.",
            type_=Notification.Type.SYSTEM,
            link="/dashboard/",
        )
        messages.success(request, "Регистрация завершена. Добро пожаловать!")
        return redirect("users:dashboard")

    return render(request, "users/register.html", {"form": form})


@login_required
def dashboard(request):
    """Личный кабинет: активные проекты, заказы, отклики и статистика."""
    user = request.user
    context = {"page_title": "Личный кабинет"}

    if user.is_customer or user.is_superuser:
        orders = Order.objects.filter(owner=user)
        received = Application.objects.filter(order__owner=user)
        projects = Project.objects.filter(customer=user)
        context.update(
            {
                "mode": "customer",
                "orders": orders.select_related("category").order_by("-created_at")[:5],
                "orders_total": orders.count(),
                "orders_open": orders.filter(status=Order.Status.OPEN).count(),
                "applications_received": received.select_related(
                    "freelancer", "order"
                ).order_by("-created_at")[:5],
                "applications_pending": received.filter(
                    status=Application.Status.PENDING
                ).count(),
                "projects": projects.select_related("order", "freelancer").order_by(
                    "-started_at"
                )[:5],
                "projects_active": projects.filter(
                    status=Project.Status.ACTIVE
                ).count(),
                "projects_completed": projects.filter(
                    status=Project.Status.COMPLETED
                ).count(),
                "budget_spent": projects.filter(
                    status=Project.Status.COMPLETED
                ).aggregate(total=Sum("price"))["total"]
                or 0,
                "rating": user.rating,
            }
        )

    elif user.is_freelancer:
        sent = Application.objects.filter(freelancer=user)
        projects = Project.objects.filter(freelancer=user)
        context.update(
            {
                "mode": "freelancer",
                "applications_sent": sent.select_related("order").order_by(
                    "-created_at"
                )[:5],
                "applications_sent_total": sent.count(),
                "applications_pending": sent.filter(
                    status=Application.Status.PENDING
                ).count(),
                "applications_accepted": sent.filter(
                    status=Application.Status.ACCEPTED
                ).count(),
                "freelancer_projects": projects.select_related(
                    "order", "customer"
                ).order_by("-started_at")[:5],
                "freelancer_projects_active": projects.filter(
                    status=Project.Status.ACTIVE
                ).count(),
                "freelancer_projects_completed": projects.filter(
                    status=Project.Status.COMPLETED
                ).count(),
                "earned": projects.filter(status=Project.Status.COMPLETED).aggregate(
                    total=Sum("price")
                )["total"]
                or 0,
                "portfolio_count": user.portfolio_items.count(),
                "rating": user.rating,
            }
        )

    return render(request, "users/dashboard.html", context)


def profile(request, pk):
    """Публичная страница пользователя: данные, портфолио, отзывы, рейтинг."""
    profile_user = get_object_or_404(User, pk=pk)
    reviews = (
        profile_user.reviews_received.select_related("author", "project")
        .order_by("-created_at")
    )
    paginator = Paginator(reviews, 5)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "profile_user": profile_user,
        "portfolio": profile_user.portfolio_items.all(),
        "page_obj": page_obj,
        "reviews_total": paginator.count,
        "open_orders": Order.objects.filter(
            owner=profile_user, status=Order.Status.OPEN
        ).count(),
        "completed_projects": Project.objects.filter(
            Q(customer=profile_user) | Q(freelancer=profile_user),
            status=Project.Status.COMPLETED,
        ).count(),
    }
    return render(request, "users/profile.html", context)


@login_required
def profile_edit(request):
    """Редактирование собственного профиля."""
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Профиль обновлён.")
        return redirect("users:profile", pk=request.user.pk)
    return render(request, "users/profile_edit.html", {"form": form})


@login_required
def password_change(request):
    """Смена пароля."""
    form = StyledPasswordChangeForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Пароль изменён.")
        return redirect("users:dashboard")
    return render(request, "users/password_change.html", {"form": form})


@login_required
def portfolio_create(request):
    """Добавление работы в портфолио."""
    form = PortfolioItemForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        item.owner = request.user
        item.save()
        messages.success(request, "Работа добавлена в портфолио.")
        return redirect("users:profile", pk=request.user.pk)
    return render(request, "users/portfolio_form.html", {"form": form, "item": None})


@login_required
def portfolio_update(request, pk):
    """Редактирование работы портфолио."""
    item = get_object_or_404(PortfolioItemModel, pk=pk)
    if item.owner_id != request.user.pk and not request.user.is_superuser:
        raise PermissionDenied("Это чужая работа в портфолио.")
    form = PortfolioItemForm(request.POST or None, request.FILES or None, instance=item)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Работа обновлена.")
        return redirect("users:profile", pk=request.user.pk)
    return render(
        request, "users/portfolio_form.html", {"form": form, "item": item}
    )


@login_required
def portfolio_delete(request, pk):
    """Удаление работы портфолио."""
    item = get_object_or_404(PortfolioItemModel, pk=pk)
    if item.owner_id != request.user.pk and not request.user.is_superuser:
        raise PermissionDenied("Это чужая работа в портфолио.")
    if request.method == "POST":
        item.delete()
        messages.success(request, "Работа удалена из портфолио.")
        return redirect("users:profile", pk=request.user.pk)
    return render(request, "users/portfolio_confirm_delete.html", {"item": item})


@login_required
def notifications(request):
    """Список уведомлений пользователя."""
    queryset = Notification.objects.filter(recipient=request.user)
    only_unread = request.GET.get("unread") == "1"
    if only_unread:
        queryset = queryset.filter(is_read=False)
    paginator = Paginator(queryset, 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "users/notifications.html",
        {"page_obj": page_obj, "only_unread": only_unread, "total": queryset.count()},
    )


@login_required
def notification_mark_read(request, pk):
    """Отметить уведомление прочитанным."""
    notification = get_object_or_404(
        Notification, pk=pk, recipient=request.user
    )
    notification.mark_as_read()
    return redirect(notification.link or "users:notifications")


@login_required
def notifications_mark_all_read(request):
    """Отметить прочитанными все уведомления."""
    if request.method == "POST":
        Notification.objects.filter(recipient=request.user, is_read=False).update(
            is_read=True
        )
        messages.success(request, "Все уведомления отмечены как прочитанные.")
    return redirect("users:notifications")
