from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField,
                     BooleanField, SubmitField)
from flask_wtf.file import FileField
from wtforms.validators import (DataRequired, Email, EqualTo,
                                Length, ValidationError)
from wtforms.fields.html5 import EmailField

from .models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegisterNewUserForm(FlaskForm):
    name = StringField(validators=[DataRequired(),
                                   Length(min=3, max=100,
                                          message='Length is 3-100 characters')])
    email = EmailField(validators=[DataRequired('Please enter your email address'),
                                   Email('Please provide a valid email address'),
                                   Length(min=3, max=150,
                                          message='Length is 3-150 characters')])
    username = StringField(validators=[DataRequired(),
                                       Length(min=3, max=50,
                                              message="Length is 3-50 characters")])
    password = PasswordField(validators=[DataRequired(),
                                         Length(min=3, max=150,
                                                message='Length is 3-150 characters')])
    confirm_password = PasswordField(validators=[DataRequired(), EqualTo('password')])
    image = FileField(_name='Upload Image')
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken. '
                                  'Please choose a different Username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already used. '
                                  'Please choose a different Email.')


class UpdateAccountForm(FlaskForm):
    name = StringField(validators=[DataRequired(),
                                   Length(min=3, max=100,
                                          message='Length is 3-100 characters')])
    email = EmailField(validators=[DataRequired('Please enter your email address'),
                                   Email('Please provide a valid email address'),
                                   Length(min=3, max=150,
                                          message='Length is 3-150 characters')])
    username = StringField(validators=[DataRequired(),
                                       Length(min=3, max=50,
                                              message="Length is 3-50 characters")])
    image = FileField('Update Profile Picture')
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username is already taken. '
                                      'Please choose a different Username.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already used. '
                                      'Please choose a different Email.')


class RequestPasswordResetForm(FlaskForm):
    email = EmailField(validators=[DataRequired('Please enter your email address'),
                                   Email('Please provide a valid email address'),
                                   Length(min=3, max=150,
                                          message='Length is 3-150 characters')])
    submit = SubmitField('Submit')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('No account found with that email. Please register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')