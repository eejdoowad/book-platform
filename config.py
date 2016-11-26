DEBUG = True

import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

DATABASE = 'bs'
USER = 'postgres'

CSRF_ENABLED = True
CSRF_SESSION_KEY = 'secret'
COOKIE_SECRET_KEY = 'secret'