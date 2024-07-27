from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from config import options


db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please login to view this page.'
login_manager.login_message_category = 'warning'


def create_app(config_name: str) -> Flask:
    """Create and configure the application."""
    app = Flask(__name__)
    app.config.from_object(options[config_name])

    # initialize dependencies
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    # register blueprints
    from app.blueprints import blog_bp, auth_bp, admin_bp
    app.register_blueprint(blog_bp, url_prefix='/blog')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    app.add_url_rule('/', endpoint='blog.index')

    return app
