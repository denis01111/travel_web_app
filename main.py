from flask import render_template, redirect, request
from flask_login import LoginManager, login_user, logout_user, current_user
from werkzeug.utils import secure_filename
from data import db_session, users, Reviews
from data.loginform import LoginForm
from data.register import RegisterForm
from data.Profile import ProfileForm
from data.place import Place
from flask import Flask
from rev_form import RevForm
from apiweather import Searching
import os


ALLOWED_EXTENSIONS = ('png', 'jpg', 'jpeg', 'gif')
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
weather_img = {'Clear': ['static/img/state_weather/clearsky.png', 'Ясно'],
               'Few_clouds': ['static/img/state_weather/fewclouds.png', 'Переменная облачность'],
               'Scattered_clouds': ['static/img/state_weather/scatteredclouds.png', 'Облачно с прояснениями'],
               'Broken_clouds': ['static/img/state_weather/brokenclouds.png', 'Пасмурно'],
               'Drizzle': ['static/img/state_weather/showerrain.png', 'Моросящий дождь'],
               'Rain': ['static/img/state_weather/rain.png', 'Дождь'],
               'Thunderstorm': ['static/img/state_weather/thunderstorm.png', 'Гроза'],
               'Snow': ['static/img/state_weather/snow.png', 'Снег'],
               'Mist': ['static/img/state_weather/mist.png', 'Туман'],
               'Smoke': ['static/img/state_weather/mist.png', 'Дымок'],
               'Haze': ['static/img/state_weather/mist.png', 'Лёгкий туман'],
               'Dust': ['static/img/state_weather/mist.png', 'Пыльная буря'],
               'Fog': ['static/img/state_weather/mist.png', 'Густой туман'],
               'Sand': ['static/img/state_weather/mist.png', 'Песчаная буря'],
               'Ash': ['static/img/state_weather/mist.png', 'Вулканическая пыль'],
               'Squall': ['static/img/state_weather/mist.png', 'Шквал'],
               'Tornado': ['static/img/state_weather/mist.png', 'Торнадо']}


@login_manager.user_loader
def load_user(user_id):
    sessions = db_session.create_session()
    return sessions.query(users.User).get(user_id)


@app.route('/exit')
def logout():
    logout_user()
    return redirect('/')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    sessions = db_session.create_session()
    user = sessions.query(users.User).filter(users.User.id == current_user.get_id()).first()
    return render_template('Profile.html', title='Авторизация', user=user)


