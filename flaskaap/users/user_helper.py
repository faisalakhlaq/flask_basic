from functools import wraps
from flask import url_for, flash, redirect, request
from flask_mail import Message
from flask_login import current_user

from .image_helper import identical_images
from flaskaap import mail


class UserHelper:
    def user_updated(self, form):
        """
        Check if the user has updated any info or profile picture. Check if
        the newly uploaded picture is the same as the previous one by comparing the images.
        :param form: form that contains the user account details which are to be updated
        :return: True if the user is updated
        """
        user_image = form.image.data
        # if user uploaded an image and previously had no image return True
        if user_image and not user_image.filename == '' and not current_user.image_url:
            return True

        if current_user.name == form.name.data \
                and current_user.email == form.email.data \
                and current_user.username == form.username.data \
                and not self.is_user_image_updated(user_image):
            return False
        return True

    @staticmethod
    def is_user_image_updated(new_image):
        """
        Check if the given image is None or empty or identical to current user image
        :param new_image:
        :return: True if the image has changed
        """
        if not new_image or new_image.filename == '' or identical_images(new_image):
            return False
        return True

    @staticmethod
    def send_password_reset_email(user):
        token = user.get_reset_token()
        msg = Message('Password Reset Request',
                      sender="ItsPythonTester@gmail.com",
                      recipients=[user.email])
        msg.body = f'''To reset your password please visit following link: 
    {url_for('users.reset_password', token=token, _external=True)}
    If you did not make this request then please discard this email.'''
        mail.send(msg)

    @staticmethod
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



