"""Бизнес-логика проектов: завершение и отмена."""
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from apps.orders.models import Order
from apps.users.models import Notification, notify

from .models import Project


def _other_participant(project, actor):
    return project.customer if actor.pk == project.freelancer_id else project.freelancer


@transaction.atomic
def complete_project(project, actor, summary=""):
    """Завершить проект: закрыть заказ и уведомить вторую сторону."""
    if project.status != Project.Status.ACTIVE:
        raise ValueError("Завершить можно только проект со статусом «в работе».")

    project.status = Project.Status.COMPLETED
    project.completed_at = timezone.now()
    if summary:
        project.summary = summary
    project.save(update_fields=["status", "completed_at", "summary"])

    order = project.order
    order.status = Order.Status.COMPLETED
    order.save(update_fields=["status"])

    recipient = _other_participant(project, actor)
    notify(
        recipient,
        title=f"Проект «{project.title}» завершён",
        body="Вы можете оставить отзыв о сотрудничестве.",
        actor=actor,
        type_=Notification.Type.PROJECT_COMPLETED,
        link=reverse("reviews:create", kwargs={"project_pk": project.pk}),
    )
    return project


@transaction.atomic
def cancel_project(project, actor, reason=""):
    """Отменить проект и соответствующий заказ."""
    if project.status == Project.Status.COMPLETED:
        raise ValueError("Завершённый проект нельзя отменить.")

    project.status = Project.Status.CANCELLED
    project.completed_at = timezone.now()
    if reason:
        project.summary = reason
    project.save(update_fields=["status", "completed_at", "summary"])

    order = project.order
    order.status = Order.Status.CANCELLED
    order.save(update_fields=["status"])

    recipient = _other_participant(project, actor)
    notify(
        recipient,
        title=f"Проект «{project.title}» отменён",
        body=reason or "Инициатор не указал причину.",
        actor=actor,
        type_=Notification.Type.SYSTEM,
        link=reverse("projects:detail", kwargs={"pk": project.pk}),
    )
    return project
