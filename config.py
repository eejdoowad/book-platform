DEBUG = True

import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

DATABASE = 'bs'
USER = 'postgres'

ADMIN_SECRET = 'admin'

CSRF_ENABLED = True
CSRF_SESSION_KEY = 'secret'
COOKIE_SECRET_KEY = 'secret'
SECRET_KEY = 'secret'