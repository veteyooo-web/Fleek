"""URL-адреса приложения orders."""
from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("", views.order_list, name="list"),
    path("my/", views.order_my, name="my"),
    path("favorites/", views.favorites, name="favorites"),
    path("categories/", views.category_list, name="categories"),
    path("create/", views.order_create, name="create"),
    path("<int:pk>/", views.order_detail, name="detail"),
    path("<int:pk>/edit/", views.order_update, name="update"),
    path("<int:pk>/delete/", views.order_delete, name="delete"),
    path("<int:pk>/favorite/", views.order_toggle_favorite, name="toggle_favorite"),
]