@app.route('/profile_update', methods=['GET', 'POST'])
def profile_update():
    form = ProfileForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            sessions = db_session.create_session()
            user = sessions.query(users.User).filter(users.User.id == current_user.get_id()).first()
            if user.password != form.password.data:
                return render_template('profile_update.html', title='Редактирование профиля',
                                       form=form,
                                       message='Неправильный пароль!')
            if form.email.data != '':
                user.email = form.email.data
            if form.password_new.data != '':
                user.password = form.password_new.data
            if form.telephone.data != '':
                user.telephone = form.telephone.data
            sessions.add(user)
            sessions.commit()
            return render_template('profile.html', title='Обновление профиля', form=form,
                                   message='Данные успешно изменены', user=user)
        return render_template('profile_update.html', title='Обновление профиля', form=form,
                               message='')
    return render_template('profile_update.html', title='Авторизация', form=form, message='')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if len(form.password.data) < 8:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Короткий пароль!")
        if 'qwerty' in form.password.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароль содержит всем известную комбинацию 'qwerty'!")
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        sessions = db_session.create_session()
        if sessions.query(users.User).filter(users.User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        f = form.img.data
        filename = secure_filename(f.filename)
        f.save(os.path.join('static/img_users/' + ''.join(form.email.data.split('.')) + '.png'))
        user = users.User(
            name=form.name.data,
            email=form.email.data,
            password=form.password.data,
            img='static/img_users/' + ''.join(form.email.data.split('.')) + '.png',
            telephone=form.telephone.data
        )
        user.set_password(form.password.data)
        sessions.add(user)
        sessions.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        sessions = db_session.create_session()
        user = sessions.query(users.User).filter(users.User.email == form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html', message='Неправильный логин или пароль', form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/')
def delete():
    return render_template("main_display.html", title='Главная', message='Абхазия')


@app.route('/abxazia', methods=['GET', 'POST'])
def abxazia():
    form = RevForm()
    data = ''
    sessions = db_session.create_session()
    data = (sessions.query(Reviews.Review.name, Reviews.Review.text).filter(Reviews.Review.place == 'АБХАЗИЯ'))[::]
    if request.method == 'POST':
        name = sessions.query(users.User.name).filter(users.User.id == current_user.get_id()).first()[0]
        img = (sessions.query(users.User.img))[::]
        for i in range(len(data)):
            for j in range(len(img)):
                data[i] = list(data[i])
                data[i].append(img[j][0])
                data[i] = tuple(data[i])
                break
        rev = Reviews.Review(
            name=name,
            text=form.text.data,
            place='АБХАЗИЯ'
        )
        sessions.add(rev)
        sessions.commit()
        return redirect('/abxazia')
    information = sessions.query(Place.info).filter(Place.name == 'АБХАЗИЯ').first()[0]
    weather = Searching(43.003852, 41.019151).return_weather().split()
    img, description = weather_img[weather[1]]
    weather = [str(weather[0]) + "°"] + [description] + [img]
    return render_template('abxazia.html', title='Абхазия', information=information, weather=weather, form=form,
                           data=data)


@app.route('/kabardino_balkaria', methods=['GET', 'POST'])
def kabardino_balkaria():
    form = RevForm()
    sessions = db_session.create_session()
    data = ''
    data = (sessions.query(Reviews.Review.name, Reviews.Review.text).filter(
        Reviews.Review.place == 'КАБАРДИНО-БАЛКАРИЯ'))[::]
    if request.method == 'POST':
        name = sessions.query(users.User.name).filter(users.User.id == current_user.get_id()).first()[0]
        img = (sessions.query(users.User.img))[::]
        for i in range(len(data)):
            for j in range(len(img)):
                data[i] = list(data[i])
                data[i].append(img[j][0])
                data[i] = tuple(data[i])
                break
        rev = Reviews.Review(
            name=name,
            text=form.text.data,
            place='КАБАРДИНО-БАЛКАРИЯ'
        )
        sessions.add(rev)
        sessions.commit()
        return redirect('/kabardino_balkaria')
    information = sessions.query(Place.info).filter(Place.name == 'КАБАРДИНО-БАЛКАРИЯ').first()[0]
    weather = Searching(43.485259, 43.607072).return_weather().split()
    img, description = weather_img[weather[1]]
    weather = [str(weather[0]) + "°"] + [description] + [img]
    return render_template('kabardino_balkaria.html', title='Кабардино-Балкария', information=information, form=form,
                           data=data, weather=weather)


@app.route('/krasnodarskiy_kray', methods=['GET', 'POST'])
def krasnodarskiy_kray():
    form = RevForm()
    data = ''
    sessions = db_session.create_session()
    data = (sessions.query(Reviews.Review.name, Reviews.Review.text).filter(Reviews.Review.place == 'КРАСНОДАРСКИЙ КРАЙ'))[::]
    if request.method == 'POST':
        print(data)
        name = sessions.query(users.User.name).filter(users.User.id == current_user.get_id()).first()[0]
        img = (sessions.query(users.User.img))[::]
        for i in range(len(data)):
            for j in range(len(img)):
                data[i] = list(data[i])
                data[i].append(img[j][0])
                data[i] = tuple(data[i])
                break
        rev = Reviews.Review(
            name=name,
            text=form.text.data,
            place='КРАСНОДАРСКИЙ КРАЙ'
        )
        sessions.add(rev)
        sessions.commit()
        return redirect('/krasnodarskiy_kray')
    information = sessions.query(Place.info).filter(Place.name == 'КРАСНОДАРСКИЙ КРАЙ').first()[0]
    weather = Searching(45.035470, 38.975313).return_weather().split()
    img, description = weather_img[weather[1]]
    weather = [str(weather[0]) + "°"] + [description] + [img]
    return render_template('krasnodarskiy_kray.html', title='Краснодарский край', information=information, form=form,
                           data=data, weather=weather)


@app.route('/crimea', methods=['GET', 'POST'])
def crimea():
    form = RevForm()
    data = ''
    sessions = db_session.create_session()
    data = (sessions.query(Reviews.Review.name, Reviews.Review.text).filter(Reviews.Review.place == 'КРЫМ'))[::]
    if request.method == 'POST':
        name = sessions.query(users.User.name).filter(users.User.id == current_user.get_id()).first()[0]
        img = (sessions.query(users.User.img))[::]
        for i in range(len(data)):
            for j in range(len(img)):
                data[i] = list(data[i])
                data[i].append(img[j][0])
                data[i] = tuple(data[i])
                break
        rev = Reviews.Review(
            name=name,
            text=form.text.data,
            place='КРЫМ'
        )
        sessions.add(rev)
        sessions.commit()
        return redirect('/crimea')
    information = sessions.query(Place.info).filter(Place.name == 'КРЫМ').first()[0]
    weather = Searching(44.948237, 34.100318).return_weather().split()
    img, description = weather_img[weather[1]]
    weather = [str(weather[0]) + "°"] + [description] + [img]
    return render_template('crimea.html', title='Крым', information=information, weather=weather, form=form,
                           data=data)


@app.route('/karelia', methods=['GET', 'POST'])
def karelia():
    form = RevForm()
    data = ''
    sessions = db_session.create_session()
    data = (sessions.query(Reviews.Review.name, Reviews.Review.text).filter(Reviews.Review.place == 'КАРЕЛИЯ'))[::]
    if request.method == 'POST':
        name = sessions.query(users.User.name).filter(users.User.id == current_user.get_id()).first()[0]
        img = (sessions.query(users.User.img))[::]
        for i in range(len(data)):
            for j in range(len(img)):
                data[i] = list(data[i])
                data[i].append(img[j][0])
                data[i] = tuple(data[i])
                break
        rev = Reviews.Review(
            name=name,
            text=form.text.data,
            place='КАРЕЛИЯ'
        )
        sessions.add(rev)
        sessions.commit()
        return redirect('/karelia')
    information = sessions.query(Place.info).filter(Place.name == 'КАРЕЛИЯ').first()[0]
    weather = Searching(61.787374, 34.354325).return_weather().split()
    img, description = weather_img[weather[1]]
    weather = [str(weather[0]) + "°"] + [description] + [img]
    return render_template('karelia.html', title='Карелия', information=information, weather=weather, form=form,
                           data=data)


@app.route('/adygeya', methods=['GET', 'POST'])
def adygeya():
    form = RevForm()
    data = ''
    sessions = db_session.create_session()
    data = (sessions.query(Reviews.Review.name, Reviews.Review.text).filter(
        Reviews.Review.place == 'РЕСПУБЛИКА АДЫГЕЯ'))[::]
    if request.method == 'POST':
        name = sessions.query(users.User.name).filter(users.User.id == current_user.get_id()).first()[0]
        img = (sessions.query(users.User.img))[::]
        for i in range(len(data)):
            for j in range(len(img)):
                data[i] = list(data[i])
                data[i].append(img[j][0])
                data[i] = tuple(data[i])
                break
        rev = Reviews.Review(
            name=name,
            text=form.text.data,
            place='РЕСПУБЛИКА АДЫГЕЯ'
        )
        sessions.add(rev)
        sessions.commit()
        return redirect('/adygeya')
    information = sessions.query(Place.info).filter(Place.name == 'РЕСПУБЛИКА АДЫГЕЯ').first()[0]
    weather = Searching(44.608865, 40.098548).return_weather().split()
    img, description = weather_img[weather[1]]
    weather = [str(weather[0]) + "°"] + [description] + [img]
    return render_template('adygeya.html', title='Адыгея', information=information, weather=weather, form=form,
                           data=data)


@app.route('/about_me')
def about_me():
    return render_template('about_me.html', title='Обо мне')


def main():
    db_session.global_init('db/blogs.sqlite')
    app.run()


if __name__ == '__main__':
    main()
