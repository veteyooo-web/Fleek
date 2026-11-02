"""Сигналы приложения reviews."""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from apps.users.models import Notification, notify

from .models import Review


@receiver(post_save, sender=Review)
def notify_new_review(sender, instance, created, **kwargs):
    """Уведомить пользователя о новом отзыве о нём."""
    if not created:
        return
    notify(
        instance.target,
        title=f"Новый отзыв о вас: {instance.rating}★",
        body=instance.comment[:200],
        actor=instance.author,
        type_=Notification.Type.NEW_REVIEW,
        link=reverse("users:profile", kwargs={"pk": instance.target_id}),
    )
