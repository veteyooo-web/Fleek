"""Команда заполнения базы демонстрационными данными: python manage.py seed_demo"""
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.applications.models import Application
from apps.messages.models import Conversation, Message
from apps.orders.models import Category, Order
from apps.projects.models import Project
from apps.reviews.models import Review
from apps.users.models import Notification, PortfolioItem, User

DEFAULT_PASSWORD = "Taskly2026"

CATEGORIES = [
    ("Веб-разработка", "Сайты, веб-приложения, интернет-магазины на Django и не только."),
    ("Дизайн и графика", "Логотипы, фирменный стиль, интерфейсы, иллюстрации."),
    ("Мобильные приложения", "Разработка приложений для Android и iOS."),
    ("Тексты и переводы", "Копирайтинг, редактура, переводы, SEO-тексты."),
    ("Маркетинг и реклама", "Настройка рекламы, SMM, аналитика."),
    ("Данные и аналитика", "Сбор и обработка данных, отчёты, машинное обучение."),
    ("Техническая поддержка", "Настройка серверов, администрирование, консультации."),
    ("Обучение и курсы", "Онлайн-уроки, менторство, подготовка материалов."),
]

CUSTOMERS = [
    ("boss_anna", "Анна", "Соколова", "anna@example.com", "Москва", "Запускаю сеть кофеен, ищу подрядчиков под digital-задачи."),
    ("proctor", "Игорь", "Петров", "igor@example.com", "Санкт-Петербург", "Руковожу небольшой студией, часто нужны внешние исполнители."),
    ("greenmarket", "Мария", "Ковалёва", "maria@example.com", "Казань", "Интернет-магазин фермерских продуктов."),
]

FREELANCERS = [
    ("devmax", "Максим", "Кузнецов", "max@example.com", "Новосибирск", "Python, Django, PostgreSQL, Celery, Docker", "Делаю backend на Django 6 лет, люблю чистые миграции и тесты."),
    ("nastya_design", "Анастасия", "Белова", "nastya@example.com", "Екатеринбург", "Figma, UI/UX, Illustrator, бренд", "Проектирую интерфейсы и фирменные стили для небольших продуктов."),
    ("mobileoleg", "Олег", "Тимин", "oleg@example.com", "Краснодар", "Kotlin, Android, Firebase", "Android-приложения под ключ: от макета до публикации в Google Play."),
    ("copycat", "Дарья", "Ильина", "darya@example.com", "Нижний Новгород", "Копирайтинг, SEO, редактура", "Пишу продающие тексты и статьи, которые читают до конца."),
    ("datavince", "Виктор", "Литвин", "viktor@example.com", "Самара", "Python, pandas, ML, SQL", "Аналитика данных, дашборды и модели прогноза."),
]

ORDERS = [
    # (заголовок, категория, заказчик, бюджет от, бюджет до, дней на сдачу, навыки, статус)
    ("Лендинг для сети кофеен", "Веб-разработка", "boss_anna", 40000, 70000, 21, "Django, HTML, CSS", Order.Status.OPEN),
    ("Доработка интернет-магазина на Django", "Веб-разработка", "greenmarket", 60000, 120000, 30, "Django, PostgreSQL, Celery", Order.Status.OPEN),
    ("Логотип и фирменный стиль для кофейни", "Дизайн и графика", "boss_anna", 15000, 30000, 14, "Illustrator, бренд, Figma", Order.Status.OPEN),
    ("UI-кит для мобильного приложения", "Дизайн и графика", "proctor", 25000, 45000, 18, "Figma, UI/UX", Order.Status.OPEN),
    ("Приложение для трекинга тренировок (Android)", "Мобильные приложения", "proctor", 90000, 150000, 45, "Kotlin, Android, Firebase", Order.Status.OPEN),
    ("Серия SEO-статей для магазина продуктов", "Тексты и переводы", "greenmarket", 20000, 35000, 20, "Копирайтинг, SEO", Order.Status.OPEN),
    ("Перевод описаний товаров (EN -> RU)", "Тексты и переводы", "greenmarket", 10000, 18000, 10, "Перевод, редактура", Order.Status.OPEN),
    ("Дашборд продаж в Excel и Python", "Данные и аналитика", "proctor", 30000, 55000, 25, "Python, pandas, SQL", Order.Status.OPEN),
    ("Настройка VPS и резервных копий", "Техническая поддержка", "boss_anna", 12000, 20000, 7, "Linux, Nginx, Docker", Order.Status.OPEN),
    ("Курс по Django для начинающих", "Обучение и курсы", "proctor", 50000, 90000, 40, "Python, Django, методология", Order.Status.IN_PROGRESS),
    ("Интеграция платёжного шлюза", "Веб-разработка", "greenmarket", 35000, 60000, 15, "Django, API, платежи", Order.Status.COMPLETED),
    ("Редизайн карточек товара", "Дизайн и графика", "greenmarket", 18000, 28000, 12, "Figma, UI", Order.Status.COMPLETED),
    ("Черновик: мобильное приложение для склада", "Мобильные приложения", "proctor", 120000, 200000, 60, "Kotlin, SQLite", Order.Status.DRAFT),
]

