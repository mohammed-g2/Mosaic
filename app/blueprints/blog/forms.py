import imghdr
from werkzeug.datastructures.file_storage import FileStorage
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError, Regexp
from flask_wtf.file import FileAllowed
from app.models import Post, Category, Blog


class CreateBlogForm(FlaskForm):
    name = StringField('title', validators=[
        DataRequired(), 
        Length(max=32),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
            'Blog name can have only letters, numbers, dots or underscores')])
    submit = SubmitField('create')

    def validate_name(self, field):
        if Blog.query.filter_by(name=field.data).first():
            raise ValidationError('blog name already in use')


class CreatePostForm(FlaskForm):
    title = StringField('title', validators=[DataRequired(), Length(max=128)])
    body = TextAreaField('body')
    image = FileField('image')
    category = SelectField('category', coerce=int, validate_choice=False)
    submit = SubmitField('publish')

    def __init__(self, allowed_ext: list, post=None, *args, **kwargs):
        super(CreatePostForm, self).__init__(*args, **kwargs)
        self.category.choices = [(c.id, c.name) for c in Category.query.all()]
        self.allowed_ext = allowed_ext
        self.post = post
        self.image.validators = [FileAllowed(allowed_ext, 'Unsupported image format')]
    
    def validate_title(self, field):
        if self.post is None:
            if Post.query.filter_by(title=field.data).first():
                raise ValidationError('title already in use')
        else:
            if self.post.title != field.data:
                if Post.query.filter_by(title=field.data).first():
                    raise ValidationError('title already in use')
                    
    
    def validate_image(self, field):
        """
        identify the format of given image stream, return None if format
        is unrecognized, else return format as file extension
        """
        if type(field.data) == FileStorage:
            header = field.data.stream.read(512)
            field.data.stream.seek(0)
            format = imghdr.what(None, header)
            if field.data.filename:
                if not format or format not in self.allowed_ext:
                    raise ValidationError('unsupported image format')


class CreateCommentForm(FlaskForm):
    body = TextAreaField('Body', validators=[DataRequired()])
    submit = SubmitField('Comment')
