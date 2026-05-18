from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# ==========ИНИЦИАЛИЗАЦИЯ =========================================================
db = SQLAlchemy()

# ==========МОДЕЛЬ ПОЛЬЗОВАТЕЛЯ=========================================================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

# ==========МОДЕЛЬ РАССЛЕДОВАНИЯ=========================================================
class Investigation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='active')
    created_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    likes = db.relationship('Like', backref='investigation', lazy=True)
    comments = db.relationship('Comment', backref='investigation', lazy=True)

# ==========МОДЕЛЬ УЛИКИ=========================================================
class Evidence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo_path = db.Column(db.String(255))
    api_response_summary = db.Column(db.Text)
    investigation_id = db.Column(db.Integer, db.ForeignKey('investigation.id'))

# ==========МОДЕЛЬ ЛАЙКОВ=========================================================
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    investigation_id = db.Column(db.Integer, db.ForeignKey('investigation.id'))

# ==========МОДЕЛЬ КОММЕНТАРИЕВ=========================================================
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    investigation_id = db.Column(db.Integer, db.ForeignKey('investigation.id'))