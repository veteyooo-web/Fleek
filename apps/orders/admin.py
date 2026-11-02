"""Административная панель приложения orders."""
from django.contrib import admin

from .models import Category, Order


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "orders_count")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}

    @admin.display(description="Заказов")
    def orders_count(self, obj):
        return obj.orders.count()


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "owner",
        "category",
        "status",
        "budget_max",
        "deadline",
        "created_at",
    )
    list_filter = ("status", "category")
    search_fields = ("title", "description", "skills")
    autocomplete_fields = ("owner",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("favorites",)
    fieldsets = (
        ("Основное", {"fields": ("title", "description", "category", "status")}),
        ("Условия", {"fields": ("budget_min", "budget_max", "deadline", "skills")}),
        ("Автор", {"fields": ("owner", "favorites")}),
        ("Служебное", {"fields": ("created_at", "updated_at")}),
    )
