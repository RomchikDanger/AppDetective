import os
import requests
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import (
    db,
    User,
    Investigation,
    Evidence,
    Like,
    Comment,
    Message,
    Friend,
    UserAchievement,
    Achievement,
    Rating)
from forms import (
    RegisterForm,
    LoginForm,
    InvestigationForm,
    EvidenceForm,
    CommentForm,
    ProfileForm,
    MessageForm
)

# ==========БД И ИНИЦИАЛИЗАЦИЯ ПРОГРАММЫ==========
app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///detective.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ==========YANDEX GPT==========
FOLDER_ID = 'b1g3dgi3bl0mmhcqhma8'
API_KEY = 'AQVNxzo7RmqB0ybPqx4eWRgG9sg4REeaBv1MtoIH'
YANDEX_GPT_URL = ('https://llm.api.cloud.yandex.net/'
                  'foundationModels/v1/completion')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/ping')
def ping():
    return 'pong'


# ==========ГЕНЕРАЦИЯ ИСТОРИИ==========
def generate_story(image_path):
    filename = os.path.basename(image_path)

    prompt = (f'напиши детективную историю по фотографии {filename}.\n'
              'добавь:\n- место преступления\n- подозреваемых\n'
              '- неожиданный поворот\n- финал расследования')

    body = {
        'modelUri': f'gpt://{FOLDER_ID}/yandexgpt/latest',
        'completionOptions': {
            'stream': False,
            'temperature': 0.7,
            'maxTokens': 800
        },
        'messages': [{'role': 'user', 'text': prompt}]
    }

    headers = {
        'Authorization': f'Api-Key {API_KEY}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(YANDEX_GPT_URL, headers=headers, json=body)

        if response.status_code == 200:
            res = response.json()
            story = res['result']['alternatives'][0]['message']['text']
            return f'ДЕТЕКТИВНОЕ ДЕЛО\n\nУлика: {filename}\n\n{story}'
        return 'ОШИБКА API'
    except Exception as e:
        return f'Ошибка: {e}'


# ==========ГЛАВНАЯ==========
@app.route('/')
def index():
    return render_template('index.html')


# ==========РЕГИСТРАЦИЯ==========
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        existing_user = User.query.filter_by(
            username=form.username.data).first()

        if existing_user:
            flash('Такой пользователь уже есть')
            return redirect(url_for('register'))

        if len(form.username.data) < 3:
            flash('Логин слишком короткий')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(
            form.password.data, method='pbkdf2:sha256')
        user = User(
            username=form.username.data, password_hash=hashed_password)

        db.session.add(user)
        db.session.commit()

        flash('Регистрация успешна')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


# ==========ВХОД==========
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and check_password_hash(
                user.password_hash, form.password.data):
            login_user(user)
            flash('Вы вошли в аккаунт')
            return redirect(url_for('dashboard'))

        flash('Неверный логин или пароль')

    return render_template('login.html', form=form)


# ==========ВЫХОД==========
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта')
    return redirect(url_for('index'))


# ==========ЛИЧНЫЙ КАБИНЕТ==========
@app.route('/dashboard')
@login_required
def dashboard():
    investigations = Investigation.query.filter_by(
        user_id=current_user.id).all()
    return render_template(
        'dashboard.html', investigations=investigations)


# ==========СОЗДАНИЕ ДЕЛА==========
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
            created_at=datetime.utcnow()
        )

        db.session.add(investigation)
        current_user.points += 5
        db.session.commit()
        check_achievements(current_user.id)

        flash('Дело создано +5 очков')
        return redirect(url_for('dashboard'))

    return render_template('create.html', form=form)


# ==========УДАЛЕНИЕ РАССЛЕДОВАНИЯ==========
@app.route('/delete_investigation/<int:investigation_id>')
@login_required
def delete_investigation(investigation_id):
    investigation = Investigation.query.get_or_404(investigation_id)

    if investigation.user_id != current_user.id:
        flash('Нет прав для удаления этого дела')
        return redirect(url_for('dashboard'))

    Evidence.query.filter_by(investigation_id=investigation_id).delete()
    Like.query.filter_by(investigation_id=investigation_id).delete()
    Comment.query.filter_by(investigation_id=investigation_id).delete()
    Rating.query.filter_by(investigation_id=investigation_id).delete()

    db.session.delete(investigation)
    db.session.commit()

    flash('Дело удалено')
    return redirect(url_for('dashboard'))


# ==========СТРАНИЦА ДЕЛА==========
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
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                story = generate_story(filepath)
                evidence = Evidence(
                    investigation_id=investigation.id,
                    photo_path=filepath,
                    api_response_summary=story
                )

                db.session.add(evidence)
                current_user.points += 3
                db.session.commit()
                check_achievements(current_user.id)

                flash('Улика добавлена (+3 очка)')
                return redirect(url_for(
                    'investigation', investigation_id=investigation.id))
            flash('Можно загружать только картинки')

    evidences = Evidence.query.filter_by(
        investigation_id=investigation.id).all()
    return render_template(
        'investigation.html',
        investigation=investigation,
        evidences=evidences,
        form=form,
        comment_form=comment_form
    )


