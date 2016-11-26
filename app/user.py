from app import cur

class User():
    
    def __init__(self, d):
        self.user_id = d.user_id
        self.username = d.username

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
    
    # My own custom method, not needed by flask-login
    def get(self, user_id):
        cur.execute("SELECT * FROM account WHERE id = (%s)", (user_id,))
        return User(cur.fetchone())


# returns User given unicode id
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
