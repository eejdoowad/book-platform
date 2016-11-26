from app import cur
from app import login_manager
from app.db import get_account



####################################
# User class required by flask-login
####################################

class User():
    
    def __init__(self, account):
        self.id = account['user_id']
        self.username = account['username']
        self.is_admin = account['is_admin']

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    # returns User id as a unicode string
    def get_id(self):
        return str(self.id)

# returns User given unicode id
@login_manager.user_loader
def load_user(user_id):
    return User(get_account(user_id=user_id))