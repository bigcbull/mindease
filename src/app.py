#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Flask module."""

import os
from pathlib import Path
from textwrap import dedent
from flask import Flask, render_template, request, flash, url_for, redirect
from flask_login import LoginManager, login_user, login_required, logout_user
import bcrypt
from dotenv import load_dotenv
from src.validator import ValidateRegister, ValidateLogin
from src.utils.register.register import Register
from src.utils.login.login import Login
from src.utils.user.user import User

load_dotenv()  # load .env

ROOT_DIR = Path(__file__).parent.parent  # getting root dir path
STATIC_DIR = (ROOT_DIR).joinpath('static')  # generating static dir path
TEMPLATES_DIR = (ROOT_DIR).joinpath(
    'templates')  # generating templates dir path


app = Flask(__name__,
            static_folder=STATIC_DIR,
            template_folder=TEMPLATES_DIR)  # init flask app

# assigning secret key for flask app
app.secret_key = os.getenv('APP_SECRET_KEY')

login_manager = LoginManager()
login_manager.init_app(app)


@app.route("/")  # route
def home_page():
    """Route for home page."""
    data = {"doc_title": "Home | Mindease"}
    return render_template("index.html", data=data)


@app.route('/register', methods=['POST', 'GET'])  # route
def register():
    """Route for account registration page."""
    form = ValidateRegister(request.form)
    if request.method == 'POST' and form.validate():
        hashed_pwd = encrypt_password(str.encode(form.password.data))

        user_data = {'first_name': form.first_name.data,
                     'last_name': form.last_name.data,
                     'email': form.email.data,
                     'password': hashed_pwd,
                     'birth': form.birth.data,
                     'gender': form.gender.data
                     }

        user = Register(user_data)
        result = user.register_user()

        if result['registration_succeeded']:
            flash(dedent("""\
                    Successfully registered.
                    We will notify you once our platform launches!"""),
                  "success")
        else:
            flash("Email already exists", "error")

    data = {"doc_title": "Register | Mindease", "register_form": form}
    return render_template("register.html", data=data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Route for login page."""
    form = ValidateLogin(request.form)
    if request.method == 'POST' and form.validate():

        user_data = {'email': form.email.data,
                     'password': form.password.data,
                     }

        user_login = Login()
        result = user_login.login(user_data['email'], user_data['password'])

        if result['login_succeeded']:
            user_id = load_user(user_data['email'])
            login_user(user_id)

            return redirect(url_for('dashboard'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Route to logout a user."""
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Route for user dashboard."""
    return 'Welcome, user!'


@login_manager.user_loader
def load_user(email):
    """Load user id from database based on email."""
    user = User(email=email, name=None,
                password=None, birth=None, gender=None, user_id=None)

    return user.get_user_id(email)


def encrypt_password(password):
    """Encrypt registration password."""
    hashed_pwd = bcrypt.hashpw(password, bcrypt.gensalt(rounds=15))
    return hashed_pwd
