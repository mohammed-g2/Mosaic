import os
import secrets
from werkzeug.utils import secure_filename
from flask import request, flash, url_for, current_app, redirect, send_from_directory
from flask_login import login_required, current_user
from app import db
from app.models import User, Permission, Post, Category, Blog, Comment
from app.decorators import template, permission_required
from app.util import hx_redirect
from . import blog_bp as bp
from .forms import CreatePostForm, CreateBlogForm, CreateCommentForm


@bp.route('/')
@template('blog/index.html')
def index():
    return dict()


@bp.route('/profile/<username>')
@template('blog/profile.html')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return dict(user=user)


@bp.route('/create-blog', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE)
@template('blog/create-blog.html')
def create_blog():
    if current_user.blog is not None:
        return redirect(url_for('blog.create_post'))
    form = CreateBlogForm()
    if form.validate_on_submit():
        blog = Blog()
        blog.name = form.name.data
        blog.user = current_user._get_current_object()
        db.session.add(blog)
        db.session.commit()
        flash('you can write posts now', category='success')
        return hx_redirect(url_for('blog.create_post'))
    return dict(form=form)


@bp.route('/<blog_name>')
@template('blog/view-blog.html')
def view_blog(blog_name):
    blog = Blog.query.filter_by(name=blog_name).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = blog.posts.order_by(Post.created_at.desc()).paginate(
        page=page,
        per_page=current_app.config['ENTRIES_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return dict(blog=blog, posts=posts, pagination=pagination)


def __post_img_url(form):
    if form.image.data is not None and form.image.data.filename:
        filename = (f'{current_user.id}_' +
                    f'{secrets.token_urlsafe(4)}_' +
                    f'{secure_filename(form.image.data.filename)}')
        img_url = url_for('static', filename=f'images/{filename}', _external=True)
        form.image.data.save(
            os.path.join(current_app.config['IMAGE_UPLOAD_PATH'], filename))
    else:
        img_url = None
    
    return img_url


@bp.route('/write', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE)
@template('blog/create-post.html')
def create_post():
    form = CreatePostForm(current_app.config['IMAGE_UPLOAD_EXTENSIONS'])
    if form.validate_on_submit():
        img_url = __post_img_url(form)
        if img_url is None:
            flash('error while handling image upload, image not saved', category='warning')
        post = Post()
        post.title = form.title.data
        post.body = form.body.data
        post.img_url = img_url
        post.author = current_user._get_current_object()
        post.blog = current_user.blog
        if form.category.data:
            post.category = Category.query.get(form.category.data)
        db.session.add(post)
        db.session.commit()
        flash('Post have been published', category='success')
        return hx_redirect(url_for('blog.view_post', id=post.id))
    else:
        if request.method == 'POST':
            flash('an error occurred while publishing the post', category='danger')
            for field_name, errors in form.errors.items():
                for msg in errors:
                    flash(f'{field_name} - {msg}', category='danger')

    return dict(form=form, endpoint=url_for('blog.create_post'))


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE)
@template('blog/create-post.html')
def edit_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and\
            not current_user.is_admin():
        return hx_redirect(url_for('blog.view_post', id=post.id))
    form = CreatePostForm(allowed_ext=current_app.config['IMAGE_UPLOAD_EXTENSIONS'], post=post)
    if form.validate_on_submit():
        img_url = __post_img_url(form)
        post.title = form.title.data
        post.body = form.body.data
        if img_url:
            post.img_url = img_url
        if form.category.data:
            post.category_id = form.category.data
        db.session.add(post)
        db.session.commit()
        flash('Post have been published', category='success')
        return hx_redirect(url_for('blog.view_post', id=post.id))
    else:
        if request.method == 'POST':
            flash('an error occurred while publishing the post', category='danger')
            for field_name, errors in form.errors.items():
                for msg in errors:
                    flash(f'{field_name} - {msg}', category='danger')
    
    form.title.data = post.title
    form.body.data = post.body
    form.category.data = post.category_id
    
    return dict(form=form, endpoint=url_for('blog.edit_post', id=post.id), img_url=post.img_url)


@bp.route('/post/<int:id>')
@template('blog/post.html')
def view_post(id):
    post = Post.query.get_or_404(id)
    form = CreateCommentForm()
    comments = post.comments.order_by(Comment.created_at.desc()).all()
    return dict(post=post, comment_form=form, comments=comments)


@bp.route('/delete-post', methods=['POST'])
@login_required
@permission_required(Permission.WRITE)
def delete_post():
    id = request.form.get('id', type=int)
    post = Post.query.get_or_404(id)
    blog_name = post.blog.name
    if not current_user.is_admin() and\
            current_user.id != post.author.id:
        return redirect(url_for('blog.view_post', id=id))
    db.session.delete(post)
    db.session.commit()
    flash('post has been deleted', category='warning')
    return redirect(url_for('blog.view_blog', blog_name=blog_name))


@bp.route('/create-comment/<int:id>', methods=['POST'])
@login_required
@permission_required(Permission.COMMENT)
def create_comment(id):
    form = CreateCommentForm(request.form)
    if form.validate_on_submit():
        comment = Comment()
        comment.body = form.body.data
        comment.user = current_user._get_current_object()
        comment.post_id = id
        db.session.add(comment)
        db.session.commit()
        flash('comment created', category='success')
    return redirect(url_for('blog.view_post', id=id))


@bp.route('/delete-comment/<int:id>', methods=['POST'])
@login_required
@permission_required(Permission.COMMENT)
def delete_comment(post_id):
    id = request.form.get('id', type=int)
    comment = Comment.query.get_or_404(id)
    if not current_user.is_admin() and\
            current_user.id != comment.user_id:
        return redirect(url_for('blog.index'))
    db.session.delete(comment)
    db.session.commit()
    flash('comment has been deleted', category='warning')
    return redirect(url_for('blog.view_post', id=post_id))
