from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    FileField,
    TextAreaField,
    SelectField,
    BooleanField
)
from wtforms.validators import DataRequired, Length, Optional, Email


# ==========ФОРМА РЕГИСТРАЦИИ==========
class RegisterForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=80)],
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=4)],
    )
    submit = SubmitField('Register')


# ==========ФОРМА ВХОДА==========
class LoginForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired()],
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()],
    )
    submit = SubmitField('Login')


# ==========ФОРМА СОЗДАНИЯ ДЕЛА==========
class InvestigationForm(FlaskForm):
    title = StringField(
        'Название дела',
        validators=[DataRequired(), Length(min=3, max=255)]
    )
    description = TextAreaField(
        'Описание дела',
        validators=[Optional(), Length(max=1000)]
    )
    location = StringField(
        'Место преступления',
        validators=[Optional(), Length(max=200)]
    )
    is_private = BooleanField('Сделать приватным')
    submit = SubmitField('Создать дело')


# ==========ФОРМА ЗАГРУЗКИ УЛИКИ==========
class EvidenceForm(FlaskForm):
    photo = FileField(
        'Фото-улика',
        validators=[DataRequired()]
    )
    submit = SubmitField('Загрузить улику')


# ==========ФОРМА КОММЕНТАРИЯ==========
class CommentForm(FlaskForm):
    text = TextAreaField(
        'Комментарий',
        validators=[DataRequired(), Length(min=2, max=1000)]
    )
    submit = SubmitField('Отправить')


# ==========ФОРМА ПРОФИЛЯ==========
class ProfileForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[Optional(), Email()]
    )
    bio = TextAreaField(
        'О себе',
        validators=[Optional(), Length(max=500)]
    )
    submit = SubmitField('Сохранить')


# ==========ФОРМА СООБЩЕНИЯ==========
class MessageForm(FlaskForm):
    content = TextAreaField(
        'Сообщение',
        validators=[DataRequired(), Length(min=1, max=1000)]
    )
    submit = SubmitField('Отправить')


# ==========ФОРМА ОЦЕНКИ==========
class RatingForm(FlaskForm):
    score = SelectField(
        'Оценка',
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
        validators=[DataRequired()]
    )
    submit = SubmitField('Оценить')
