"""URL-адреса приложения applications."""
from django.urls import path

from . import views

app_name = "applications"

urlpatterns = [
    path("", views.my_applications, name="my"),
    path("order/<int:order_pk>/", views.order_applications, name="for_order"),
    path("order/<int:order_pk>/send/", views.application_create, name="create"),
    path("<int:pk>/accept/", views.application_accept, name="accept"),
    path("<int:pk>/reject/", views.application_reject, name="reject"),
    path("<int:pk>/withdraw/", views.application_withdraw, name="withdraw"),
]
