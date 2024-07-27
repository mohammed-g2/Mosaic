import time
import hashlib
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from app import db, login_manager
from app.util import utcnow
from .role import Role, Permission


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(128), unique=True, index=True)
    location = db.Column(db.String(128))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=utcnow)
    last_seen = db.Column(db.DateTime(), default=utcnow)
    confirmed = db.Column(db.Boolean(), default=False)
    password_hash = db.Column(db.String(128))
    avatar_hash = db.Column(db.String(32))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    blog = db.relationship('Blog', uselist=False, backref='user')
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='user', lazy='dynamic')

    def __repr__(self) -> str:
        return f'<User {self.username}>'

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        if self.role is None:
            if self.email == current_app.config['APP_ADMIN']:
                self.role = Role.query.filter_by(name='administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
            db.session.add(self)
        if self.email and self.avatar_hash is None:
            self.avatar_hash = self.generate_md5_hash()
    
    @property
    def password(self):
        raise AttributeError('password is not a readable property')
    
    @password.setter
    def password(self, password: str):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password: str) -> bool:
        """Check if given password matches the stored password hash"""
        return check_password_hash(self.password_hash, password)
    
    def can(self, permission: int) -> bool:
        """Check if user have the given permission"""
        return self.role is not None and self.role.has_permission(permission)

    def is_admin(self) -> bool:
        """Check if user have administrator access"""
        return self.can(Permission.ADMIN)

    def generate_token(self, payload: dict, expires_in: int=600) -> str:
        """Generate jwt token using given payload"""
        payload.update({'exp': time.time() + expires_in})
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        return token
    
    def confirm(self, token: str) -> bool:
        """
        Set confirmed flag to True, payload format: {'confirm': user.id},
        return False if token is invalid or token doesn't contain the payload
        """
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms='HS256')
        except:
            return False
        
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True
    
    @staticmethod
    def reset_password(token: str) -> bool|str:
        """
        payload format: {'email': user.email},
        return False if token is invalid or token doesn't contain the payload
        """        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms='HS256')
        except:
            return False
        
        if data.get('email') is None:
            return False
        
        return data.get('email')

    def update_email(self, token: str) -> bool:
        """
        update user email, payload format: {'update-email': user.email},
        return False if token is invalid or token doesn't contain the payload
        """
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms='HS256')
        except:
            return False
        
        if data.get('update-email') is None:
            return False
        
        self.email = data.get('update-email')
        self.avatar_hash = self.generate_md5_hash()
        db.session.add(self)
        return True
    
    def ping(self):
        """Update user's last seen property"""
        self.last_seen = utcnow()
        db.session.add(self)
        db.session.commit()

    def generate_md5_hash(self) -> str:
        """Generate md5 hash using user email"""
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    def gravatar(self, size: int=100, default: str='identicon', rating: str='g') -> str:
        """Generate gravatar image link using user's email"""
        url = 'https://secure.gravatar.com/avatar'
        if self.avatar_hash:
            hash = self.avatar_hash
        else:
            hash = self.generate_md5_hash()
        return f'{url}/{hash}?s={size}&d={default}&r={rating}'


class AnonymousUser(AnonymousUserMixin):
    def can(self, permission: int) -> bool:
        return False
    
    def is_admin(self) -> bool:
        return False


login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(id :str) -> User:
    return User.query.get(int(id))
