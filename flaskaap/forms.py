from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, \
    BooleanField, SubmitField, SelectField
from flask_wtf.file import FileField
from wtforms.validators import DataRequired, Email, Length, \
    NumberRange, ValidationError, EqualTo, Optional
from wtforms.fields.html5 import EmailField

from flask_table import Table, Col, ButtonCol
from flask_login import current_user

from .models.user import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class BookStoreForm(FlaskForm):
    book_id = IntegerField('book_id', validators=[Optional()])
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    year = IntegerField('Year', validators=[Optional()])
    isbn = StringField('ISBN')
    search_by = SelectField(u'Search By', validators=[Optional()],
                            choices=[('0', 'Choose'), ('title', 'Title'),
                                     ('author', 'Author'), ('year', 'Year'),
                                     ('isbn', 'ISBN')])
    clear = SubmitField('Clear')
    add_new = SubmitField('Add New')
    search = SubmitField('Search')
    update = SubmitField('Update')
    delete = SubmitField(label='Delete')
    edit = SubmitField('Edit')
    view_all = SubmitField('View All')

    def validate_year(self, year):
        if year.data:
            try:
                int(year.data)
            except:
                raise ValidationError("Year must have an integer value")


class BookStoreTable(Table):
    """
    BookStoreTable is used to display books
    from database table on the page in a Table
    """
    classes = ['book-store-table']
    book_id = Col(name='book_id', show=False)
    title = Col(name='Title')
    author = Col(name='Author')
    year = Col(name='Year')
    isbn = Col(name='ISBN')
    edit = ButtonCol(name='EDIT', endpoint='edit_book')
    # edit = ButtonCol(name='EDIT', endpoint='edit_book',
    #                  url_kwargs=dict(book_id='book_id'))

    # def get_tr_attrs(self, item):
    #     if item:
    #         print("Clicked Item: ", str(item.title))
    #         return {'book': item}
    #     else:
    #         return {}


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
                        # , validators=[FileAllowed(app.config['ALLOWED_EXTENSIONS'])])
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


