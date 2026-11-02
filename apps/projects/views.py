"""Представления приложения projects."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render

from apps.applications.models import Application

from .forms import ProjectCancelForm, ProjectCompleteForm
from .models import Project
from .services import cancel_project, complete_project


@login_required
def project_list(request):
    """Список проектов пользователя (как заказчика или как исполнителя)."""
    user = request.user
    queryset = (
        Project.objects.filter(Q(customer=user) | Q(freelancer=user))
        .select_related("order", "customer", "freelancer")
        .order_by("-started_at")
    )

    status_param = request.GET.get("status")
    if status_param and status_param in dict(Project.Status.choices):
        queryset = queryset.filter(status=status_param)

    search = request.GET.get("q", "").strip()
    if search:
        queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))

    counts = (
        Project.objects.filter(Q(customer=user) | Q(freelancer=user))
        .values("status")
        .annotate(total=Count("id"))
    )
    status_counts = {row["status"]: row["total"] for row in counts}
    status_tabs = [
        {"value": value, "label": label, "count": status_counts.get(value, 0)}
        for value, label in Project.Status.choices
    ]

    paginator = Paginator(queryset, 10)
    return render(
        request,
        "projects/project_list.html",
        {
            "page_obj": paginator.get_page(request.GET.get("page")),
            "statuses": Project.Status.choices,
            "status_tabs": status_tabs,
            "current_status": status_param or "",
            "status_counts": status_counts,
            "search": search,
            "total": queryset.count(),
        },
    )


@login_required
def project_detail(request, pk):
    """Карточка проекта: условия, стороны, статус, действия."""
    project = get_object_or_404(
        Project.objects.select_related("order", "order__category", "customer", "freelancer"),
        pk=pk,
    )
    if not project.is_participant(request.user) and not request.user.is_superuser:
        raise PermissionDenied("Проект виден только заказчику и исполнителю.")

    application = Application.objects.filter(order=project.order).select_related("freelancer").first()
    reviews = project.reviews.select_related("author")

    complete_form = ProjectCompleteForm(instance=project) if project.is_active else None
    cancel_form = ProjectCancelForm() if project.status != Project.Status.CANCELLED else None

    return render(
        request,
        "projects/project_detail.html",
        {
            "project": project,
            "application": application,
            "reviews": reviews,
            "complete_form": complete_form,
            "cancel_form": cancel_form,
            "partner": project.customer if request.user.pk == project.freelancer_id else project.freelancer,
            "can_review": project.can_be_reviewed_by(request.user),
        },
    )


@login_required
def project_complete(request, pk):
    """Завершение проекта участником."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    project = get_object_or_404(Project, pk=pk)
    if not project.is_participant(request.user):
        raise PermissionDenied("Завершить проект могут только его стороны.")

    form = ProjectCompleteForm(request.POST, instance=project)
    if not form.is_valid():
        messages.error(request, "Заполните описание итога работы.")
        return redirect("projects:detail", pk=project.pk)

    complete_project(project, request.user, summary=form.cleaned_data["summary"])
    messages.success(request, "Проект завершён. Не забудьте оставить отзыв!")
    return redirect("projects:detail", pk=project.pk)


@login_required
def project_cancel(request, pk):
    """Отмена проекта участником."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    project = get_object_or_404(Project, pk=pk)
    if not project.is_participant(request.user):
        raise PermissionDenied("Отменить проект могут только его стороны.")

    reason = request.POST.get("reason", "").strip()
    try:
        cancel_project(project, request.user, reason=reason)
    except ValueError as exc:
        messages.error(request, str(exc))
        return redirect("projects:detail", pk=project.pk)

    messages.success(request, "Проект отменён, заказ закрыт.")
    return redirect("projects:detail", pk=project.pk)
