from flask import Blueprint, render_template, url_for

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    image_file = url_for('static', filename='images/cc9da77274fe3f5111.png')
    return render_template("home.html", image_file=image_file)


@main.route('/about')
def about():
    return render_template("about.html")


@main.route('/contact')
def contact():
    return render_template("contact.html")


@main.route('/projects')
def projects():
    return render_template("projects.html")
