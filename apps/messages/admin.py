"""Административная панель приложения личных сообщений."""
from django.contrib import admin

from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    fields = ("sender", "recipient", "content", "is_read", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "participants_list", "subject", "messages_count", "updated_at")
    search_fields = ("subject", "participants__username")
    filter_horizontal = ("participants",)
    inlines = [MessageInline]

    @admin.display(description="Участники")
    def participants_list(self, obj):
        return ", ".join(str(p) for p in obj.participants.all())

    @admin.display(description="Сообщений")
    def messages_count(self, obj):
        return obj.messages.count()


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "recipient", "short_content", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("content", "sender__username", "recipient__username")
    autocomplete_fields = ("sender", "recipient")
    raw_id_fields = ("conversation",)
    date_hierarchy = "created_at"

    @admin.display(description="Текст")
    def short_content(self, obj):
        return obj.content[:60]
