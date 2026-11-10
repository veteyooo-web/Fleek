"""Временный смоук-тест: проверяет, что все страницы отдаются без ошибок."""
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test.utils import setup_test_environment  # noqa: E402

setup_test_environment()

from django.test import Client  # noqa: E402

from apps.applications.models import Application  # noqa: E402
from apps.messages.models import Conversation  # noqa: E402
from apps.orders.models import Order  # noqa: E402
from apps.projects.models import Project  # noqa: E402
from apps.reviews.models import Review  # noqa: E402
from apps.users.models import Notification, PortfolioItem, User  # noqa: E402

open_order = Order.objects.filter(status=Order.Status.OPEN).first()
my_order = Order.objects.filter(owner__username="boss_anna").exclude(status=Order.Status.DRAFT).first()
project = Project.objects.first()
review = Review.objects.first()
conversation = Conversation.objects.first()
portfolio = PortfolioItem.objects.first()
notification = Notification.objects.first()
freelancer = User.objects.get(username="devmax")
customer = User.objects.get(username="boss_anna")
pending_app = Application.objects.filter(status=Application.Status.PENDING).first()

GUEST = [
    "/", "/orders/", "/orders/?q=лендинг&sort=-budget_max", "/orders/?min_budget=30000&max_budget=90000&status=open",
    f"/orders/{open_order.pk}/", "/orders/categories/", "/applications/", "/projects/", "/reviews/",
    "/messages/", "/accounts/login/", "/register/", "/profile/%d/" % freelancer.pk, "/no-such-page/",
]

CUSTOMER = [
    "/dashboard/", "/profile/edit/", "/accounts/password/change/", "/notifications/", "/notifications/?unread=1",
    "/orders/create/", "/orders/my/", "/orders/my/?status=open", "/orders/favorites/",
    f"/orders/{my_order.pk}/", f"/orders/{my_order.pk}/edit/", f"/applications/order/{my_order.pk}/",
    "/projects/", "/projects/?status=active", "/messages/", "/reviews/",
    f"/reviews/project/{project.pk}/add/", "/portfolio/add/",
]

FREELANCER = [
    "/dashboard/", "/applications/", "/applications/?status=pending", "/projects/", "/projects/?status=completed",
    f"/projects/{project.pk}/", f"/orders/{open_order.pk}/", f"/messages/chat/{conversation.pk}/",
    f"/messages/start/{customer.pk}/", f"/profile/{customer.pk}/",
    f"/portfolio/{portfolio.pk}/edit/", f"/reviews/{review.pk}/delete/",
    "/notifications/", "/profile/edit/",
]

failures = []


def check(client, urls, label):
    for url in urls:
        try:
            response = client.get(url, follow=True)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{label} {url}: ИСКЛЮЧЕНИЕ {type(exc).__name__}: {exc}")
            continue
        if response.status_code >= 500:
            failures.append(f"{label} {url}: HTTP {response.status_code}")
        print(f"  {label:9} {url:45} -> {response.status_code}")


print("=== ГОСТЬ ===")
check(Client(), GUEST, "guest")

print("=== ЗАКАЗЧИК ===")
c = Client()
assert c.login(username="boss_anna", password="Taskly2026"), "не удалось войти заказчику"
check(c, CUSTOMER, "customer")

print("=== ФРИЛАНСЕР ===")
f = Client()
assert f.login(username="devmax", password="Taskly2026"), "не удалось войти фрилансеру"
check(f, FREELANCER, "freelancer")

print("=== АДМИН ===")
a = Client()
assert a.login(username="admin", password="Taskly2026"), "не удалось войти админу"
for url in ["/admin/", "/admin/orders/order/", "/admin/users/user/", "/admin/chat/message/",
            "/admin/applications/application/", "/admin/projects/project/", "/admin/reviews/review/"]:
    response = a.get(url)
    print(f"  {'admin':9} {url:45} -> {response.status_code}")
    if response.status_code >= 500:
        failures.append(f"admin {url}: HTTP {response.status_code}")

print("=== POST: отклик, избранное, принятие, завершение ===")
app_order = Order.objects.filter(status=Order.Status.OPEN).exclude(owner=freelancer).first()
r = f.post(f"/applications/order/{app_order.pk}/send/", {"price": "45000", "days": "12", "cover_letter": "Тестовый отклик из смоук-теста"})
print("  отклик ->", r.status_code, r.headers.get("Location"))
if r.status_code not in (301, 302):
    failures.append("POST отклик вернул %s" % r.status_code)

r = f.post(f"/orders/{open_order.pk}/favorite/")
print("  избранное ->", r.status_code)
r = a.post(f"/notifications/{notification.pk}/read/", {}) if False else None

# Принятие отклика заказчиком (создание проекта)
target = Application.objects.filter(status=Application.Status.PENDING, order__owner=customer).first()
if target:
    r = c.post(f"/applications/{target.pk}/accept/")
    print("  принять отклик ->", r.status_code, r.headers.get("Location"))
    if r.status_code >= 500:
        failures.append("accept вернул %s" % r.status_code)

# Завершение проекта
active = Project.objects.filter(status=Project.Status.ACTIVE).first()
if active:
    r = c.post(f"/projects/{active.pk}/complete/", {"summary": "Работа сдана, исходники переданы."})
    print("  завершить проект ->", r.status_code, r.headers.get("Location"))
    fresh = Project.objects.get(pk=active.pk)
    print("  статус проекта после:", fresh.status)
    if fresh.status != Project.Status.COMPLETED:
        failures.append("проект не завершился: %s" % fresh.status)
    # Отзыв по завершённому проекту
    r = c.post(f"/reviews/project/{fresh.pk}/add/", {"rating": "5", "comment": "Отличная работа, всё вовремя!"})
    print("  оставить отзыв ->", r.status_code, r.headers.get("Location"))
    if not Review.objects.filter(project=fresh, author=customer).exists():
        failures.append("отзыв не создан")

# Сообщение в диалог
if conversation:
    r = c.post(f"/messages/chat/{conversation.pk}/", {"content": "Тестовое сообщение из смоук-теста"})
    print("  отправить сообщение ->", r.status_code)

print("=== ИТОГ ===")
if failures:
    print("ПРОБЛЕМЫ:")
    for item in failures:
        print(" -", item)
    raise SystemExit(1)
print("Все страницы и POST-сценарии отработали без ошибок.")
