"""Бизнес-логика откликов: принятие, отклонение, отзыв + уведомления."""
from datetime import timedelta

from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from apps.orders.models import Order
from apps.users.models import Notification, notify

from .models import Application


def _order_link(order):
    return reverse("orders:detail", kwargs={"pk": order.pk})


@transaction.atomic
def accept_application(application, actor):
    """Принять отклик: создать проект, закрыть набор, разослать уведомления."""
    if application.status != Application.Status.PENDING:
        raise ValueError("Принять можно только отклик со статусом «на рассмотрении».")

    order = application.order
    application.status = Application.Status.ACCEPTED
    application.answered_at = timezone.now()
    application.save(update_fields=["status", "answered_at"])

    order.status = Order.Status.IN_PROGRESS
    order.save(update_fields=["status"])

    # Локальный импорт: projects ссылается на orders/users, циклов не будет.
    from apps.projects.models import Project

    deadline = order.deadline or (timezone.localdate() + timedelta(days=application.days))
    project = Project.objects.create(
        order=order,
        customer=order.owner,
        freelancer=application.freelancer,
        title=order.title,
        description=order.description,
        price=application.price,
        deadline=deadline,
    )

    other_pending = list(
        order.applications.filter(status=Application.Status.PENDING).exclude(
            pk=application.pk
        )
    )
    if other_pending:
        Application.objects.filter(pk__in=[a.pk for a in other_pending]).update(
            status=Application.Status.REJECTED, answered_at=timezone.now()
        )
    for other in other_pending:
        notify(
            other.freelancer,
            title=f"Отклик на заказ «{order.title}» отклонён",
            body="Заказчик выбрал другого исполнителя.",
            actor=actor,
            type_=Notification.Type.APPLICATION_REJECTED,
            link=_order_link(order),
        )

    notify(
        application.freelancer,
        title=f"Ваш отклик принят: {order.title}",
        body="Создан проект, можно приступать к работе.",
        actor=actor,
        type_=Notification.Type.PROJECT_STARTED,
        link=reverse("projects:detail", kwargs={"pk": project.pk}),
    )
    return project


@transaction.atomic
def reject_application(application, actor):
    """Отклонить отклик."""
    if application.status != Application.Status.PENDING:
        raise ValueError("Отклонить можно только отклик со статусом «на рассмотрении».")
    application.status = Application.Status.REJECTED
    application.answered_at = timezone.now()
    application.save(update_fields=["status", "answered_at"])
    notify(
        application.freelancer,
        title=f"Отклик на заказ «{application.order.title}» отклонён",
        body=application.order.owner.display_name + " не выбрал вашу кандидатуру.",
        actor=actor,
        type_=Notification.Type.APPLICATION_REJECTED,
        link=_order_link(application.order),
    )
    return application


@transaction.atomic
def withdraw_application(application, actor):
    """Отозвать свой отклик (пока он на рассмотрении)."""
    if application.status != Application.Status.PENDING:
        raise ValueError("Отозвать можно только отклик со статусом «на рассмотрении».")
    application.status = Application.Status.WITHDRAWN
    application.answered_at = timezone.now()
    application.save(update_fields=["status", "answered_at"])
    notify(
        application.order.owner,
        title=f"{actor.display_name} отозвал свой отклик",
        body=f"Заказ: {application.order.title}",
        actor=actor,
        type_=Notification.Type.SYSTEM,
        link=_order_link(application.order),
    )
    return application
