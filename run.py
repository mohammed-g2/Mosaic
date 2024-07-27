import os
from dotenv import load_dotenv
from flask_migrate import Migrate
from app import create_app, db
from app.models import User, Role, Permission, Blog, Post, Category, Comment
from app.cli import register_cli
from app.util import render_partial
from config import basedir


load_dotenv(os.path.join(basedir, '.env'))

app = create_app(os.environ.get('APP_CONFIG', 'default'))
migrate = Migrate(app, db)

register_cli(app)


@app.shell_context_processor
def shell_context():
    return dict(
        db=db, User=User, Role=Role, Permission=Permission, Blog=Blog, Post=Post,
        Category=Category, Comment=Comment)


@app.context_processor
def template_context():
    return dict(render_partial=render_partial, Permission=Permission)
