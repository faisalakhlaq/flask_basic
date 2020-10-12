from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flaskaap import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "person"
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    created = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime)
    image_url = db.Column(db.String())
    # Define the relationship to Role via UserRoles
    roles = db.relationship('Role', secondary='user_role')

    def __init__(self, name_, email_, username_, password_, created_=None,
                 last_updated_=None, image_url_=None):
        self.name = name_
        self.email = email_
        self.username = username_
        self.password = password_
        if created_:
            self.created = created_
        else:
            self.created = datetime.now()
        if last_updated_:
            self.last_updated = last_updated_
        if image_url_:
            self.image_url = image_url_

    def get_id(self):
        return self.user_id

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.user_id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


# Define the Role data-model
class Role(db.Model):
    __tablename__ = 'role'
    role_id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(255))


# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'user_role'
    user_role_id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('person.user_id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.role_id', ondelete='CASCADE'))