# ==========ЛАЙК==========
@app.route('/like/<int:investigation_id>')
@login_required
def like_investigation(investigation_id):
    existing_like = Like.query.filter_by(
        user_id=current_user.id,
        investigation_id=investigation_id
    ).first()

    if not existing_like:
        like = Like(user_id=current_user.id,
                    investigation_id=investigation_id)
        db.session.add(like)
        current_user.points += 1
        db.session.commit()
        check_achievements(current_user.id)

        flash('Лайк поставлен (+1 очко)')
    else:
        flash('Вы уже поставили лайк')

    return redirect(url_for('investigation',
                            investigation_id=investigation_id))


# ==========КОММЕНТАРИИ==========
@app.route('/comment/<int:investigation_id>', methods=['POST'])
@login_required
def add_comment(investigation_id):
    form = CommentForm()

    if form.validate_on_submit():
        if len(form.text.data) < 2:
            flash('Комментарий слишком короткий')
            return redirect(url_for('investigation',
                                    investigation_id=investigation_id))

        comment = Comment(
            text=form.text.data,
            user_id=current_user.id,
            investigation_id=investigation_id
        )

        db.session.add(comment)
        current_user.points += 2
        db.session.commit()
        check_achievements(current_user.id)

        flash('Комментарий добавлен (+2 очка)')

    return redirect(url_for('investigation',
                            investigation_id=investigation_id))


# ==========ТОП ДЕЛ==========
@app.route('/leaderboard')
def leaderboard():
    investigations = Investigation.query.all()
    investigations.sort(key=lambda x: len(x.likes), reverse=True)
    return render_template('leaderboard.html',
                           investigations=investigations)


# ==========ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ==========
@app.route('/profile/<int:user_id>')
@login_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    investigations = Investigation.query.filter_by(user_id=user_id).all()
    return render_template('profile.html', user=user,
                           investigations=investigations)


# ==========РЕДАКТИРОВАНИЕ ПРОФИЛЯ==========
@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm()

    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash('Профиль обновлен')
        return redirect(url_for('user_profile',
                                user_id=current_user.id))

    form.email.data = current_user.email
    form.bio.data = current_user.bio
    return render_template(
        'edit_profile.html', form=form)


# ==========ПОИСК==========
@app.route('/search')
def search():
    query = request.args.get('q', '')
    investigations = Investigation.query.filter(
        Investigation.title.contains(query)
    ).all()
    return render_template('search.html',
                           investigations=investigations, query=query)


# ==========СТАТИСТИКА==========
@app.route('/statistics')
@login_required
def statistics():
    total_users = User.query.count()
    total_investigations = Investigation.query.count()
    total_evidences = Evidence.query.count()
    total_likes = Like.query.count()
    total_comments = Comment.query.count()
    return render_template(
        'statistics.html',
        total_users=total_users,
        total_investigations=total_investigations,
        total_evidences=total_evidences,
        total_likes=total_likes,
        total_comments=total_comments
    )


# ==========ОТПРАВКА СООБЩЕНИЯ==========
@app.route('/send_message/<int:receiver_id>', methods=['GET', 'POST'])
@login_required
def send_message(receiver_id):
    receiver = User.query.get_or_404(receiver_id)
    form = MessageForm()

    if form.validate_on_submit():
        message = Message(
            sender_id=current_user.id,
            receiver_id=receiver_id,
            content=form.content.data
        )
        db.session.add(message)
        db.session.commit()
        flash('Сообщение отправлено')
        return redirect(url_for('inbox'))

    return render_template('send_message.html', form=form, receiver=receiver)


# ==========ВХОДЯЩИЕ СООБЩЕНИЯ==========
@app.route('/inbox')
@login_required
def inbox():
    messages = (Message.query.filter_by(receiver_id=current_user.id).
                order_by(Message.created_at.desc()).all())
    return render_template('inbox.html', messages=messages)


# ==========ОТПРАВЛЕННЫЕ СООБЩЕНИЯ==========
@app.route('/sent')
@login_required
def sent_messages():
    messages = (Message.query.filter_by(sender_id=current_user.id).
                order_by(Message.created_at.desc()).all())
    return render_template('sent.html', messages=messages)


# ==========ПРОЧИТАТЬ СООБЩЕНИЕ==========
@app.route('/message/<int:message_id>')
@login_required
def view_message(message_id):
    message = Message.query.get_or_404(message_id)
    if message.receiver_id == current_user.id and not message.is_read:
        message.is_read = True
        db.session.commit()
    return render_template('message.html', message=message)


# ==========ДОБАВИТЬ ДРУГА==========
@app.route('/add_friend/<int:friend_id>')
@login_required
def add_friend(friend_id):
    if friend_id == current_user.id:
        flash('Нельзя добавить самого себя')
        return redirect(url_for('user_profile', user_id=friend_id))

    existing = Friend.query.filter_by(user_id=current_user.id,
                                      friend_id=friend_id).first()
    if existing:
        flash('Запрос уже отправлен')
    else:
        friend = Friend(user_id=current_user.id, friend_id=friend_id)
        db.session.add(friend)
        db.session.commit()
        flash('Запрос в друзья отправлен')

    return redirect(url_for('user_profile', user_id=friend_id))


