from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, SelectMultipleField, TextAreaField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError
from app.db import key_available, get_user
from app import app

####################################
# Custom Validators
####################################

# My custom Validator for checking to see that a unique key in the database isn't already taken
def KeyAvailable(table, column):
    def _KeyAvailable(form, field):
        if not key_available(table, column, field.data):
            raise ValidationError("'%s' is unavailable" % (field.data))
    return _KeyAvailable

def admin_check(form, field):
    if field.data != '' and field.data != app.config['ADMIN_SECRET']:
        raise ValidationError('Incorrect admin secret key')

def authenticate_user(form, field):
    user = get_user(form.username.data)
    if user == None or user['password'] != form.password.data:
        raise ValidationError('Invalid username or password')


####################################
# Authentication Forms
####################################

class RegistrationForm(FlaskForm):
    username = StringField('Username', [
        Length(min=1, max=25),
        KeyAvailable('account', 'username')
    ])
    email = StringField('Email Address', [
        Length(min=3, max=35),
        KeyAvailable('account', 'email')
    ])
    password = PasswordField('New Password', [
        Length(min=3),
        EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    first_name = StringField('First Name', [Length(min=1)])
    last_name = StringField('Last Name', [Length(min=1)])
    admin = PasswordField('Admin Secret', [admin_check])

class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('New Password', [
        authenticate_user
    ])

####################################
# Book Forms
####################################

class CreateBookForm(FlaskForm):
    title = StringField('Title', [
        Length(min=1, max=30)
    ])
    summary = TextAreaField('Summary')
    # choices generated dynamically in view
    genres = SelectMultipleField('Genre')

class EditBookForm(FlaskForm):
    title = StringField('Title', [
        Length(min=1, max=30)
    ])
    summary = TextAreaField('Summary')
    # choices generated dynamically in view
    genres = SelectMultipleField('Genre')



####################################
# Chapter Forms
####################################

class CreateChapterForm(FlaskForm):
    title = StringField('Chapter Title', [
        Length(min=1, max=30)
    ])
    content = TextAreaField('Content')
    status = BooleanField('Publish (if not selected saves as draft)')

class EditChapterForm(FlaskForm):
    title = StringField('Chapter Title', [
        Length(min=1, max=30)
    ])
    content = TextAreaField('Content')
    status = BooleanField('Publish (if not selected saves as draft)')



####################################
# Comment Forms
####################################

class CommentForm(FlaskForm):
    comment = TextAreaField('Comment', [
        Length(min=1)
    ])