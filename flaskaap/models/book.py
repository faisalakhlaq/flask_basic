from flaskaap import db


class Book(db.Model):
    __tablename__ = "book"
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer)
    isbn = db.Column(db.String(200))

    def __init__(self, title_, author_, year_, isbn_):
        self.title = title_
        self.author = author_
        self.year = year_
        self.isbn = isbn_
