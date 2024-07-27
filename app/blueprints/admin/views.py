from flask import request, url_for, flash
from flask_login import login_required
from app import db
from app.decorators import template, admin_required
from app.util import hx_redirect
from app.models import User, Role
from . import admin_bp as bp
from .forms import EditAccountForm


@bp.route('/edit-user-account/<username>', methods=['GET', 'POST'])
@login_required
@admin_required
@template('admin/edit-user-account.html')
def edit_user_account(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = EditAccountForm(user, request.form)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('data has been updated', category='success')
        return hx_redirect(url_for('blog.profile', username=username))
    form.username.data = user.username
    form.email.data = user.email
    form.location.data = user.location
    form.about_me.data = user.about_me
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id

    return dict(form=form, user=user)