# ==========СПИСОК ДРУЗЕЙ==========
@app.route('/friends')
@login_required
def friends_list():
    friends = Friend.query.filter_by(
        user_id=current_user.id, is_accepted=True).all()
    pending_requests = Friend.query.filter_by(
        friend_id=current_user.id, is_accepted=False).all()

    return render_template(
        'friends.html', friends=friends, pending_requests=pending_requests)


# ==========ПРИНЯТЬ ЗАПРОС В ДРУЗЬЯ==========
@app.route('/accept_friend/<int:friend_id>')
@login_required
def accept_friend(friend_id):
    friendship = Friend.query.filter_by(
        user_id=friend_id, friend_id=current_user.id).first()
    if friendship:
        friendship.is_accepted = True
        db.session.commit()
        flash('Друг добавлен')
    return redirect(url_for('friends_list'))


# ==========ПОИСК ПОЛЬЗОВАТЕЛЕЙ==========
@app.route('/search_users')
@login_required
def search_users():
    query = request.args.get('q', '')
    users = []
    if query:
        users = User.query.filter(User.username.contains(query)).all()
    return render_template('search_users.html', users=users, query=query)


# ==========ДОСТИЖЕНИЯ ПОЛЬЗОВАТЕЛЯ==========
@app.route('/achievements')
@login_required
def achievements():
    user_achievements = UserAchievement.query.filter_by(
        user_id=current_user.id).all()
    all_achievements = Achievement.query.all()
    return render_template(
        'achievements.html',
        user_achievements=user_achievements,
        all_achievements=all_achievements)


# ==========ДОБАВИТЬ ОЧКИ==========
@app.route('/add_points/<int:points>')
@login_required
def add_points(points):
    if not hasattr(current_user, 'points'):
        current_user.points = 0
    current_user.points += points
    db.session.commit()

    achievements = Achievement.query.all()
    for ach in achievements:
        existing = UserAchievement.query.filter_by(
            user_id=current_user.id, achievement_id=ach.id).first()
        if not existing and current_user.points >= ach.required_points:
            new = UserAchievement(
                user_id=current_user.id, achievement_id=ach.id)
            db.session.add(new)
            db.session.commit()
            flash(f'Получено достижение: {ach.name}!')

    flash(f'Добавлено {points} очков')
    return redirect(url_for('achievements'))


# ==========ОЦЕНКА РАССЛЕДОВАНИЯ==========
@app.route('/rate_investigation/<int:investigation_id>/<int:score>')
@login_required
def rate_investigation(investigation_id, score):
    if score < 1 or score > 5:
        flash('Оценка должна быть от 1 до 5')
        return redirect(url_for(
            'investigation', investigation_id=investigation_id))

    existing = Rating.query.filter_by(
        user_id=current_user.id, investigation_id=investigation_id).first()
    if existing:
        existing.score = score
    else:
        rating = Rating(
            user_id=current_user.id,
            investigation_id=investigation_id, score=score)
        db.session.add(rating)

    db.session.commit()
    flash('Оценка сохранена')
    return redirect(url_for(
        'investigation', investigation_id=investigation_id))


# ==========АДМИНКА==========
@app.route('/admin')
def admin():
    investigations = Investigation.query.all()
    users = User.query.all()
    return render_template(
        'admin.html', investigations=investigations, users=users)


# ==========ПРОВЕРКА ДОСТИЖЕНИЙ==========
def check_achievements(user_id):
    user = User.query.get(user_id)
    achievements = Achievement.query.all()
    new_achievements = []

    for ach in achievements:
        existing = UserAchievement.query.filter_by(
            user_id=user_id,
            achievement_id=ach.id
        ).first()

        if not existing and user.points >= ach.required_points:
            new = UserAchievement(user_id=user_id, achievement_id=ach.id)
            db.session.add(new)
            new_achievements.append(ach.name)

    if new_achievements:
        db.session.commit()
        for ach_name in new_achievements:
            flash(f'ПОЛУЧЕНО ДОСТИЖЕНИЕ: {ach_name}!')


# ==========СОЗДАНИЕ ДОСТИЖЕНИЙ==========
def create_achievements():
    with app.app_context():
        if Achievement.query.count() == 0:
            achievements = [
                Achievement(name='Новичок',
                            description='Первые 10 очков',
                            required_points=10),
                Achievement(name='Следователь',
                            description='50 очков',
                            required_points=50),
                Achievement(name='Детектив',
                            description='100 очков',
                            required_points=100),
                Achievement(name='Легенда',
                            description='500 очков',
                            required_points=500),
            ]
            for ach in achievements:
                db.session.add(ach)
            db.session.commit()
        else:
            print('ДОСТИЖЕНИЙ НЕТ')


# ==========ЗАПУСК==========
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_achievements()
    app.run(debug=True)
