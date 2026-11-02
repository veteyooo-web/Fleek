"""Контекст-процессор: счётчики непрочитанных уведомлений и сообщений для шапки."""
from apps.messages.models import Message

from .models import Notification


def user_counters(request):
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return {}
    return {
        "unread_notifications": Notification.objects.filter(
            recipient=user, is_read=False
        ).count(),
        "unread_messages": Message.objects.filter(
            conversation__participants=user, is_read=False
        ).exclude(sender=user).count(),
    }
