from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# ==========ВСПОМОГАТЕЛЬНЫЕ ТАБЛИЦЫ==========
investigation_tags = db.Table(
    'investigation_tags',
    db.Column('investigation_id', db.Integer,
              db.ForeignKey('investigation.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)


# ==========МОДЕЛЬ ПОЛЬЗОВАТЕЛЯ==========
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True)
    bio = db.Column(db.Text)
    avatar_path = db.Column(db.String(255))
    points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)


# ==========МОДЕЛЬ КАТЕГОРИЙ==========
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)


# ==========МОДЕЛЬ ТЕГОВ==========
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)


# ==========МОДЕЛЬ РАССЛЕДОВАНИЯ==========
class Investigation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='active')
    location = db.Column(db.String(255))
    is_private = db.Column(db.Boolean, default=False)
    views_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    likes = db.relationship('Like', backref='investigation', lazy=True)
    comments = db.relationship('Comment', backref='investigation', lazy=True)
    tags = db.relationship(
        'Tag',
        secondary=investigation_tags,
        lazy='subquery',
        backref=db.backref('investigations', lazy=True)
    )
    category = db.relationship('Category', backref='investigations')


# ==========МОДЕЛЬ УЛИКИ==========
class Evidence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo_path = db.Column(db.String(255))
    api_response_summary = db.Column(db.Text)
    investigation_id = db.Column(db.Integer,
                                 db.ForeignKey('investigation.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_analyzed = db.Column(db.Boolean, default=False)
    confidence_score = db.Column(db.Float, default=0.0)


# ==========МОДЕЛЬ ЛАЙКОВ==========
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    investigation_id = db.Column(db.Integer,
                                 db.ForeignKey('investigation.id'))


# ==========МОДЕЛЬ КОММЕНТАРИЕВ==========
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    investigation_id = db.Column(db.Integer,
                                 db.ForeignKey('investigation.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User',
                           backref='comments', foreign_keys=[user_id])


# ==========МОДЕЛЬ УВЕДОМЛЕНИЙ==========
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='notifications')


# ==========МОДЕЛЬ СООБЩЕНИЙ==========
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer,
                          db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer,
                            db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User',
                             foreign_keys=[sender_id],
                             backref='sent_messages')
    receiver = db.relationship('User',
                               foreign_keys=[receiver_id],
                               backref='received_messages')


# ==========МОДЕЛЬ ДРУЗЕЙ==========
class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_id = db.Column(db.Integer,
                          db.ForeignKey('user.id'), nullable=False)
    is_accepted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', foreign_keys=[user_id],
                           backref='friendships')
    friend = db.relationship('User', foreign_keys=[friend_id])


# ==========МОДЕЛЬ ДОСТИЖЕНИЙ==========
class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(255))
    required_points = db.Column(db.Integer, default=0)


class UserAchievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    achievement_id = db.Column(db.Integer,
                               db.ForeignKey('achievement.id'),
                               nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='user_achievements')
    achievement = db.relationship('Achievement', backref='users')


# ==========МОДЕЛЬ РЕЙТИНГА==========
class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    investigation_id = db.Column(db.Integer,
                                 db.ForeignKey('investigation.id'),
                                 nullable=False)
    score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='ratings')
    investigation = db.relationship('Investigation', backref='ratings')
