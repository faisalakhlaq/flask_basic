from flask_login import current_user
from flaskaap.image_helper import identical_images


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

    def is_user_image_updated(self, new_image):
        """
        Check if the given image is None or empty or identical to current user image
        :param new_image:
        :return: True if the image has changed
        """
        if not new_image or new_image.filename == '' or identical_images(new_image):
            return False
        return True