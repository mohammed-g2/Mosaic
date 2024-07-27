from flask import request, redirect, url_for
from flask_login import current_user
from . import blog_bp as bp


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and\
                request.endpoint == 'blog.create_post':
            return redirect(url_for('auth.unconfirmed'))
        if current_user.blog is None and\
                request.endpoint == 'blog.create_post':
            return redirect(url_for('blog.create_blog'))
