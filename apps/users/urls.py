"""URL-адреса приложения users."""
from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/password/", views.password_change, name="password_change"),
    path("notifications/", views.notifications, name="notifications"),
    path(
        "notifications/mark-all-read/",
        views.notifications_mark_all_read,
        name="notifications_mark_all_read",
    ),
    path(
        "notifications/<int:pk>/read/",
        views.notification_mark_read,
        name="notification_mark_read",
    ),
    path("portfolio/add/", views.portfolio_create, name="portfolio_create"),
    path("portfolio/<int:pk>/edit/", views.portfolio_update, name="portfolio_update"),
    path("portfolio/<int:pk>/delete/", views.portfolio_delete, name="portfolio_delete"),
    path("profile/<int:pk>/", views.profile, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
]
