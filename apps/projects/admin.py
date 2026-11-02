"""Административная панель приложения projects."""
from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "customer", "freelancer", "price", "status", "deadline", "started_at")
    list_filter = ("status", "deadline")
    search_fields = ("title", "description", "summary", "order__title")
    autocomplete_fields = ("customer", "freelancer")
    raw_id_fields = ("order",)
    readonly_fields = ("started_at", "completed_at")
    date_hierarchy = "started_at"
