"""Модели приложения пользователей: аккаунт, портфолио, уведомления."""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    """Кастомный пользователь с ролью «заказчик» или «фрилансер»."""

    class Role(models.TextChoices):
        CUSTOMER = "customer", "Заказчик"
        FREELANCER = "freelancer", "Фрилансер"

    role = models.CharField(
        "Роль", max_length=20, choices=Role.choices, default=Role.FREELANCER
    )
    avatar = models.ImageField("Аватар", upload_to="avatars/", blank=True)
    bio = models.TextField("О себе", blank=True)
    city = models.CharField("Город", max_length=100, blank=True)
    skills = models.CharField(
        "Навыки",
        max_length=255,
        blank=True,
        help_text="Перечислите навыки через запятую: Python, Django, Figma",
    )
    telegram = models.CharField("Telegram", max_length=64, blank=True)
    created_at = models.DateTimeField("Дата регистрации", auto_now_add=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        full_name = self.get_full_name()
        return full_name or self.username

    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER

    @property
    def is_freelancer(self):
        return self.role == self.Role.FREELANCER

    @property
    def skill_list(self):
        return [skill.strip() for skill in self.skills.split(",") if skill.strip()]

    @property
    def rating(self):
        """Средний рейтинг по всем полученным отзывам (от 0 до 5)."""
        aggregate = self.reviews_received.aggregate(avg=models.Avg("rating"))
        value = aggregate["avg"]
        return round(value, 2) if value else 0

    @property
    def reviews_count(self):
        return self.reviews_received.count()

    def get_absolute_url(self):
        return reverse("users:profile", kwargs={"pk": self.pk})


class PortfolioItem(models.Model):
    """Работа в портфолио фрилансера."""

    owner = models.ForeignKey(
        User,
        verbose_name="Владелец",
        on_delete=models.CASCADE,
        related_name="portfolio_items",
    )
    title = models.CharField("Название", max_length=150)
    description = models.TextField("Описание", blank=True)
    image = models.ImageField("Изображение", upload_to="portfolio/", blank=True)
    link = models.URLField("Ссылка на работу", blank=True)
    order = models.ForeignKey(
        "orders.Order",
        verbose_name="Связанный заказ",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="portfolio_items",
    )
    created_at = models.DateTimeField("Дата", auto_now_add=True)

    class Meta:
        verbose_name = "Работа портфолио"
        verbose_name_plural = "Портфолио"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Notification(models.Model):
    """Уведомление в личном кабинете."""

    class Type(models.TextChoices):
        NEW_APPLICATION = "new_application", "Новый отклик"
        APPLICATION_ACCEPTED = "application_accepted", "Отклик принят"
        APPLICATION_REJECTED = "application_rejected", "Отклик отклонён"
        PROJECT_STARTED = "project_started", "Проект начат"
        PROJECT_COMPLETED = "project_completed", "Проект завершён"
        NEW_REVIEW = "new_review", "Новый отзыв"
        NEW_MESSAGE = "new_message", "Новое сообщение"
        SYSTEM = "system", "Системное"

    recipient = models.ForeignKey(
        User,
        verbose_name="Получатель",
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    actor = models.ForeignKey(
        User,
        verbose_name="От кого",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications_sent",
    )
    type = models.CharField(
        "Тип", max_length=32, choices=Type.choices, default=Type.SYSTEM
    )
    title = models.CharField("Заголовок", max_length=200)
    body = models.TextField("Текст", blank=True)
    link = models.CharField("Ссылка", max_length=255, blank=True)
    is_read = models.BooleanField("Прочитано", default=False)
    created_at = models.DateTimeField("Дата", auto_now_add=True)

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["recipient", "is_read"])]

    def __str__(self):
        return f"{self.title} → {self.recipient}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=["is_read"])


def notify(recipient, title, *, actor=None, type_=Notification.Type.SYSTEM, body="", link=""):
    """Создать уведомление; у самого себя уведомления не создаём."""
    if actor is not None and actor.pk == recipient.pk:
        return None
    return Notification.objects.create(
        recipient=recipient,
        actor=actor,
        type=type_,
        title=title,
        body=body,
        link=link,
    )
