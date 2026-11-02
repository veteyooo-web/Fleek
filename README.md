🚀 Taskly
Taskly — веб-приложение для поиска и размещения фриланс-заказов.

Платформа объединяет заказчиков и фрилансеров в одном месте. Заказчики могут создавать проекты и выбирать исполнителей, а фрилансеры — находить подходящие заказы и отправлять отклики.

🛠️ Tech Stack
    Frontend
    Backend
    Database & Tools
✨ Features
    👤 Пользователи
        регистрация и авторизация;
        роли заказчик / фрилансер;
        редактирование профиля;
        портфолио;
        рейтинг и отзывы.
    📋 Заказы
        создание заказа;
        редактирование и удаление;
        категории;
        бюджет и сроки;
        поиск и фильтрация;
        просмотр подробной информации.
    💼 Отклики
        отправка отклика;
        предложение цены;
        указание срока выполнения;
        сообщение заказчику;
        принятие и отклонение откликов.
    📊 Личный кабинет
        активные проекты;
        история заказов;
        отправленные отклики;
        статистика;
        уведомления.
    💬 Дополнительно
        личные сообщения;
        система отзывов;
        избранные заказы;
        административная панель.


🏗️ Architecture
┌──────────────────────────────┐
│           Browser            │
│     HTML / CSS / JS          │
└──────────────┬───────────────┘
               │
               │ HTTP / REST API
               ▼
┌──────────────────────────────┐
│          Django              │
│          Python              │
│                              │
│  Auth │ Orders │ Projects    │
│  Users │ Reviews │ Messages  │
└──────────────┬───────────────┘
               │
               │ ORM
               ▼
┌──────────────────────────────┐
│         PostgreSQL           │
│                              │
│ Users │ Orders │ Applications│
│ Reviews │ Messages │ Projects│
└──────────────────────────────┘
📁 Project Structure
taskly/
│
├── config/                    # Настройки Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── apps/
│   ├── users/                 # Пользователи и профили
│   ├── orders/                # Заказы
│   ├── applications/          # Отклики
│   ├── projects/              # Проекты
│   ├── reviews/               # Отзывы
│   └── messages/              # Личные сообщения
│
├── templates/                 # HTML-шаблоны
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── media/                     # Загруженные файлы
│
├── docs/
│   └── screenshots/           # Скриншоты проекта
│
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── README.md

🎯 Project Goal
Цель проекта — разработать веб-приложение для взаимодействия заказчиков и фрилансеров, позволяющее размещать заказы, находить исполнителей, управлять проектами и отслеживать результаты работы.

📚 Educational Project
Проект разрабатывается в рамках курсовой работы по специальности «Информационные системы и программирование».

👨‍💻 Author
Igor

GitHub: @veteyooo-web

📄 License
This project is intended for educational purposes.

🚀 Installation & Run
1. Локальный запуск (SQLite по умолчанию)
    python -m venv .venv
    .venv\Scripts\activate            # Windows
    source .venv/bin/activate         # Linux/macOS
    pip install -r requirements.txt
    copy .env.example .env            # Windows (Linux/macOS: cp .env.example .env)
    python manage.py makemigrations
    python manage.py migrate
    python manage.py seed_demo        # демо-данные (необязательно)
    python manage.py runserver
    Откроется по адресу http://127.0.0.1:8000/

2. Демо-доступы после seed_demo (пароль по умолчанию: Taskly2026)
    admin / Taskly2026 — админ-панель: http://127.0.0.1:8000/admin/
    boss_anna / Taskly2026 — заказчик
    devmax / Taskly2026 — фрилансер
    Пароль можно изменить: python manage.py seed_demo --password "ВашПароль"

3. PostgreSQL
    В .env установите DB_ENGINE=postgresql и заполните POSTGRES_* значения,
    затем повторите migrate/seed_demo.

4. Docker (PostgreSQL + web)
    docker compose up --build
    docker compose exec web python manage.py migrate
    docker compose exec web python manage.py seed_demo
    Приложение: http://localhost:8000

🗂️ Реализованная структура
    config/          settings.py (чтение .env), urls.py, wsgi.py, asgi.py
    apps/users/      кастомный User с ролями, портфолио, уведомления, кабинет, регистрация
    apps/orders/     Category, Order, поиск/фильтрация, избранные, CRUD
    apps/applications/  отклики (цена, срок, сообщение), принятие/отклонение/отзыв
    apps/projects/   проекты из принятых откликов, завершение/отмена, статистика
    apps/reviews/    отзывы, рейтинг пользователя, уведомления о новых отзывах
    apps/messages/   диалоги и личные сообщения (app_label chat)
    templates/       base + страницы разделов, partials (пагинация, формы, карточки)
    static/css, js   оформление и небольшие JS-улучшения
    media/           загружаемые файлы (аватары, портфолио)

🧭 Основные маршруты
    /                     главная витрина
    /orders/             список заказов с фильтрами, /orders/create/, /orders/my/, /orders/favorites/
    /applications/       мои отклики, отклики заказа, accept/reject/withdraw
    /projects/           проекты и их статусы
    /reviews/            последние отзывы, создание отзыва по проекту
    /messages/           диалоги и переписка
    /dashboard/          личный кабинет (заказчик / фрилансер)
    /notifications/      уведомления
    /admin/              административная панель
