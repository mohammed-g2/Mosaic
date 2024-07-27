from flask import request, url_for, flash, redirect
from flask_login import login_required, login_user, logout_user, current_user
from app import db
from app.models import User
from app.decorators import template
from app.util import hx_redirect, send_mail
from . import auth_bp as bp
from .forms import (
    LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm, ChangeEmailForm,
    ChangeAccountInfoForm, DeleteAccountForm)


@bp.route('/login', methods=['GET', 'POST'])
@template('auth/login.html')
def login():
    if current_user.is_authenticated:
        return hx_redirect(url_for('blog.index'))
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('blog.index')
            return hx_redirect(next)
        flash('Invalid username or password.', category='warning')
    return dict(form=form)


@bp.route('/register', methods=['GET', 'POST'])
@template('auth/register.html')
def register():
    if current_user.is_authenticated:
        return hx_redirect(url_for('blog.index'))
    form = RegistrationForm(request.form)
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        send_mail(
            user.email, 
            'Confirm your account', 
            'auth/email/confirm',
            user=user,
            token=user.generate_token({'confirm': user.id}))
        flash('a confirmation email has been sent, please check your inbox', category='success')
        return hx_redirect(url_for('auth.login'))
    return dict(form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out.', category='success')
    return hx_redirect(url_for('blog.index'))


@bp.route('/settings')
@login_required
@template('auth/settings.html')
def settings():
    change_account_info_form = ChangeAccountInfoForm()
    change_account_info_form.username.data = current_user.username
    change_account_info_form.location.data = current_user.location
    change_account_info_form.about_me.data = current_user.about_me
    change_email_form = ChangeEmailForm()
    change_email_form.email.data = current_user.email
    reset_password_form = ResetPasswordForm()
    delete_account_form = DeleteAccountForm()
    delete_account_form.id.data = current_user.id

    return dict(
        change_account_info_form=change_account_info_form,
        change_email_form=change_email_form,
        reset_password_form=reset_password_form,
        delete_account_form=delete_account_form)


@bp.route('/change-account-info', methods=['POST'])
@login_required
def change_account_info():
    form = ChangeAccountInfoForm(request.form)
    if form.validate():
        user = current_user._get_current_object()
        if User.query.filter_by(username=form.username.data).first()\
            and form.username.data != user.username:
            flash('please choose a different username', category='warning')
            return hx_redirect(url_for('auth.settings'))
        user.username = form.username.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('account info updated', category='success')
    else:
        flash('an error occurred while updating your info', category='warning')
    return hx_redirect(url_for('auth.settings'))


@bp.route('/change-email', methods=['POST'])
@login_required
def change_email():
    form = ChangeEmailForm(request.form)
    if form.validate():
        send_mail(
            current_user.email,
            'Update your email address',
            'auth/email/update-email',
            user=current_user,
            token=current_user.generate_token({'update-email': form.email.data}))
        flash('an email have been sent to your account to confirm the changes', category='success')
    else:
        flash('an error occurred while updating your info', category='warning')
    return hx_redirect(url_for('auth.settings'))


@bp.route('/update-email/<token>')
@login_required
def update_email(token):
    if current_user.update_email(token):
        db.session.commit()
        flash('your email address have been updated', category='success')
    else:
        flash('an error occurred while updating your info, link might be invalid or expired', category='warning')
    return redirect(url_for('auth.settings'))


@bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    form = ResetPasswordForm(request.form)
    if form.validate():
        user = current_user._get_current_object()
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        flash('password has been updated', category='success')
    else:
        flash('an error occurred while updating your info, password is invalid', category='warning')
    return redirect(url_for('auth.settings'))


@bp.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    form = DeleteAccountForm(request.form)
    if form.validate():
        user = current_user._get_current_object()
        db.session.delete(user)
        db.session.commit()
        flash('account has been deleted', category='warning')
        return redirect(url_for('blog.index'))
    else:
        flash('an error occurred while updating your info', category='warning')
        return redirect(url_for('auth.settings'))


@bp.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('blog.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('you have confirmed your account', category='success')
    else:
        flash('confirmation link is invalid or expired')
    return redirect(url_for('blog.index'))


@bp.route('/unconfirmed')
@login_required
@template('auth/unconfirmed.html')
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for('blog.index'))
    return dict()


@bp.route('/resend-confirmation')
@login_required
def resend_confirmation():
    send_mail(
        current_user.email,
        'Confirm your account', 
        'auth/email/confirm',
        user=current_user,
        token=current_user.generate_token({'confirm': current_user.id}))
    flash('a confirmation email has been sent, please check your inbox', category='success')
    return redirect(url_for('blog.index'))


@bp.route('/forgot-password', methods=['GET', 'POST'])
@template('auth/forgot-password.html')
def forgot_password():
    form = ForgotPasswordForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('we could not find the given email in our database', category='warning')
            return dict(form=form)
        send_mail(
            user.email,
            'Reset your password',
            'auth/email/reset-password',
            user=user,
            token=user.generate_token({'email': user.email}))
        flash('please check your inbox for resitting password email', category='success')
    return dict(form=form)


@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
@template('auth/reset-password.html')
def reset_password(token):
    form = ResetPasswordForm(request.form)
    if form.validate_on_submit():
        email = User.reset_password(token)
        print(email)
        if email:
            user = User.query.filter_by(email=email).first()
            if user:
                user.password = form.password.data
                db.session.add(user)
                db.session.commit()
                flash('password has been updated, you can login now', category='success')
                return hx_redirect(url_for('auth.login'))
        flash('an error occurred while handling your request, your link might have expired', category='danger')
    return dict(form=form, token=token)
