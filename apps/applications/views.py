"""Представления приложения applications."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.orders.models import Order
from apps.users.mixins import freelancer_required
from apps.users.models import Notification, notify

from .forms import ApplicationForm
from .models import Application
from .services import accept_application, reject_application, withdraw_application


@login_required
@freelancer_required
def application_create(request, order_pk):
    """Отправка отклика на заказ."""
    order = get_object_or_404(Order, pk=order_pk)
    if request.method != "POST":
        return redirect("orders:detail", pk=order.pk)

    form = ApplicationForm(request.POST, order=order, freelancer=request.user)
    if form.is_valid():
        application = form.save()
        messages.success(request, "Отклик отправлен заказчику.")
        notify(
            order.owner,
            title=f"Новый отклик к заказу «{order.title}»",
            body=f"{request.user.display_name}: {application.price_display} за {application.days} дн.",
            actor=request.user,
            type_=Notification.Type.NEW_APPLICATION,
            link=reverse("applications:for_order", kwargs={"order_pk": order.pk}),
        )
    else:
        messages.error(request, "Не удалось отправить отклик: проверьте данные формы.")
    return redirect("orders:detail", pk=order.pk)


@login_required
@freelancer_required
def my_applications(request):
    """Список откликов, отправленных текущим фрилансером."""
    queryset = (
        Application.objects.filter(freelancer=request.user)
        .select_related("order", "order__category")
        .order_by("-created_at")
    )
    status_param = request.GET.get("status")
    if status_param and status_param in dict(Application.Status.choices):
        queryset = queryset.filter(status=status_param)

    paginator = Paginator(queryset, 10)
    return render(
        request,
        "applications/my_applications.html",
        {
            "page_obj": paginator.get_page(request.GET.get("page")),
            "applications_total": queryset.count(),
            "statuses": Application.Status.choices,
            "current_status": status_param or "",
        },
    )


@login_required
def order_applications(request, order_pk):
    """Отклики на заказ — видит только заказчик (владелец заказа)."""
    order = get_object_or_404(Order, pk=order_pk)
    if not order.can_be_edited_by(request.user):
        raise PermissionDenied("Список откликов доступен только автору заказа.")

    applications = (
        order.applications.select_related("freelancer")
        .order_by("status", "-created_at")
    )
    paginator = Paginator(applications, 10)
    return render(
        request,
        "applications/order_applications.html",
        {
            "order": order,
            "page_obj": paginator.get_page(request.GET.get("page")),
            "applications_total": order.applications.count(),
            "pending_count": order.applications.filter(
                status=Application.Status.PENDING
            ).count(),
        },
    )


def _get_application_for_owner(pk, user):
    application = get_object_or_404(
        Application.objects.select_related("order", "freelancer"), pk=pk
    )
    if not application.order.can_be_edited_by(user):
        raise PermissionDenied("Решения по откликам принимает только автор заказа.")
    return application


@login_required
def application_accept(request, pk):
    """Принять отклик и создать проект."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    application = _get_application_for_owner(pk, request.user)
    try:
        project = accept_application(application, request.user)
    except ValueError as exc:
        messages.error(request, str(exc))
        return redirect("applications:for_order", order_pk=application.order_id)
    messages.success(request, "Отклик принят, проект создан.")
    return redirect("projects:detail", pk=project.pk)


@login_required
def application_reject(request, pk):
    """Отклонить отклик."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    application = _get_application_for_owner(pk, request.user)
    try:
        reject_application(application, request.user)
    except ValueError as exc:
        messages.error(request, str(exc))
        return redirect("applications:for_order", order_pk=application.order_id)
    messages.success(request, "Отклик отклонён.")
    return redirect("applications:for_order", order_pk=application.order_id)


@login_required
def application_withdraw(request, pk):
    """Отозвать собственный отклик."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    application = get_object_or_404(
        Application.objects.select_related("order", "freelancer"), pk=pk
    )
    if application.freelancer_id != request.user.pk and not request.user.is_superuser:
        raise PermissionDenied("Отозвать отклик может только его автор.")
    try:
        withdraw_application(application, request.user)
    except ValueError as exc:
        messages.error(request, str(exc))
        return redirect("applications:my")
    messages.success(request, "Отклик отозван.")
    return redirect("applications:my")
