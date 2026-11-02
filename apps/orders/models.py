"""Модели приложения заказов: категории и фриланс-заказы."""
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    """Категория (специализация) заказов."""

    name = models.CharField("Название", max_length=120, unique=True)
    slug = models.SlugField("Слаг", max_length=140, unique=True, blank=True)
    description = models.TextField("Описание", blank=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name, allow_unicode=True)
            slug = base
            suffix = 2
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{suffix}"
                suffix += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"{reverse('orders:list')}?category={self.pk}"


class Order(models.Model):
    """Фриланс-заказ, размещаемый заказчиком."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        OPEN = "open", "Открыт"
        IN_PROGRESS = "in_progress", "В работе"
        COMPLETED = "completed", "Завершён"
        CANCELLED = "cancelled", "Отменён"

    title = models.CharField("Заголовок", max_length=150)
    description = models.TextField("Описание задачи")
    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Заказчик",
        on_delete=models.CASCADE,
        related_name="orders",
    )
    budget_min = models.DecimalField("Бюджет от", max_digits=12, decimal_places=2, default=0)
    budget_max = models.DecimalField("Бюджет до", max_digits=12, decimal_places=2, default=0)
    deadline = models.DateField("Срок сдачи", null=True, blank=True)
    skills = models.CharField(
        "Требуемые навыки",
        max_length=255,
        blank=True,
        help_text="Навыки через запятую: Python, Django, PostgreSQL",
    )
    status = models.CharField(
        "Статус", max_length=20, choices=Status.choices, default=Status.OPEN
    )
    favorites = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="Избранные",
        related_name="favorite_orders",
        blank=True,
    )
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Изменён", auto_now=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["category", "status"]),
        ]

    def __str__(self):
        return self.title

    @property
    def is_open(self):
        return self.status == self.Status.OPEN

    @property
    def budget_display(self):
        formatter = "{:,.0f}".format
        if self.budget_min and self.budget_max and self.budget_min != self.budget_max:
            return f"{formatter(self.budget_min)} – {formatter(self.budget_max)} ₽"
        amount = self.budget_max or self.budget_min
        return f"{formatter(amount)} ₽" if amount else "Договорная"

    @property
    def skill_list(self):
        return [skill.strip() for skill in self.skills.split(",") if skill.strip()]

    @property
    def applications_count(self):
        return self.applications.count()

    @property
    def pending_applications_count(self):
        # Локальный импорт, чтобы избежать циклической зависимости приложений.
        from apps.applications.models import Application

        return self.applications.filter(status=Application.Status.PENDING).count()

    def can_be_edited_by(self, user):
        return user.is_authenticated and (
            user.pk == self.owner_id or user.is_superuser
        )

    def get_absolute_url(self):
        return reverse("orders:detail", kwargs={"pk": self.pk})
