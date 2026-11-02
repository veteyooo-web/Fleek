"""Модели приложения проектов (заказы, принятые исполнителем в работу)."""
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Project(models.Model):
    """Проект создаётся автоматически при принятии отклика."""

    class Status(models.TextChoices):
        ACTIVE = "active", "В работе"
        COMPLETED = "completed", "Завершён"
        CANCELLED = "cancelled", "Отменён"

    order = models.OneToOneField(
        "orders.Order",
        verbose_name="Заказ",
        on_delete=models.CASCADE,
        related_name="project",
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Заказчик",
        on_delete=models.CASCADE,
        related_name="customer_projects",
    )
    freelancer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Исполнитель",
        on_delete=models.CASCADE,
        related_name="freelancer_projects",
    )
    title = models.CharField("Название", max_length=150)
    description = models.TextField("Описание", blank=True)
    price = models.DecimalField("Цена", max_digits=12, decimal_places=2)
    deadline = models.DateField("Срок сдачи", null=True, blank=True)
    status = models.CharField(
        "Статус", max_length=20, choices=Status.choices, default=Status.ACTIVE
    )
    summary = models.TextField("Итог работы", blank=True, help_text="Что сделано по проекту")
    started_at = models.DateTimeField("Начат", auto_now_add=True)
    completed_at = models.DateTimeField("Завершён", null=True, blank=True)

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ["-started_at"]
        indexes = [models.Index(fields=["status", "-started_at"])]

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE

    @property
    def days_left(self):
        """Осталось дней до срока сдачи (отрицательное — просрочено)."""
        if not self.deadline or not self.is_active:
            return None
        return (self.deadline - timezone.localdate()).days

    @property
    def is_overdue(self):
        days = self.days_left
        return days is not None and days < 0

    def is_participant(self, user):
        return user.is_authenticated and (
            user.pk == self.customer_id or user.pk == self.freelancer_id
        )

    def can_be_reviewed_by(self, user):
        """Отзыв оставить можно только по завершённому проекту и только участнику."""
        return (
            self.is_participant(user)
            and self.status == self.Status.COMPLETED
            and not self.reviews.filter(author=user).exists()
        )

    def get_absolute_url(self):
        return reverse("projects:detail", kwargs={"pk": self.pk})
