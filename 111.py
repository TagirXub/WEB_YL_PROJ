from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_user, login_required, logout_user
from data.users import User
from forms.user import RegistrationForm, LoginForm
from data.db_session import global_init, create_session
from data import db_session
from flask import request
from werkzeug.utils import secure_filename
import uuid
app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
global_init('photos.db')
login_manager = LoginManager()
login_manager.init_app(app)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def register():
    ses = create_session()
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data,surname=form.surname.data, email=form.email.data, hashed_password=form.password.data)
        user.set_password(form.password.data)
        ses.add(user)
        ses.commit()
        flash('Вы успешно зарегистрировались!', 'success')
        return redirect(url_for('login'))
    return render_template('signup1.html', title='Регистрация', form=form)


@app.route('/empty')
def empty():
    return render_template('empty.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/load-picture', methods=['GET', 'POST'])
def load():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Не могу прочитать файл')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('Нет выбранного файла')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            uid = uuid.uuid4()
            file.save(f"static/dataset/{uid}.jpg")
            return redirect(url_for('check_file', name=f'{uid}.jpg'))
    return render_template('load-picture.html')

@app.route('/check/<name>', methods=['GET', 'POST'])
def check_file(name):
    """
    просто показываем фотку
    можно добавить чтобы внизу писался класс
    тип вот фотка ее класс ГРафика
    и опиисание еще если успеете
    """
    path = f'/dataset/{name}'
    if request.method == 'POST':
        return redirect(url_for('download_file', name=path.split("/")[-1]))
    else:
        return render_template('check-picture.html', path=url_for('static', filename=path))
@app.route('/tagir')
def tagir():
    return render_template('tagir.html')


@app.route('/adilet')
def adilet():
    return render_template('adilet.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


if __name__ == '__main__':
    app.run(debug=True)