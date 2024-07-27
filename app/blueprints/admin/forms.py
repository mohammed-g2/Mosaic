from flask_wtf import FlaskForm
from wtforms import (
    StringField, EmailField, TextAreaField, BooleanField, SelectField)
from wtforms.validators import DataRequired, Length, Regexp, Email, ValidationError
from app.models import User, Role


class EditAccountForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
            'Usernames must have only letters, numbers, dots or '
            'underscores')])
    email = EmailField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    location = StringField('Location', validators=[Length(max=64)])
    about_me = TextAreaField('About me')
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)

    def __init__(self, user, *args, **kwargs):
        super(EditAccountForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.all()]
        self.user = user
    
    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('email already in use')
    
    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('username already in use')
    