APPLICATIONS = [
    # (заголовок заказа, фрилансер, цена, дней, текст, статус)
    ("Лендинг для сети кофеен", "nastya_design", 55000, 18, "Соберу лендинг на чистом HTML/CSS с админкой, покажу 2 концепции hero-блока.", Application.Status.PENDING),
    ("Лендинг для сети кофеен", "devmax", 62000, 21, "Сделаю Django-шаблон + CMS для редактирования текстов и фото, деплой на ваш сервер.", Application.Status.PENDING),
    ("Доработка интернет-магазина на Django", "devmax", 110000, 28, "Опыт с Django-магазинами: фильтры, корзина, оплата, ускорение запросов.", Application.Status.PENDING),
    ("Доработка интернет-магазина на Django", "datavince", 95000, 30, "Могу взять аналитическую часть: рекомендации товаров и отчёты.", Application.Status.PENDING),
    ("Логотип и фирменный стиль для кофейни", "nastya_design", 27000, 12, "3 варианта логотипа, гайд по цвету и шрифтам, макеты упаковки.", Application.Status.PENDING),
    ("UI-кит для мобильного приложения", "nastya_design", 38000, 16, "Соберу дизайн-систему в Figma с компонентами и тёмной темой.", Application.Status.PENDING),
    ("Приложение для трекинга тренировок (Android)", "mobileoleg", 135000, 42, "Kotlin + Room, экспорт статистики, офлайн-режим, публикация в Play Market.", Application.Status.PENDING),
    ("Серия SEO-статей для магазина продуктов", "copycat", 30000, 18, "10 статей по 8000 знаков с кластерами и внутренней перелинковкой.", Application.Status.PENDING),
    ("Перевод описаний товаров (EN -> RU)", "copycat", 15000, 8, "Перевод с адапацией под русскоязычного покупателя, редакторская правка.", Application.Status.PENDING),
    ("Дашборд продаж в Excel и Python", "datavince", 45000, 20, "Python + pandas, интерактивный дашборд, инструкция для менеджеров.", Application.Status.PENDING),
    ("Настройка VPS и резервных копий", "devmax", 16000, 5, "Ubuntu, Nginx, Let's Encrypt, cron-бэкапы с проверкой восстановления.", Application.Status.PENDING),
    ("Курс по Django для начинающих", "devmax", 85000, 38, "12 уроков с домашними заданиями и проверкой кода, формат — видео + конспекты.", Application.Status.ACCEPTED),
    ("Интеграция платёжного шлюза", "devmax", 52000, 14, "Интеграция эквайринга, тестовые платежи, обработка возвратов.", Application.Status.ACCEPTED),
    ("Редизайн карточек товара", "nastya_design", 24000, 10, "Новые карточки в Figma + адаптив, 3 варианта сетки каталога.", Application.Status.ACCEPTED),
    ("Серия SEO-статей для магазина продуктов", "copycat", 26000, 15, "Альтернативный вариант: 8 статей и блог-раздел.", Application.Status.REJECTED),
]

PORTFOLIO = [
    ("devmax", "Кабинет страхового агента", "Django-приложение для 200 пользователей с ролями и отчётами.", "https://example.com/insurance"),
    ("devmax", "Интеграция 1С и сайта", "Обмен остатками и ценами через REST API.", "https://example.com/1c"),
    ("nastya_design", "Приложение для записи к барберу", "UX-исследование, прототип и UI-кит.", "https://example.com/barber"),
    ("nastya_design", "Айдентика кофейни", "Логотип, упаковка, навигация в зале.", ""),
    ("mobileoleg", "Трекер воды на Kotlin", "Офлайн-приложение с виджетами и уведомлениями.", "https://example.com/water"),
    ("copycat", "Тексты для сервиса доставки", "24 статьи и лендинг, рост органики на 40%.", ""),
    ("datavince", "Прогноз спроса для склада", "Модель на pandas + LightGBM, отчёт в дашборде.", "https://example.com/forecast"),
]

