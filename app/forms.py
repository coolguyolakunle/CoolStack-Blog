from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField, FileField, SelectField, DateField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, NumberRange
from flask_wtf.file import FileAllowed

class SignupForm(FlaskForm):
    fullname = StringField('Full name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Length(min=3, max=120)])
    dob = DateField('Date of Birth (YYYY-MM-DD)', format='%Y-%m-%d', validators=[DataRequired()])
    gender = RadioField('Gender', choices=[('Male', 'Male'), ('Female', 'Female')], validators=[DataRequired()])
    phone_number = StringField('Phone number', validators=[Regexp(r'^\+?\d{10,15}$')])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    terms = BooleanField('Accept Terms & Conditions', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
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
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    video = FileField('Upload Video', validators=[FileAllowed(['mp4', 'mov', 'avi'])])
    submit = SubmitField('Post')

class EditProfileForm(FlaskForm):
    fullname = StringField('Full Name', validators=[DataRequired()])
    bio = TextAreaField('Bio')
    profile_pic = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    cover_photo = FileField('Cover Photo', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Save Changes')  

class CommentForm(FlaskForm):
    comment = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Post Comment')
