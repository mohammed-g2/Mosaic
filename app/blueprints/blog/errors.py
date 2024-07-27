from app.decorators import template
from . import blog_bp as bp


@bp.app_errorhandler(404)
@template('errors/404.html', 404)
def page_not_found(e):
    return dict()


@bp.app_errorhandler(500)
@template('errors/500.html', 500)
def internal_server_error(e):
    return dict()


@bp.app_errorhandler(403)
@template('errors/403.html', 403)
def forbidden(e):
    return dict()
