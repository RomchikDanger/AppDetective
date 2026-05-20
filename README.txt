ВОЗМОЖНОСТИ

- авторизация - регистрация и вход в аккаунт
- управление делами — создание, просмотр, удаление расследований
- улики — загрузка фото с генерацией детективной истории через Yandex GPT
- комментарии — обсуждение дел
- лайки — оценка понравившихся расследований
- рейтинг — оценка дел от 1 до 5 звёзд
- достижения — система очков и наград за активность
- друзья — добавление в друзья, отправка сообщений
- личные сообщения — общение между пользователями
- поиск — поиск пользователей
- статистика — общая статистика приложения
- админка — просмотр всех дел

---

ИСПОЛЬЗУЕМЫЕ ТЕХНОЛОГИИ
- Python 3
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- Bootstrap 5
- SQLite
- Yandex GPT API

---

СТРУКТУРА ПРОЕКТА

photo-detective/
├── app.py
├── models.py
├── forms.py
├── requirements.txt
├── README.md
├── static/
│   └── uploads/
└── templates/
    ├── base.html
    ├── index.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── create.html
    ├── investigation.html
    ├── leaderboard.html
    ├── profile.html
    ├── edit_profile.html
    ├── search.html
    ├── statistics.html
    ├── inbox.html
    ├── sent.html
    ├── message.html
    ├── send_message.html
    ├── friends.html
    ├── search_users.html
    ├── achievements.html
    └── admin.html
