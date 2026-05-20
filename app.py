import os
import requests
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Investigation, Evidence, Like, Comment
from forms import (
    RegisterForm,
    LoginForm,
    InvestigationForm,
    EvidenceForm,
    CommentForm,
)

# =========БД И ИНИЦИАЛИЗАЦИЯ ПРОГРАММЫ===========================
app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///detective.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ==========YANDEX GPT=============================================
FOLDER_ID = 'b1g3dgi3bl0mmhcqhma8'
API_KEY = 'AQVNxzo7RmqB0ybPqx4eWRgG9sg4REeaBv1MtoIH'
YANDEX_GPT_URL = (
    'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/ping')
def ping():
    return 'pong'


# ==========ГЕНЕРАЦИЯ ИСТОРИИ======================================
def generate_story(image_path):
    filename = os.path.basename(image_path)

    prompt = (
        f'напиши детективную историю по фотографии {filename}.\n'
        'добавь:\n'
        '- место преступления\n'
        '- подозреваемых\n'
        '- неожиданный поворот\n'
        '- финал расследования'
    )

    body = {
        'modelUri': f'gpt://{FOLDER_ID}/yandexgpt/latest',
        'completionOptions': {
            'stream': False,
            'temperature': 0.7,
            'maxTokens': 800,
        },
        'messages': [
            {
                'role': 'user',
                'text': prompt,
            }
        ],
    }

    headers = {
        'Authorization': f'Api-Key {API_KEY}',
        'Content-Type': 'application/json',
    }

    try:
        response = requests.post(
            YANDEX_GPT_URL,
            headers=headers,
            json=body,
        )

        if response.status_code == 200:
            res = response.json()
            story = res['result']['alternatives'][0]['message']['text']

            return (
                f'ДЕТЕКТИВНОЕ ДЕЛО\n\n'
                f'Улика: {filename}\n\n'
                f'{story}'
            )

        return 'ОШИБКА API'

    except Exception as e:
        return f'Ошибка: {e}'


# ==========ГЛАВНАЯ===============================================
@app.route('/')
def index():
    return render_template('index.html')


# ==========РЕГИСТРАЦИЯ===========================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        existing_user = User.query.filter_by(
            username=form.username.data
        ).first()

        if existing_user:
            flash('Такой пользователь уже есть')
            return redirect(url_for('register'))

        if len(form.username.data) < 3:
            flash('Логин слишком короткий')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
        )

        user = User(
            username=form.username.data,
            password_hash=hashed_password,
        )

        db.session.add(user)
        db.session.commit()

        flash('Регистрация успешна')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


# ========== ВХОД ==============================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(
            username=form.username.data
        ).first()

        if user and check_password_hash(
            user.password_hash,
            form.password.data,
        ):
            login_user(user)
            flash('Вы вошли в аккаунт')
            return redirect(url_for('dashboard'))

        flash('Неверный логин или пароль')

    return render_template('login.html', form=form)


# ==========ВЫХОД===============================================
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта')
    return redirect(url_for('index'))


# ==========ЛИЧНЫЙ КАБИНЕТ=======================================
@app.route('/dashboard')
@login_required
def dashboard():
    investigations = Investigation.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        'dashboard.html',
        investigations=investigations,
    )


# ==========СОЗДАНИЕ ДЕЛА========================================
@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_investigation():
    form = InvestigationForm()

    if form.validate_on_submit():
        if len(form.title.data) < 3:
            flash('Название слишком короткое')
            return redirect(url_for('create_investigation'))

        investigation = Investigation(
            title=form.title.data,
            user_id=current_user.id,
            created_at=datetime.utcnow(),
        )

        db.session.add(investigation)
        db.session.commit()

        flash('Дело создано')
        return redirect(url_for('dashboard'))

    return render_template('create.html', form=form)


# ==========СТРАНИЦА ДЕЛА========================================
@app.route('/investigation/<int:investigation_id>', methods=['GET', 'POST'])
@login_required
def investigation(investigation_id):
    investigation = Investigation.query.get_or_404(investigation_id)

    form = EvidenceForm()
    comment_form = CommentForm()

    if form.validate_on_submit():
        file = form.photo.data

        if file:
            filename = secure_filename(file.filename)

            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

                filepath = os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    filename,
                )

                file.save(filepath)

                story = generate_story(filepath)

                evidence = Evidence(
                    investigation_id=investigation.id,
                    photo_path=filepath,
                    api_response_summary=story,
                )

                db.session.add(evidence)
                db.session.commit()

                flash('Улика добавлена')
                return redirect(url_for('investigation',
                        investigation_id=investigation.id,))

            flash('Можно загружать только картинки')

    evidences = Evidence.query.filter_by(
        investigation_id=investigation.id
    ).all()

    return render_template(
        'investigation.html',
        investigation=investigation,
        evidences=evidences,
        form=form,
        comment_form=comment_form,
    )


# ==========ЛАЙК=================================================
@app.route('/like/<int:investigation_id>')
@login_required
def like_investigation(investigation_id):
    existing_like = Like.query.filter_by(
        user_id=current_user.id,
        investigation_id=investigation_id,
    ).first()

    if not existing_like:
        like = Like(
            user_id=current_user.id,
            investigation_id=investigation_id,
        )

        db.session.add(like)
        db.session.commit()
    else:
        flash('Вы уже поставили лайк')

    return redirect(url_for('investigation', investigation_id=investigation_id))


# ==========КОММЕНТАРИИ==========================================
@app.route('/comment/<int:investigation_id>', methods=['POST'])
@login_required
def add_comment(investigation_id):
    form = CommentForm()

    if form.validate_on_submit():
        if len(form.text.data) < 2:
            flash('Комментарий слишком короткий')
            return redirect(url_for('investigation', investigation_id=investigation_id))

        comment = Comment(
            text=form.text.data,
            user_id=current_user.id,
            investigation_id=investigation_id,
        )

        db.session.add(comment)
        db.session.commit()
        
        flash('Комментарий добавлен')
    return redirect(url_for('investigation', investigation_id=investigation_id))


# ==========ТОП ДЕЛ==============================================
@app.route('/leaderboard')
def leaderboard():
    investigations = Investigation.query.all()
    investigations.sort(key=lambda x: len(x.likes), reverse=True)

    return render_template('leaderboard.html', investigations=investigations,)


# ==========АДМИНКА==============================================
@app.route('/admin')
def admin():
    investigations = Investigation.query.all()
    users = User.query.all()

    return render_template('admin.html', investigations=investigations, users=users,)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
