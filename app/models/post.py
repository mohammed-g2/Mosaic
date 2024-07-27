import bleach
from markdown import markdown
from app import db
from app.util import utcnow


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), unique=True, index=True)
    body = db.Column(db.Text())
    body_html = db.Column(db.Text())
    created_at = db.Column(db.DateTime(), index=True, default=utcnow)
    img_url = db.Column(db.String())
    blog_id = db.Column(db.Integer, db.ForeignKey('blogs.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    def __repr__(self):
        return f'<Post {self.id}>'

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = [
            'a', 'b', 'p', 'i', 'ul', 'li', 'ol', 'em'
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'pre',
            'abbr', 'acronym', 'blockquote', 'code', 'strong']
        target.body_html = bleach.linkify(bleach.clean(
            text=markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))


db.event.listen(Post.body, 'set', Post.on_changed_body)
