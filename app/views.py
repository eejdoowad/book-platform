from app import app
from flask import render_template, flash, redirect, session, url_for, request, g, jsonify, abort
from flask_login import login_required, login_user, logout_user, current_user
from sys import stderr
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from app.forms import RegistrationForm, LoginForm
from app.db import register_user, get_all_users, get_account
from app.user import User



####################################
# General Routes
####################################

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    account = get_account(username=current_user.username)
    return render_template('profile.html', account=account)

@app.route('/admin', methods=['GET'])
def admin():
    return render_template('admin/index.html')

@app.route('/admin/user', methods=['GET'])
def admin_user():
    users = get_all_users()
    return render_template('admin/user.html', users=users)



####################################
# Authentication Routes
####################################

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(get_account(username=form.username.data))
        login_user(user)
        flash('Logged in successfully.')
        next = request.args.get('next')
        return redirect(next or url_for('index'))

    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        register_user(form)
        flash('Thanks for registering')
        return redirect(url_for('login'))
    return render_template('auth/register.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')



####################################
# 404 Route
####################################

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404