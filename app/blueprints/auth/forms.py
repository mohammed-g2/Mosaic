from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, EmailField, BooleanField, SubmitField, TextAreaField,
    HiddenField)
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from app.models import User


class LoginForm(FlaskForm):
    email = EmailField('email', validators=[DataRequired(), Length(max=64), Email()])
    password = PasswordField('password', validators=[DataRequired(), Length(min=6)])
    remember_me = BooleanField('remember me?')
    submit = SubmitField('login')


class RegistrationForm(FlaskForm):
    email = EmailField('email', validators=[DataRequired(), Length(max=64), Email()])
    username = StringField('username', validators=[
        DataRequired(), 
        Length(min=3, max=64), 
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
            'Username can have only letters, numbers, dots or underscores')])
    password = PasswordField(
        'password', validators=[DataRequired(), EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('confirm password', validators=[DataRequired()])
    submit = SubmitField('Sign up')

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError('email already in use')
    
    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError('username already in use')


class ForgotPasswordForm(FlaskForm):
    email = EmailField('email', validators=[DataRequired(), Length(max=64), Email()])
    submit = SubmitField('Send')


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        'password', validators=[DataRequired(), EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('confirm password', validators=[DataRequired()])
    submit = SubmitField('Reset')


class ChangeEmailForm(FlaskForm):
    email = EmailField('email', validators=[DataRequired(), Length(max=64), Email()])
    submit = SubmitField('Send')

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError('email already in use')


class ChangeAccountInfoForm(FlaskForm):
    username = StringField('username', validators=[
        DataRequired(), 
        Length(min=3, max=64), 
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
            'Username can have only letters, numbers, dots or underscores')])
    location = StringField('location', validators=[Length(max=128)])
    about_me = TextAreaField('about me')
    submit = SubmitField('Save')


class DeleteAccountForm(FlaskForm):
    id = HiddenField('id', validators=[DataRequired()])
    submit = SubmitField('Delete')
