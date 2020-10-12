from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length, NumberRange, Email


class HeightDataForm(FlaskForm):
    name_error_message = "Please provide name between 3-45 characters long"
    name = StringField('Name', validators=[DataRequired(name_error_message),
                                           Length(min=3, max=45, message=name_error_message)])
    height_error_msg = 'Please enter you height between 80-250'
    height = IntegerField('Height', validators=[DataRequired(height_error_msg),
                                                NumberRange(min=80, max=250,
                                                            message=height_error_msg)])
    email = EmailField('Email', validators=[DataRequired('Please enter your email address'),
                                            Email('Please provide a valid email address')])
    submit = SubmitField('Send')
