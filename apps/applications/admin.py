"""Административная панель приложения applications."""
from django.contrib import admin

from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("order", "freelancer", "price", "days", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order__title", "cover_letter", "freelancer__username")
    autocomplete_fields = ("freelancer",)
    raw_id_fields = ("order",)
    readonly_fields = ("created_at", "answered_at")
