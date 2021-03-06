from flask import Flask, render_template
from flask_login import LoginManager
import psycopg2, psycopg2.extras

app = Flask(__name__)
app.config.from_object('config')

DEC2FLOAT = psycopg2.extensions.new_type(
    psycopg2.extensions.DECIMAL.values,
    'DEC2FLOAT',
    lambda value, curs: float(value) if value is not None else None)
psycopg2.extensions.register_type(DEC2FLOAT)

conn = psycopg2.connect("dbname=%s user=%s" % (app.config['DATABASE'], app.config['USER']))
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from app import views