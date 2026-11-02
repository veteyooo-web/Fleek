"""Модели приложения откликов на заказы."""
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Application(models.Model):
    """Отклик фрилансера на заказ: цена, срок, сообщение заказчику."""

    class Status(models.TextChoices):
        PENDING = "pending", "На рассмотрении"
        ACCEPTED = "accepted", "Принят"
        REJECTED = "rejected", "Отклонён"
        WITHDRAWN = "withdrawn", "Отозван"

    order = models.ForeignKey(
        "orders.Order",
        verbose_name="Заказ",
        on_delete=models.CASCADE,
        related_name="applications",
    )
    freelancer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Фрилансер",
        on_delete=models.CASCADE,
        related_name="applications",
    )
    price = models.DecimalField(
        "Предлагаемая цена",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(1)],
    )
    days = models.PositiveIntegerField("Срок выполнения (дней)", validators=[MinValueValidator(1)])
    cover_letter = models.TextField("Сообщение заказчику")
    status = models.CharField(
        "Статус", max_length=20, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField("Дата отклика", auto_now_add=True)
    answered_at = models.DateTimeField("Дата решения", null=True, blank=True)

    class Meta:
        verbose_name = "Отклик"
        verbose_name_plural = "Отклики"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=("order", "freelancer"),
                name="unique_order_freelancer_application",
            )
        ]
        indexes = [models.Index(fields=["freelancer", "status"])]

    def __str__(self):
        return f"{self.freelancer} → {self.order}"

    @property
    def price_display(self):
        return f"{self.price:,.0f} ₽"

    @property
    def can_be_withdrawn(self):
        return self.status == self.Status.PENDING

    @property
    def is_pending(self):
        return self.status == self.Status.PENDING
