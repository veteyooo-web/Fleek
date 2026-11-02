from django.apps import AppConfig


class ChatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.messages"
    # Метка chat вместо messages, чтобы не конфликтовать с django.contrib.messages.
    label = "chat"
    verbose_name = "Личные сообщения"
