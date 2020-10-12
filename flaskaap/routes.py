from datetime import datetime

from sqlalchemy import or_
from flask import render_template, redirect, request, url_for, flash
from flask_login import (login_user, current_user,
                         logout_user, login_required)
from functools import wraps
from flask_mail import Message

from flaskaap import db, app, bcrypt, mail
from flaskaap.image_helper import save_user_image, delete_image, identical_images
from flaskaap.models.height_data import Data
from flaskaap.models.user import User
from flaskaap.models.book import Book
from flaskaap.forms import (RegisterNewUserForm, LoginForm, HeightDataForm,
                            UpdateAccountForm, BookStoreForm, BookStoreTable,
                            RequestPasswordResetForm, ResetPasswordForm)
from flaskaap.email_sender import EmailSender
from flaskaap.helpers.user_helper import UserHelper


def is_admin(f):
    """Decorator checks if the user has a role of admin"""
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'admin' in [role.name for role in current_user.roles]:
            return f(*args, **kwargs)
        else:
            flash("Sorry, Admin Rights Required!")
            return redirect(request.referrer)
    return wrap


@app.route('/register_new_user', methods=['GET', 'POST'])
def register_new_user():
    if current_user.is_authenticated:
        flash('Please logout to register as a new user')
        return redirect(request.referrer)
    form = RegisterNewUserForm()
    if request.method == 'GET':
        return render_template('register.html', form=form)
    if request.method == 'POST':
        if form.validate_on_submit():
            n = form.name.data
            e = form.email.data
            u = form.username.data
            p = form.password.data
            try:
                image_url = save_user_image(form.image.data)
                hashed_password = bcrypt.generate_password_hash(p).decode('utf-8')
                data = User(name_=n, email_=e, username_=u,
                            password_=hashed_password, image_url_=image_url)
                db.session.add(data)
                db.session.commit()
            except TypeError as error:
                return render_template('register.html', form=form, error_message=error)
            # TODO display a message for 5 sec
            flash("User Created")
            return redirect(url_for('home'))
        else:
            return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged-in')
        return redirect(request.referrer)
    form = LoginForm()
    if request.method == 'GET':
        return render_template('login.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember_me.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                error = 'Please check your username and password and try again'
                return render_template('login.html', form=form, error_message=error)
        return render_template('login.html', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/height', methods=['GET', 'POST'])
def height_data():
    form = HeightDataForm()
    if request.method == 'GET':
        return render_template('height.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            n = form.name.data
            e = form.email.data
            h = form.height.data
            if db.session.query(Data).filter(Data.email_ == e).count() == 0:
                data = Data(name=n, email=e, height=h)
                db.session.add(data)
                db.session.commit()
                EmailSender().send_height_data_email(name=n, email=e, height=h)
                return redirect(url_for('height'))
            else:
                # FIXME make the error disappear after 20 seconds
                error = "It seems this email is already used"
                return render_template('height.html', form=form, error_message=error)
        return render_template('height.html', form=form)


@app.route('/book_store', methods=['GET', 'POST'])
def book_store():
    form = BookStoreForm()
    books = Book.query.all()
    table = BookStoreTable(books)
    if request.method == 'GET':
        return render_template("book_store.html", form=form, table=table)
    elif request.method == 'POST':
        t = form.title.data
        if request.form.get("search"):
            search_by = form.search_by.data
            if not t or len(t.strip()) == 0 or search_by.strip() == '0':
                flash("We cannot find out what you want to search! Please Try again")
                return redirect(url_for('book_store'))
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


@app.route('/book_admin', methods=['GET', 'POST'])
@login_required
@is_admin
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
            # books = Book.query.paginate(page=page, per_page=books_per_page)
            books = db.session.query(Book).filter(or_(*filter_by_expression)).\
                paginate(page=page, per_page=books_per_page)
        else:
            flash("We cannot find out what you want to search! Please Try again")
    elif request.form.get('clear'):
        form = BookStoreForm(None)

    return render_template('book_admin_2.html', books=books, form=form)


# @app.route('/edit_book<int:book_id>',  methods=['GET', 'POST'])
@app.route('/edit_book',  methods=['GET', 'POST'])
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
            return redirect(url_for('book_store'))
        elif request.form.get('update'):
            flash('Please go to the book admin section to update books!')
            pass
    return render_template('book_admin.html', form=form)


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        try:
            # Check if data is not changed and the image is
            #  also the same then do not change anything
            if not UserHelper().user_updated(form=form):
                flash("User is not updated because nothing has changed!")
                return redirect(url_for('account'))
            # if the user has updated the image check validity
            if form.image.data:
                if not form.image.data.filename == '' and not identical_images(form.image.data):
                    picture_url = save_user_image(form.image.data)
                    # if a new image is saved, delete the previous one
                    if current_user.image_url:
                        delete_image(current_user.image_url)
                    current_user.image_url = picture_url
            current_user.name = form.name.data
            current_user.email = form.email.data
            current_user.username = form.username.data
            current_user.last_updated = datetime.now()
            db.session.commit()
            flash('Account Updated!', 'success')
            return redirect(url_for('account'))
        except TypeError as error:
            return render_template('user_account.html', form=form, error_message=error)
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = None
    if current_user.image_url:
        image_file = url_for('static', filename='images/' + current_user.image_url)
    return render_template('user_account.html', form=form, image_file=image_file)


# TODO change the name of error page
@app.errorhandler(404)
def error_page(e):
    print(e)
    return render_template("404.html", error_message=e)


@app.route('/')
@app.route('/home')
def home():
    image_file = url_for('static', filename='images/cc9da77274fe3f5111.png')
    return render_template("home.html", image_file=image_file)


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact')
def contact():
    return render_template("contact.html")


@app.route('/projects')
def projects():
    return render_template("projects.html")


def send_password_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender="ItsPythonTester@gmail.com",
                  recipients=[user.email])
    msg.body = f'''To reset your password please visit following link: 
{url_for('reset_password', token=token, _external=True)}
If you did not make this request then please discard this email.'''
    mail.send(msg)


@app.route('/request_password_reset', methods=['GET', 'POST'])
def request_password_reset():
    if current_user.is_authenticated:
        flash("Please logout and then try to reset the password")
        return redirect(request.referrer)
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_password_reset_email(user=user)
        return redirect(url_for('login'))
    return render_template("reset_password_request.html", form=form)


@app.route('/reset_password<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        flash("Please logout and then try to reset the password")
        return redirect(request.referrer)
    user = User.verify_reset_token(token=token)
    if not user:
        flash("Sorry your token is invalid or expired!")
        return redirect(url_for('reset_password'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template("reset_password.html", form=form)
