from datetime import datetime, timezone
from threading import Thread
from markupsafe import Markup
from flask import Response, render_template, current_app
from flask_mail import Message
from app import mail


def utcnow() -> datetime:
    """Return a naive datetime object, a date without timezone"""
    return datetime.now(timezone.utc)


def render_partial(template: str, **data) -> str:
    """Extracts the data dict into the given template"""
    return Markup(render_template(template, **data))


def hx_redirect(url: str) -> Response:
    """Htmx redirect response"""
    resp = Response()
    resp.status_code = 302
    resp.headers['HX-Redirect'] = url
    return resp


def _send_async_mail(app, msg):
    with app.app_context():
        mail.send(msg)


def send_mail(to: str, subject: str, template: str, **kwargs) -> Thread:
    """Send async emails"""
    msg = Message()
    msg.recipients = [to]
    msg.subject = current_app.config['MAIL_SUBJECT_PREFIX'] + subject
    msg.sender = current_app.config['APP_ADMIN']
    msg.body = render_template(f'{template}.txt', **kwargs)
    msg.html = render_template(f'{template}.html', **kwargs)
    thr = Thread(
        target=_send_async_mail, 
        args=[current_app._get_current_object(), msg])
    thr.start()
    return thr
