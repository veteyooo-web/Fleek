"""Контекст-процессор: категории для меню навигации."""
from django.db.models import Count, Q

from .models import Category, Order


def menu_categories(request):
    categories = (
        Category.objects.annotate(
            open_count=Count("orders", filter=Q(orders__status=Order.Status.OPEN))
        )
        .order_by("-open_count", "name")[:8]
    )
    return {"menu_categories": categories}
