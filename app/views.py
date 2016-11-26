from app import app
from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
from flask.ext.login import login_required
from sys import stderr

from app import cur
import json
    
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.route('/', methods=['GET', 'POST'])
def index():
    users = []
    try:
        cur.execute("SELECT * FROM account")
        users = cur.fetchall()
    except Exception as e:
        print(e, file=stderr)
    return render_template('index.html', users=users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # form = LoginForm()
    # if form.validate_on_submit():
    #     login_user(user)
    #     flask.flash('Logged in successfully.')
    #     next = flask.request.args.get('next')
    #     if not is_safe_url(next):
    #         return flask.abort(400)
    #     return flask.redirect(next or flask.url_for('index'))
    return render_template('login.html') # , form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(somewhere)