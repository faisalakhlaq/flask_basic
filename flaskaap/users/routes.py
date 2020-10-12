from datetime import datetime
from flask import (render_template, redirect,
                   request, url_for, flash, Blueprint)
from flask_login import (current_user, login_user,
                         logout_user, login_required)
from flaskaap import db, bcrypt
from .models import User
from .image_helper import (save_user_image,
                           identical_images, delete_image)
from .forms import (RegisterNewUserForm, LoginForm,
                    UpdateAccountForm, ResetPasswordForm,
                    RequestPasswordResetForm)
from .user_helper import UserHelper

users = Blueprint('users', __name__)


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        try:
            # Check if data is not changed and the image is
            #  also the same then do not change anything
            if not UserHelper().user_updated(form=form):
                flash("User is not updated because nothing has changed!")
                return redirect(url_for('users.account'))
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
            return redirect(url_for('users.account'))
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


@users.route('/register_new_user', methods=['GET', 'POST'])
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
            return redirect(url_for('main.home'))
        else:
            return render_template('register.html', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged-in')
        return redirect(request.referrer)
    form = LoginForm()
    if request.method == 'GET':
        return render_template('login.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            user_to_login = User.query.filter_by(username=form.username.data).first()
            if user_to_login and bcrypt.check_password_hash(user_to_login.password, form.password.data):
                login_user(user_to_login, remember=form.remember_me.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.home'))
            else:
                error = 'Please check your username and password and try again'
                return render_template('login.html', form=form, error_message=error)
        return render_template('login.html', form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/request_password_reset', methods=['GET', 'POST'])
def request_password_reset():
    if current_user.is_authenticated:
        flash("Please logout and then try to reset the password")
        return redirect(request.referrer)
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        reset_pwd_user = User.query.filter_by(email=form.email.data).first()
        UserHelper.send_password_reset_email(user=reset_pwd_user)
        return redirect(url_for('users.login'))
    return render_template("reset_password_request.html", form=form)


@users.route('/reset_password<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        flash("Please logout and then try to reset the password")
        return redirect(request.referrer)
    reset_user_pwd = User.verify_reset_token(token=token)
    if not reset_user_pwd:
        flash("Sorry your token is invalid or expired!")
        return redirect(url_for('users.reset_password'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        reset_user_pwd.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('main.login'))
    return render_template("reset_password.html", form=form)
