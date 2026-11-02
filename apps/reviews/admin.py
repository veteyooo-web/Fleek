"""Административная панель приложения reviews."""
from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("rating", "author", "target", "project", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("comment", "author__username", "target__username", "project__title")
    autocomplete_fields = ("author", "target")
    raw_id_fields = ("project",)
    readonly_fields = ("created_at",)