REVIEWS = [
    # (автор, оценённый, заказ, оценка, текст)
    ("boss_anna", "devmax", "Интеграция платёжного шлюза", 5, "Максим сделал всё раньше срока и подробно задокументировал интеграцию. Рекомендую."),
    ("devmax", "boss_anna", "Интеграция платёжного шлюза", 5, "Чёткое ТЗ и быстрые согласования — работать было комфортно."),
    ("greenmarket", "nastya_design", "Редизайн карточек товара", 4, "Дизайн понравился, пришлось пару раз уточнить адаптив, но итог хороший."),
    ("nastya_design", "greenmarket", "Редизайн карточек товара", 5, "Заказчик присылал материалы вовремя, обратная связь по делу."),
]

MESSAGES = [
    ("Курс по Django для начинающих", "proctor", "devmax", [
        "Максим, добрый день! Уточните, пожалуйста, сколько часов занимает курс?",
        "Игорь, здравствуйте! Примерно 40 часов видео плюс практика. Могу прислать программу по урокам.",
        "Отлично, присылайте. Если устроит стоимость — стартуем на этой неделе.",
    ]),
    ("Интеграция платёжного шлюза", "greenmarket", "devmax", [
        "По оплате всё приняли, спасибо! Возвраты тоже проверили на тестовой карте.",
        "Супер, тогда проект можно закрывать.",
    ]),
]


