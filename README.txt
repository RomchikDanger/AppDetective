веб-приложение на Flask
- зарегистрироваться и войти в аккаунт
- создавать детективные дела
- загружать фотографии(улики)
- получать сгенерированную AI историю
- лайкать расследования
- оставлять комменты
- просматривать лидерборд

---

используемые технологии

- Python 3
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- Bootstrap 5
- SQLite
- Yandex GPT API

---

структура проекта

PhotoDetective/
├── app.py
├── models.py
├── forms.py
├── requirements.txt
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── create.html
│   ├── investigation.html
│   ├── leaderboard.html
│   └── admin.html
│
├── static/
│   └── uploads/
│
└── instance/
