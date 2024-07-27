from functools import wraps
from flask import request, render_template, Response, abort
from flask_login import current_user
from app.models import Permission


def template(temp_name: str=None, status_code: int=200):
    """return the template if request type is hypermedia, else return the full page"""
    def decorator(f):
        @wraps(f)
        def decorated_func(*args, **kwargs):
            # catch the data returned by the view
            data = f(*args, **kwargs)
            if type(data) == Response:
                return data
            if request.headers.get('HX-Request'):
                resp = render_template(temp_name, **data), status_code
            else:
                resp = render_template('_wrapper.html', partial=temp_name, data=data), status_code
            return resp
        return decorated_func
    return decorator


def permission_required(permission: int):
    """abort with 403 if current user doesn't have given permission"""
    def decorator(f):
        @wraps(f)
        def decorated_func(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_func
    return decorator


def admin_required(f):
    """abort with 403 if current user is not admin"""
    return permission_required(Permission.ADMIN)(f)
