"""Модели личных сообщений: диалоги и сообщения."""
from django.conf import settings
from django.db import models


class Conversation(models.Model):
    """Личный диалог между двумя пользователями."""

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="Участники",
        related_name="conversations",
        blank=True,
    )
    subject = models.CharField("Тема", max_length=150, blank=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Последняя активность", auto_now=True)

    class Meta:
        verbose_name = "Диалог"
        verbose_name_plural = "Диалоги"
        ordering = ["-updated_at"]

    def __str__(self):
        names = ", ".join(str(p) for p in self.participants.all())
        return f"Диалог: {names}"

    @classmethod
    def get_or_create_between(cls, user_a, user_b, subject=""):
        """Вернуть диалог между двумя пользователями, создав его при необходимости."""
        existing = (
            cls.objects.filter(participants=user_a)
            .filter(participants=user_b)
            .distinct()
            .first()
        )
        if existing:
            return existing, False
        conversation = cls.objects.create(subject=subject)
        conversation.participants.set([user_a, user_b])
        return conversation, True

    def has_participant(self, user):
        return user.is_authenticated and self.participants.filter(pk=user.pk).exists()

    def other_participant(self, user):
        return self.participants.exclude(pk=user.pk).first()

    def last_message(self):
        return self.messages.order_by("-created_at").first()

    def unread_count(self, user):
        return self.messages.filter(recipient=user, is_read=False).count()


class Message(models.Model):
    """Личное сообщение внутри диалога."""

    conversation = models.ForeignKey(
        Conversation,
        verbose_name="Диалог",
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Отправитель",
        on_delete=models.CASCADE,
        related_name="messages_sent",
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Получатель",
        on_delete=models.CASCADE,
        related_name="messages_received",
    )
    content = models.TextField("Текст сообщения")
    is_read = models.BooleanField("Прочитано", default=False)
    created_at = models.DateTimeField("Дата", auto_now_add=True)

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["created_at"]
        indexes = [models.Index(fields=["conversation", "created_at"])]

    def __str__(self):
        return f"{self.sender} → {self.recipient}: {self.content[:40]}"
