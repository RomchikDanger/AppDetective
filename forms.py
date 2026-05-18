from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField
from wtforms.validators import DataRequired, Length

# ==========ФОРМА РЕГИСТРАЦИИ============================================================
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4)])
    submit = SubmitField('Register')

# ==========ФОРМА ВХОДА==================================================================
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# ==========ФОРМА СОЗДАНИЯ ДЕЛА==========================================================
class InvestigationForm(FlaskForm):
    title = StringField('Название дела', validators=[DataRequired()])
    submit = SubmitField('Создать дело')

# ==========ФОРМА ЗАГРУЗКИ УЛИКИ=========================================================
class EvidenceForm(FlaskForm):
    photo = FileField('Фото-улика', validators=[DataRequired()])
    submit = SubmitField('Загрузить улику')

# ==========ФОРМА КОММЕНТАРИЯ============================================================
class CommentForm(FlaskForm):
    text = TextAreaField('Комментарий', validators=[DataRequired()])
    submit = SubmitField('Отправить')