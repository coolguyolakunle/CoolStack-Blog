from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from app import db
from app.models import User, Post, Like, Comment
from app.forms import SignupForm, LoginForm, PostForm, EditProfileForm, CommentForm
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

bp = Blueprint('main', __name__)

UPLOAD_FOLDER = 'app/static/uploads'


# ---------------- LANDING PAGE ----------------
@bp.route('/')
def landing():
    login_form = LoginForm()
    signup_form = SignupForm()
    return render_template(
        'landing.html', 
        login_form=login_form,
        signup_form=signup_form,
        title="Welcome"
    )


# ---------------- HOME ----------------
@bp.route('/home')
@login_required
def home():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('home.html', posts=posts)


# ---------------- SIGNUP ----------------
@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    # Handle AJAX request (for modal)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('signup_form.html', form=form), 200 

    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.email == form.email.data) | (User.username == form.username.data)
        ).first()
        if existing_user:
            flash('Username or Email already registered. Please log in instead.', 'warning')
            return redirect(url_for('main.login'))

        hashed_pw = generate_password_hash(form.password.data)
        user = User(
            fullname=form.fullname.data,
            username=form.username.data,
            email=form.email.data,
            dob=form.dob.data,
            gender=form.gender.data,
            phone_number=form.phone_number.data,
            password=hashed_pw
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        print("Form errors:", form.errors)

    return render_template('signup.html', form=form)


# ---------------- LOGIN ----------------
@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    # Handle AJAX request (for modal)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('login_form.html', form=form), 200

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f"Welcome back, {user.username}!", 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html', form=form)


# ---------------- LOGOUT ----------------
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.landing'))


# ---------------- CREATE POST ----------------
@bp.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()

    if request.method == 'POST':
        print("POST received")
        print("Form data:", request.form)
        print("Files:", request.files)
        print("Form errors before validate:", form.errors)

    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            user_id=current_user.id
        )

        # Handle uploads properly
        upload_folder = os.path.join(current_app.root_path, 'static/uploads')
        os.makedirs(upload_folder, exist_ok=True)

        if form.image.data:
            image_file = form.image.data
            filename = secure_filename(image_file.filename)

            image_folder = os.path.join(current_app.root_path, 'static/uploads/post_images')
            os.makedirs(image_folder, exist_ok=True)

            filepath = os.path.join(image_folder, filename)
            if os.path.exists(filepath):
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{str(len(os.listdir(image_folder)))}{ext}"
                filepath = os.path.join(image_folder, filename)

            image_file.save(filepath)
            post.image = filename


        if form.video.data:
            video_file = form.video.data
            filename = secure_filename(video_file.filename)
            video_path = os.path.join(upload_folder, filename)
            video_file.save(video_path)
            post.video = filename

        db.session.add(post)
        db.session.commit()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": True, "message": "Post created successfully!"})

        flash("Post created successfully!", "success")
        return redirect(url_for('main.home'))

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"success": False, "message": "Form validation failed.", "errors": form.errors})

    return render_template('create_post.html', form=form)




@bp.route('/category/<string:category_name>')
def category_posts(category_name):
    posts = Post.query.filter_by(category=category_name).order_by(Post.date_posted.desc()).all()
    return render_template('category_posts.html', posts=posts, category_name=category_name)


@bp.route('/category/<string:category_name>')
def category_page(category_name):
    posts = Post.query.filter_by(category=category_name).all()
    return render_template('category.html', posts=posts, category_name=category_name)



# ---------------- VIEW POST + ADD COMMENT ----------------
@bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.date_posted.desc()).all()
    form = CommentForm()

    if form.validate_on_submit() and current_user.is_authenticated:
        new_comment = Comment(
            content=form.comment.data.strip(),
            user_id=current_user.id,
            post_id=post.id
        )
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment added!', 'success')
        return redirect(url_for('main.view_post', post_id=post.id))

    elif form.is_submitted() and not current_user.is_authenticated:
        flash('Please log in to comment.', 'warning')
        return redirect(url_for('main.login'))

    return render_template('view_post.html', post=post, comments=comments, form=form)

# ---------------- FETCH COMMENTS (AJAX) ----------------
@bp.route('/comments/<int:post_id>')
def fetch_comments(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.date_posted.desc()).all()
    form = CommentForm()
    return render_template('partials/_comments.html', post=post, comments=comments, form=form)

   
# ---------------- ADD COMMENT (for AJAX) ----------------
@bp.route('/add_comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(
            content=form.comment.data.strip(),
            user_id=current_user.id,
            post_id=post.id
        )
        db.session.add(comment)
        db.session.commit()

    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.date_posted.desc()).all()
    return render_template('partials/_comments.html', post=post, comments=comments, form=form)


# ---------------- VIEW PROFILE ----------------
@bp.route('/profile/<username>')
def view_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.date_posted.desc()).all()
    return render_template('view_profile.html', user=user, posts=posts)

# ---------------- EDIT PROFILE ----------------
@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()

    if form.validate_on_submit():
        current_user.fullname = form.fullname.data
        current_user.bio = form.bio.data

        # Profile Picture
        if form.profile_pic.data:
            profile_folder = os.path.join(current_app.root_path, 'static/uploads/profile_pics')
            os.makedirs(profile_folder, exist_ok=True)
            filename = secure_filename(form.profile_pic.data.filename)
            path = os.path.join(profile_folder, filename)
            form.profile_pic.data.save(path)
            current_user.profile_pic = filename

        # Cover Photo
        if form.cover_photo.data:
            cover_folder = os.path.join(current_app.root_path, 'static/uploads/cover_photos')
            os.makedirs(cover_folder, exist_ok=True)
            cover_filename = secure_filename(form.cover_photo.data.filename)
            cover_path = os.path.join(cover_folder, cover_filename)
            form.cover_photo.data.save(cover_path)
            current_user.cover_photo = cover_filename

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile'))

    elif request.method == 'GET':
        form.fullname.data = current_user.fullname
        form.bio.data = current_user.bio

    return render_template('edit_profile.html', form=form)


# ---------------- PROFILE ----------------
@bp.route('/profile')
@login_required
def profile():
    posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.date_posted.desc()).all()
    return render_template('profile.html', user=current_user, posts=posts)


# ---------------- LIKE POST ----------------
@bp.route('/like/<int:post_id>')
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user_id=current_user.id, post_id=post.id).first()

    if like:
        db.session.delete(like)
    else:
        new_like = Like(user_id=current_user.id, post_id=post.id)
        db.session.add(new_like)

    db.session.commit()
    return redirect(request.referrer or url_for('main.home'))


# ---------------- DELETE POST ----------------
@bp.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.user_id != current_user.id:
        flash("You are not authorized to delete this post.", "danger")
        return redirect(url_for('main.home'))

    if post.image:
        image_path = os.path.join(current_app.root_path, 'static/uploads', post.image)
        if os.path.exists(image_path):
            os.remove(image_path)

    if post.video:
        video_path = os.path.join(current_app.root_path, 'static/uploads', post.video)
        if os.path.exists(video_path):
            os.remove(video_path)

    db.session.delete(post)
    db.session.commit()

    flash("Post deleted successfully.", "info")
    return redirect(url_for('main.home'))



# ---------------- SEARCH ----------------
@bp.route('/search')
def search():
    query = request.args.get('q', '')
    results = []
    if query:
        results = Post.query.filter(
            Post.title.like(f'%{query}%') | Post.content.like(f'%{query}%')
        ).all()
    return render_template('search.html', results=results, query=query)


# ---------------- ABOUT ----------------
@bp.route('/about')
def about():
    return render_template('about.html')
