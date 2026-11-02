from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.reviews"
    verbose_name = "Отзывы"

    def ready(self):
        # Подписка сигналов (уведомление о новом отзыве).
        from . import signals  # noqa: F401
