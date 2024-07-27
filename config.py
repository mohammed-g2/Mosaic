import os
import secrets

basedir = os.path.abspath(os.path.dirname(__name__))


class Config():
    # App
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    WTF_CSRF_SECRET_KEY = secrets.token_urlsafe(16)
    APP_ADMIN = os.environ.get('APP_ADMIN')
    APP_ADMIN_PASSWORD = os.environ.get('APP_ADMIN_PASSWORD')
    ENTRIES_PER_PAGE = int(os.environ.get('ENTRIES_PER_PAGE')) or 6

    # Image upload
    MAX_CONTENT_LENGTH = 1024 * 1024  # maximum request size: 1 MB
    IMAGE_UPLOAD_EXTENSIONS =  ['jpg', 'jpe', 'jpeg', 'png', 'webp', 'gif']
    IMAGE_UPLOAD_PATH = os.path.join(basedir, 'app', 'static', 'images')

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS').lower() in ['true', '1']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL').lower() in ['true', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SUBJECT_PREFIX = os.environ.get('MAIL_SUBJECT_PREFIX')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEVELOPMENT_DB') or \
        f'sqlite:///{os.path.join(basedir, 'data', 'dev-data.sqlite')}'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TESTING_DB') or 'sqlite://'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('PRODUCTION_DB') or \
        f'sqlite:///{os.path.join(basedir, 'data', 'data.sqlite')}'


options = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}