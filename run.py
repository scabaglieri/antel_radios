from flask import Flask, render_template, request, redirect, url_for
from forms import SignupForm, PostForm, LoginForm
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
#from models import users
from werkzeug.urls import url_parse
from flask_sqlalchemy import SQLAlchemy
from models import User, Post, Radio
from aux_functions import insert_radios, delete_radio_by_name
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:db-flask@localhost:3306/portaltelcos'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager(app)
login_manager.login_view = "login"


radios = []

@app.route("/")
@login_required
def index():
    radios = Radio.get_all()
    return render_template("index.html", radios=radios)

@app.route("/p/<string:slug>/")
def show_post(slug):
    post = Post.get_by_slug(slug)
    if post is None:
        abort(404)
    return render_template("post_view.html", post=post)


@app.route("/r/<string:name>/")
def show_radio(name):
    radio = Radio.get_by_name(name)
    print(radio)
    if radio is None:
        #abort(404)
        print(radio)
        print('Que paso?')
        return render_template("index.html", radios=radios)
    return render_template("radio_view.html", radio=radio)

@app.route("/signup/", methods=["GET", "POST"])
def show_signup_form():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = SignupForm()
    error = None
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        # Comprobamos que no hay ya un usuario con ese email
        user = User.get_by_email(email)
        if user is not None:
            error = f'El email {email} ya está siendo utilizado por otro usuario'
        else:
            # Creamos el usuario y lo guardamos
            user = User(name=name, email=email)
            user.set_password(password)
            user.save()
            # Dejamos al usuario logueado
            login_user(user, remember=True)
            next_page = request.args.get('next', None)
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
    return render_template("signup_form.html", form=form, error=error)

@app.route("/admin/radio/", methods=['GET', 'POST'], defaults={'radio_id': None})
@app.route("/admin/radio/<int:radio_id>/", methods=['GET', 'POST'])
@login_required
def radio_form(radio_id):
    form = PostForm()
    if request.method == 'POST':
        name = request.form['name']
        unique_name = name + "_rx"
        username = request.form['username']
        password = request.form['password']
      
        radio = Radio(name=name, unique_name=unique_name, username=username, password=password, is_active=True)
        radio.save()
        

       #Armo las lineas para agregar en la configuracion de icecast

        space = "    "
        lines_to_add = [space+'<mount type="normal">', space+space+"<mount-name>/"+unique_name+"</mount-name>", space+space+"<username>"+username+"</username>", space+space+"<password>"+password+"</password>", space+"</mount>"]
        line_numbers_for_insertion = [146]
        filename = "/etc/icecast2/icecast.xml"
        insert_radios(filename, lines_to_add, line_numbers_for_insertion)
        command="sudo systemctl reload icecast2.service"
        os.system(command)


        return redirect(url_for('index'))
    return render_template("admin/radio_form.html")

@app.route("/admin/delete/", methods=['GET', 'POST'])
@login_required
def radio_delete():
    if request.method == 'POST':
        unique_name= request.form['unique_name']
        filename = "/etc/icecast2/icecast.xml"
        delete_radio_by_name(filename, unique_name)
        Radio.remove_by_unique_name(unique_name)

    return redirect(url_for('index'))

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        #user = get_user(form.email.data)
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
    return render_template('login_form.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
