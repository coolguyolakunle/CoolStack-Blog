from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from app import db
from uuid import uuid4
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

    # Handle AJAX submission
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if form.validate_on_submit():
            existing_user = User.query.filter_by(email=form.email.data).first()
            if existing_user:
                return jsonify({'success': False, 'message': 'Email already registered.'}), 200

            new_user = User(
                username=form.username.data,
                email=form.email.data,
                password=generate_password_hash(form.password.data)
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return jsonify({
                'success': True,
                'message': f"Welcome, {new_user.username}!",
                'redirect_url': url_for('main.home')  # 👈 include redirect URL
            }), 200

        return jsonify({'success': False, 'errors': form.errors}), 200

    # Normal non-AJAX fallback
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.signup'))

        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data)
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash(f"Welcome, {new_user.username}!", 'success')
        return redirect(url_for('main.home'))

    return render_template('signup.html', form=form)



# ---------------- LOGIN ----------------
# LOGIN ROUTE
@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    # Handle AJAX modal submission
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return jsonify({
                    'success': True,
                    'message': f"Welcome back, {user.username}!",
                    'redirect_url': url_for('main.home')  # 👈 send redirect target
                }), 200
            else:
                return jsonify({'success': False, 'message': 'Invalid email or password'}), 200

        # validation errors
        return jsonify({'success': False, 'errors': form.errors}), 200

    # Non-AJAX (normal form)
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


def save_upload(file_storage, folder):
    """Save file with a unique name and return filename."""
    if not file_storage or file_storage.filename == "":
        return None

    ext = os.path.splitext(file_storage.filename)[1].lower()
    filename = secure_filename(f"{uuid4().hex}{ext}")
    os.makedirs(folder, exist_ok=True)

    path = os.path.join(folder, filename)
    file_storage.save(path)
    return filename



# ---------------- CREATE POST ----------------
@bp.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()

    # AJAX GET (modal request)
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template("create_post.html", form=form, modal_only=True)

    if request.method == "POST":
        if form.validate_on_submit():
            post = Post(
                title=form.title.data,
                content=form.content.data,
                category=form.category.data,
                user_id=current_user.id
            )

            base_upload = os.path.join(current_app.root_path, "static", "uploads")
            images_folder = os.path.join(base_upload, "post_images")
            videos_folder = os.path.join(base_upload, "post_videos")

            # Save image
            new_image = save_upload(form.image.data, images_folder)
            if new_image:
                post.image = new_image

            # Save video
            new_video = save_upload(form.video.data, videos_folder)
            if new_video:
                post.video = new_video

            db.session.add(post)
            db.session.commit()

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"success": True, "message": "Post created successfully!"})

            return redirect(url_for('main.home'))

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": False, "errors": form.errors}), 400

    return render_template("create_post.html", form=form, modal_only=False)




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


def save_upload(file_storage, folder):
    """Save file with a unique name and return filename."""
    if not file_storage or file_storage.filename == "":
        return None

    ext = os.path.splitext(file_storage.filename)[1].lower()  # like ".jpg"
    filename = secure_filename(f"{uuid4().hex}{ext}")
    os.makedirs(folder, exist_ok=True)

    path = os.path.join(folder, filename)
    file_storage.save(path)
    return filename

# ---------------- EDIT PROFILE ----------------
@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()

    if request.method == "POST":
        if form.validate_on_submit():
            current_user.fullname = form.fullname.data
            current_user.bio = form.bio.data

            # ✅ save the other fields too
            current_user.dob = form.dob.data
            current_user.gender = form.gender.data
            current_user.phone_number = form.phone_number.data

            # uploads
            profile_folder = os.path.join(current_app.root_path, 'static/uploads/profile_pics')
            new_profile = save_upload(form.profile_pic.data, profile_folder)
            if new_profile:
                current_user.profile_pic = new_profile

            cover_folder = os.path.join(current_app.root_path, 'static/uploads/cover_photos')
            new_cover = save_upload(form.cover_photo.data, cover_folder)
            if new_cover:
                current_user.cover_photo = new_cover

            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('main.profile'))

        print("EDIT PROFILE ERRORS:", form.errors)

    if request.method == "GET":
        form.fullname.data = current_user.fullname
        form.bio.data = current_user.bio
        form.dob.data = current_user.dob
        form.gender.data = current_user.gender
        form.phone_number.data = current_user.phone_number

    return render_template('edit_profile.html', form=form)


# ---------------- PROFILE ----------------
@bp.route('/profile')
@login_required
def profile():
    posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.date_posted.desc()).all()
    return render_template('profile.html', user=current_user, posts=posts)


# ---------------- LIKE POST ----------------
@bp.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user_id=current_user.id, post_id=post.id).first()

    if like:
        db.session.delete(like)
        db.session.commit()
        liked = False
    else:
        new_like = Like(user_id=current_user.id, post_id=post.id)
        db.session.add(new_like)
        db.session.commit()
        liked = True

    # Return JSON for AJAX update
    return jsonify({
        "liked": liked,
        "like_count": len(post.likes)
    })



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
    q = request.args.get('q', '').strip()
    if not q:
        return redirect(url_for('main.home'))

    # Find users matching search term
    users = User.query.filter(
        (User.username.ilike(f"%{q}%")) | (User.fullname.ilike(f"%{q}%"))
    ).all()

    # Find posts matching title/content
    posts = Post.query.filter(
        (Post.title.ilike(f"%{q}%")) | (Post.content.ilike(f"%{q}%"))
    ).order_by(Post.date_posted.desc()).all()

    # Include posts by matching users
    user_posts = []
    for user in users:
        user_posts.extend(user.posts)

    # Merge and remove duplicates
    all_posts = list({p.id: p for p in (posts + user_posts)}.values())

    return render_template(
        'search_results.html',
        users=users,
        posts=all_posts,
        query=q
    )


@bp.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow(user_id):
    user = User.query.get_or_404(user_id)
    if current_user == user:
        return jsonify(status='error', message="You cannot follow yourself"), 400

    if current_user.is_following(user):
        current_user.unfollow(user)
        db.session.commit()
        return jsonify(status='unfollowed')
    else:
        current_user.follow(user)
        db.session.commit()
        return jsonify(status='followed')


# ---------------- ABOUT ----------------
@bp.route('/about')
def about():
    return render_template('about.html')

# --------Settings-----------
@bp.route('/settings')
def settings():
    return render_template('settings.html')

