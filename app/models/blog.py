from app import db


class Blog(db.Model):
    __tablename__ = 'blogs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    posts = db.relationship('Post', backref='blog', lazy='dynamic')

    def __repr__(self):
        return f'<Blog {self.name}>'
