"""Маршруты корневого URL-адреса проекта Taskly."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from apps.users.forms import LoginForm

admin.site.site_header = "Администрирование Taskly"
admin.site.site_title = "Taskly admin"
admin.site.index_title = "Управление данными"

urlpatterns = [
    path("admin/", admin.site.urls),
    # Авторизация: вход и выход (смена пароля — в кабинете пользователя)
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html", authentication_form=LoginForm
        ),
        name="login",
    ),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    # Пользователи: регистрация, личный кабинет, профили, уведомления
    path("", include(("apps.users.urls", "users"), namespace="users")),
    path("orders/", include(("apps.orders.urls", "orders"), namespace="orders")),
    path(
        "applications/",
        include(("apps.applications.urls", "applications"), namespace="applications"),
    ),
    path("projects/", include(("apps.projects.urls", "projects"), namespace="projects")),
    path("reviews/", include(("apps.reviews.urls", "reviews"), namespace="reviews")),
    path("messages/", include(("apps.messages.urls", "messages"), namespace="messages")),
]

if settings.DEBUG:
    # В режиме разработки медиафайлы отдаёт Django; статикой занимается runserver.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
