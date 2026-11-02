"""URL-адреса приложения projects."""
from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("", views.project_list, name="list"),
    path("<int:pk>/", views.project_detail, name="detail"),
    path("<int:pk>/complete/", views.project_complete, name="complete"),
    path("<int:pk>/cancel/", views.project_cancel, name="cancel"),
]
