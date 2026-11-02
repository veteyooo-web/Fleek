"""Модели приложения отзывов."""
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    """Отзыв об участнике завершённого проекта."""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="reviews_written",
    )
    target = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="О ком",
        on_delete=models.CASCADE,
        related_name="reviews_received",
    )
    project = models.ForeignKey(
        "projects.Project",
        verbose_name="Проект",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField(
        "Оценка", validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField("Отзыв", max_length=2000)
    created_at = models.DateTimeField("Дата", auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=("project", "author"), name="unique_review_per_project_author"
            )
        ]

    def __str__(self):
        return f"{self.rating}★ от {self.author} о {self.target}"
