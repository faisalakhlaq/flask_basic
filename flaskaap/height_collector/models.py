from flaskaap import db


class Height_Data(db.Model):
    __tablename__ = "data"
    id = db.Column(db.Integer, primary_key=True)
    name_ = db.Column(db.String(70))
    email_ = db.Column(db.String(120), unique=True)
    height_ = db.Column(db.Integer)

    def __init__(self, name, email, height):
        self.name_ = name
        self.email_ = email
        self.height_ = height