class Command(BaseCommand):
    help = "Создать демонстрационные данные: пользователи, заказы, отклики, проекты, отзывы, сообщения."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            default=DEFAULT_PASSWORD,
            help="Пароль для всех демо-аккаунтов (по умолчанию: %(default)s)",
        )
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Удалить ранее созданные демо-данные перед заполнением",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["flush"]:
            self._flush()

        categories = self._create_categories()
        users = self._create_users(options["password"])
        orders = self._create_orders(categories, users)
        applications = self._create_applications(orders, users)
        projects = self._create_projects(applications, orders, users)
        self._create_portfolio(users)
        self._create_reviews(projects, users)
        self._create_messages(orders, users)
        self._create_favorites(orders, users)
        self._create_notifications(orders, applications, users)

        self.stdout.write(self.style.SUCCESS("Демо-данные созданы."))
        self.stdout.write(f"Админ: admin / {options['password']}  (http://localhost:8000/admin/)")
        self.stdout.write(f"Заказчик: boss_anna / {options['password']}")
        self.stdout.write(f"Фрилансер: devmax / {options['password']}")
        self.stdout.write(
            "Записей: пользователей %s, заказов %s, откликов %s, проектов %s, отзывов %s"
            % (
                User.objects.count(),
                Order.objects.count(),
                Application.objects.count(),
                Project.objects.count(),
                Review.objects.count(),
            )
        )

    # ------------------------------------------------------------------ #
    def _flush(self):
        demo_names = [name for name, *_ in CUSTOMERS] + [name for name, *_ in FREELANCERS]
        Review.objects.all().delete()
        Message.objects.all().delete()
        Conversation.objects.all().delete()
        Project.objects.all().delete()
        Application.objects.all().delete()
        Order.objects.all().delete()
        Category.objects.all().delete()
        PortfolioItem.objects.all().delete()
        Notification.objects.all().delete()
        User.objects.filter(username__in=demo_names).delete()
        self.stdout.write("Старые демо-данные удалены.")

    def _create_categories(self):
        result = {}
        for name, description in CATEGORIES:
            category, _ = Category.objects.get_or_create(
                name=name, defaults={"description": description}
            )
            result[name] = category
        self.stdout.write(f"Категории: {len(result)}")
        return result

    def _create_users(self, password):
        users = {}

        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "first_name": "Администратор",
                "last_name": "Taskly",
                "email": "admin@example.com",
                "role": User.Role.CUSTOMER,
                "is_staff": True,
                "is_superuser": True,
                "city": "Москва",
                "bio": "Служебный аккаунт для проверки админ-панели.",
            },
        )
        if created:
            admin.set_password(password)
            admin.save()
        users["admin"] = admin

        for username, first_name, last_name, email, city, bio in CUSTOMERS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "role": User.Role.CUSTOMER,
                    "city": city,
                    "bio": bio,
                },
            )
            if created:
                user.set_password(password)
                user.save()
            users[username] = user

        for username, first_name, last_name, email, city, skills, bio in FREELANCERS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "role": User.Role.FREELANCER,
                    "city": city,
                    "skills": skills,
                    "bio": bio,
                    "telegram": username,
                },
            )
            if created:
                user.set_password(password)
                user.save()
            users[username] = user

        self.stdout.write(f"Пользователи: {len(users)}")
        return users

    def _create_orders(self, categories, users):
        today = timezone.localdate()
        orders = {}
        for (
            title,
            category_name,
            owner_name,
            budget_min,
            budget_max,
            deadline_days,
            skills,
            status,
        ) in ORDERS:
            order, _ = Order.objects.get_or_create(
                title=title,
                owner=users[owner_name],
                defaults={
                    "category": categories[category_name],
                    "description": (
                        f"{title}.\n\n"
                        "Что нужно сделать:\n"
                        "1. Обсудить детали и зафиксировать требования.\n"
                        "2. Выполнить работу и показать промежуточный результат.\n"
                        "3. Внести правки и передать исходники.\n\n"
                        "Ожидаем от исполнителя опыт по похожим задачам и пример работ."
                    ),
                    "budget_min": Decimal(budget_min),
                    "budget_max": Decimal(budget_max),
                    "deadline": today + timedelta(days=deadline_days),
                    "skills": skills,
                    "status": status,
                },
            )
            orders[title] = order
        self.stdout.write(f"Заказы: {len(orders)}")
        return orders

    def _create_applications(self, orders, users):
        applications = {}
        for order_title, freelancer_name, price, days, text, status in APPLICATIONS:
            order = orders[order_title]
            application, created = Application.objects.get_or_create(
                order=order,
                freelancer=users[freelancer_name],
                defaults={
                    "price": Decimal(price),
                    "days": days,
                    "cover_letter": text,
                    "status": status,
                },
            )
            if not created and application.status != status:
                application.status = status
                application.save(update_fields=["status"])
            applications[order_title, freelancer_name] = application
        self.stdout.write(f"Отклики: {len(applications)}")
        return applications

    def _create_projects(self, applications, orders, users):
        projects = {}
        for (order_title, freelancer_name), application in applications.items():
            if application.status != Application.Status.ACCEPTED:
                continue
            order = application.order
            completed = order.status == Order.Status.COMPLETED
            project, _ = Project.objects.get_or_create(
                order=order,
                defaults={
                    "customer": order.owner,
                    "freelancer": application.freelancer,
                    "title": order.title,
                    "description": order.description,
                    "price": application.price,
                    "deadline": order.deadline,
                    "status": Project.Status.COMPLETED if completed else Project.Status.ACTIVE,
                    "summary": "Все договорённости выполнены, исходники переданы."
                    if completed
                    else "",
                    "completed_at": timezone.now() - timedelta(days=5) if completed else None,
                },
            )
            projects[order_title] = project
        self.stdout.write(f"Проекты: {len(projects)}")
        return projects

    def _create_portfolio(self, users):
        count = 0
        for username, title, description, link in PORTFOLIO:
            _, created = PortfolioItem.objects.get_or_create(
                owner=users[username],
                title=title,
                defaults={"description": description, "link": link},
            )
            count += int(created)
        self.stdout.write(f"Работ в портфолио добавлено: {count}")

    def _create_reviews(self, projects, users):
        count = 0
        for author_name, target_name, order_title, rating, comment in REVIEWS:
            project = projects.get(order_title)
            if project is None:
                continue
            _, created = Review.objects.get_or_create(
                project=project,
                author=users[author_name],
                defaults={
                    "target": users[target_name],
                    "rating": rating,
                    "comment": comment,
                },
            )
            count += int(created)
        self.stdout.write(f"Отзывов добавлено: {count}")

    def _create_messages(self, orders, users):
        count = 0
        for order_title, first_name, second_name, texts in MESSAGES:
            conversation, _ = Conversation.get_or_create_between(
                users[first_name], users[second_name], subject=order_title
            )
            for index, text in enumerate(texts):
                sender = users[first_name] if index % 2 == 0 else users[second_name]
                recipient = users[second_name] if sender is users[first_name] else users[first_name]
                _, created = Message.objects.get_or_create(
                    conversation=conversation,
                    content=text,
                    defaults={"sender": sender, "recipient": recipient},
                )
                count += int(created)
        self.stdout.write(f"Сообщений добавлено: {count}")

    def _create_favorites(self, orders, users):
        for username in ("devmax", "mobileoleg"):
            user = users[username]
            titles = ("Лендинг для сети кофеен", "UI-кит для мобильного приложения")
            for title in titles:
                if title in orders:
                    orders[title].favorites.add(user)
        self.stdout.write("Избранные заказы проставлены.")

    def _create_notifications(self, orders, applications, users):
        created = 0
        for application in applications.values():
            if application.status != Application.Status.PENDING:
                continue
            _, is_new = Notification.objects.get_or_create(
                recipient=application.order.owner,
                actor=application.freelancer,
                type=Notification.Type.NEW_APPLICATION,
                title=f"Новый отклик к заказу «{application.order.title}»",
                defaults={
                    "body": (
                        f"{application.freelancer.display_name}: "
                        f"{application.price_display} за {application.days} дн."
                    ),
                    "link": f"/applications/order/{application.order.pk}/",
                },
            )
            created += int(is_new)
        self.stdout.write(f"Уведомлений создано: {created}")
