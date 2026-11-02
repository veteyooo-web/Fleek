"""Административная панель приложения users."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Notification, PortfolioItem, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "city",
        "rating",
        "is_active",
    )
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("username", "first_name", "last_name", "email")
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Профиль Taskly",
            {
                "fields": (
                    "role",
                    "avatar",
                    "bio",
                    "city",
                    "skills",
                    "telegram",
                    "created_at",
                )
            },
        ),
    )
    readonly_fields = ("created_at",)
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Профиль", {"fields": ("email", "role", "city", "skills")}),
    )


class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "created_at")
    list_filter = ("owner",)
    search_fields = ("title", "description", "owner__username")


class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "recipient", "type", "is_read", "created_at")
    list_filter = ("type", "is_read")
    search_fields = ("title", "body", "recipient__username")
    autocomplete_fields = ("recipient", "actor")


admin.site.register(PortfolioItem, PortfolioItemAdmin)
admin.site.register(Notification, NotificationAdmin)
