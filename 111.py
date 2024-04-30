from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_user
from data.users import User
from forms.user import RegistrationForm, LoginForm
from data.db_session import global_init, create_session
from data import db_session

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
global_init('photos.db')
login_manager = LoginManager()
login_manager.init_app(app)



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




@app.route('/load-picture')
def load():
    return render_template('load-picture.html')


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
        print(user.check_password(form.password.data))
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


if __name__ == '__main__':
    app.run(debug=True)
