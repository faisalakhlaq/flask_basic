from sqlalchemy import or_
from flask_login import login_required
from flask import (render_template, redirect,
                   request, url_for, flash, Blueprint)

from flaskaap import db
from .models import Book
from flaskaap.users.user_helper import UserHelper
from .forms import (BookStoreForm, BookStoreTable)

books_app = Blueprint('books_app', __name__)


@books_app.route('/book_store', methods=['GET', 'POST'])
def book_store():
    form = BookStoreForm()
    books = Book.query.all()
    table = BookStoreTable(books)
    if request.method == 'GET':
        return render_template('book_store.html', form=form, table=table)
    elif request.method == 'POST':
        t = form.title.data
        if request.form.get("search"):
            search_by = form.search_by.data
            if not t or len(t.strip()) == 0 or search_by.strip() == '0':
                flash("We cannot find out what you want to search! Please Try again")
                return redirect(url_for('books_app.book_store'))
            else:
                search_result = []
                if search_by == 'title':
                    search_result = Book.query.filter(Book.title.ilike(f'%{t}%'))
                elif search_by == 'author':
                    search_result = Book.query.filter(Book.author.ilike(f'%{t}%'))
                elif search_by == 'year':
                    search_result = Book.query.filter_by(year=t)
                elif search_by == 'isbn':
                    search_result = Book.query.filter_by(isbn=t)

                table = BookStoreTable(search_result)
                return render_template("book_store.html", form=form, table=table)

        return render_template("book_store.html", form=form, table=table)


@books_app.route('/book_admin', methods=['GET', 'POST'])
@login_required
@UserHelper.is_admin
def book_admin():
    page = request.args.get('page', 1, type=int)
    books_per_page = request.form.get('books_per_page', 10, type=int)
    books = Book.query.paginate(page=page, per_page=books_per_page)
    form = BookStoreForm()
    if request.form.get('edit'):
        book_id = request.form.get('edit')
        book = Book.query.get(book_id)
        form = BookStoreForm(book_id=book.book_id, title=book.title,
                             author=book.author, year=book.year, isbn=book.isbn)
    elif request.form.get('delete'):
        book_id = request.form.get('delete')
        delete_book = Book.query.get_or_404(book_id)
        db.session.delete(delete_book)
        db.session.commit()
        books = Book.query.paginate(page=page, per_page=books_per_page)
        flash("Book Deleted from the database!")
    elif request.form.get("add_new"):
        if form.validate_on_submit():
            t = form.title.data
            a = form.author.data
            y = form.year.data
            i = form.isbn.data
            book = Book(title_=t, author_=a, year_=y, isbn_=i)
            db.session.add(book)
            db.session.commit()
            flash("Book Added to the database!")
    elif request.form.get('update'):
        if form.validate_on_submit():
            update_book = Book.query.get(form.book_id.data)
            update_book.title = form.title.data
            update_book.author = form.author.data
            update_book.year = form.year.data
            update_book.isbn = form.isbn.data
            db.session.commit()
            flash('Book Updated')
    elif request.form.get('search'):
        # TODO let user search for multiple parameters in the
        #  same field e.g. Year= 2005, 2009, Author = Dietal, Kristian
        t = form.title.data
        a = form.author.data
        y = form.year.data
        i = form.isbn.data
        filter_by_expression = []
        if t and len(t.strip()) > 0:
            title_filter = (getattr(Book, 'title').ilike("%%%s%%" % t))
            filter_by_expression.append(title_filter)
        if a and len(a.strip()) > 0:
            author_filter = (getattr(Book, 'author').ilike("%%%s%%" % a))
            filter_by_expression.append(author_filter)
        if y and str(y).isnumeric():
            year_filter = (getattr(Book, 'year') == y)
            filter_by_expression.append(year_filter)
        if i and len(i) > 0:
            isbn_filter = (getattr(Book, 'isbn').ilike("%%%s%%" % i))
            filter_by_expression.append(isbn_filter)
        if len(filter_by_expression) > 0:
            print(filter_by_expression)
            books = db.session.query(Book).filter(or_(*filter_by_expression)).\
                paginate(page=page, per_page=books_per_page)
        else:
            flash("We cannot find out what you want to search! Please Try again")
    elif request.form.get('clear'):
        form = BookStoreForm(None)
    return render_template('book_admin_2.html', books=books, form=form)


@books_app.route('/edit_book',  methods=['GET', 'POST'])
@login_required
def edit_book():
    # TODO make a check that a specific user cannot add more
    #  then 5 books in a day. Only with the book_store_manager
    #  role or admin
    form = BookStoreForm()
    if request.method == 'POST':
        if request.form.get("delete"):
            flash('Please go to the book admin section to delete books!')
            pass
        elif request.form.get("add_new"):
            if form.validate_on_submit():
                t = form.title.data
                a = form.author.data
                y = form.year.data
                i = form.isbn.data
                book = Book(title_=t, author_=a, year_=y, isbn_=i)
                db.session.add(book)
                db.session.commit()
                flash("Book Added to the database!")
        elif request.form.get("view_all"):
            return redirect(url_for('books_app.book_store'))
        elif request.form.get('update'):
            flash('Please go to the book admin section to update books!')
            pass
    return render_template('book_admin.html', form=form)
