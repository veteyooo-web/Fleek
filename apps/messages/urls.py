"""URL-адреса приложения личных сообщений."""
from django.urls import path

from . import views

app_name = "messages"

urlpatterns = [
    path("", views.inbox, name="inbox"),
    path("chat/<int:pk>/", views.conversation_detail, name="detail"),
    path("start/<int:user_pk>/", views.conversation_start, name="start"),
]
