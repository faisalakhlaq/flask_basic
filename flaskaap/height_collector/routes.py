from flask import Blueprint, redirect, request, render_template, url_for

from flaskaap import db
from .forms import HeightDataForm
from .models import Height_Data
from .email_sender import EmailSender

height_collector = Blueprint('height_collector', __name__)


@height_collector.route('/height', methods=['GET', 'POST'])
def height_data():
    form = HeightDataForm()
    if request.method == 'GET':
        return render_template('height.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            n = form.name.data
            e = form.email.data
            h = form.height.data
            if db.session.query(Height_Data).filter(Height_Data.email_ == e).count() == 0:
                data = Height_Data(name=n, email=e, height=h)
                db.session.add(data)
                db.session.commit()
                EmailSender().send_height_data_email(name=n, email=e, height=h)
                return redirect(url_for('height_collector.height'))
            else:
                # TODO make the error disappear after 20 seconds
                error = "It seems this email is already used"
                return render_template('height.html', form=form, error_message=error)
        return render_template('height.html', form=form)
