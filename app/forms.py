from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField, FileField, SelectField, DateField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, NumberRange, Optional
from flask_wtf.file import FileAllowed

class SignupForm(FlaskForm):
    username = StringField('', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('', validators=[DataRequired(), Length(min=3, max=120)])
    password = PasswordField('', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('', validators=[DataRequired(), EqualTo('password')])
    terms = BooleanField('Accept Terms & Conditions', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('', validators=[DataRequired(), Email()])
    password = PasswordField('', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('Technology', 'Technology'), ('Lifestyle', 'Lifestyle'),
        ('Education', 'Education'), ('Sports', 'Sports'),
        ('Entertainment', 'Entertainment'), ('Business', 'Business'),
        ('Art', 'Art'), ('Science', 'Science')
    ])
    image = FileField("Image", validators=[FileAllowed(["jpg", "jpeg", "png", "webp"], "Images only!")])
    video = FileField("Video", validators=[FileAllowed(["mp4", "mov", "webm"], "Video files only!")])
    submit = SubmitField('Post')

class EditProfileForm(FlaskForm):
    fullname = StringField('Full Name', validators=[DataRequired()])
    dob = DateField('Date of Birth (YYYY-MM-DD)', format='%Y-%m-%d', validators=[Optional()])
    gender = RadioField('Gender', choices=[('Male', 'Male'), ('Female', 'Female')], validators=[Optional()])

    phone_number = StringField(
        'Phone number',
        validators=[Optional(), Regexp(r'^\+?\d{10,15}$', message="Enter a valid phone number (10-15 digits).")]
    )

    bio = TextAreaField('Bio', validators=[Optional()])

    profile_pic = FileField('Profile Picture', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'])])
    cover_photo = FileField('Cover Photo', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'])])

    submit = SubmitField('Save Changes')

class CommentForm(FlaskForm):
    comment = TextAreaField('', validators=[DataRequired()])
    submit = SubmitField('Post Comment')
