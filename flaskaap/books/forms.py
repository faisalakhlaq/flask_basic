from abc import ABC

from flask_table import Table, Col, ButtonCol

from flask_wtf import FlaskForm
from wtforms import (IntegerField, StringField,
                     SelectField, SubmitField)
from wtforms.validators import Optional, DataRequired, ValidationError


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
