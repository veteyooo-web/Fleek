"""URL-адреса приложения reviews."""
from django.urls import path

from . import views

app_name = "reviews"

urlpatterns = [
    path("", views.latest, name="latest"),
    path("project/<int:project_pk>/add/", views.review_create, name="create"),
    path("<int:pk>/delete/", views.review_delete, name="delete"),
]
