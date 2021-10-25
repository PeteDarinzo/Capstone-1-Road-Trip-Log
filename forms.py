from flask_wtf import FlaskForm
from flask_wtf.recaptcha import validators
from wtforms import StringField, IntegerField, TextField, TextAreaField, PasswordField
from wtforms.validators import InputRequired, ValidationError, DataRequired, Length, email_validator, Email
from wtforms.fields.html5 import DateField
from flask_wtf.file import FileField, FileAllowed
from datetime import datetime
from flask_uploads import UploadSet, IMAGES

#DATE PICKER FORM:
# https://www.youtube.com/watch?v=jAdFZa6KZNE

images = UploadSet()


class BusinessSearchForm(FlaskForm):
    """Form for business search submit."""

    category = StringField("Category", validators=[InputRequired(message="This field is required.")])
    city = StringField("Location", validators=[InputRequired(message="This field is required.")])


class LogForm(FlaskForm):
    """Form to submit a new log."""

    title = StringField("Title", render_kw={'class': 'form-control', 'placeholder' : 'Title'}, validators=[InputRequired(message="This field is required.")])
    location = StringField("Location", render_kw={'class': 'form-control', 'placeholder' : 'City, State'})
    mileage = IntegerField("Mileage", render_kw={'class': 'form-control', 'placeholder' : 'Mileage'})
    date = DateField('DatePicker', format='%Y-%m-%d', render_kw={'class': 'form-control'}, default=datetime.now)
    photo = FileField("Image (Optional)")
    text = TextAreaField("Body", render_kw={'class': 'form-control', 'rows' : '500', 'cols' :'10'}, validators=[InputRequired("This field is required.")])


class MaintenanceForm(FlaskForm):
    """Form to submit a new maintenance event."""

    # date = StringField("Date", render_kw={'class': 'form-control', 'placeholder' : 'Date'}, validators=[InputRequired(message="This field is required.")])

    title = StringField("Title", render_kw={'class': 'form-control', 'placeholder' : 'Title'}, validators=[InputRequired(message="This field is required.")])
    location = StringField("Location", render_kw={'class': 'form-control', 'placeholder' : 'City, State'}, validators=[InputRequired("This field is required.")])
    mileage = IntegerField("Mileage", render_kw={'class': 'form-control', 'placeholder' : 'Mileage'})
    date = DateField('DatePicker', render_kw={'class': 'form-control'}, format='%Y-%m-%d', default=datetime.now)
    photo = FileField("Image (Optional)")
    description = TextAreaField("Body", render_kw={'class': 'form-control'}, validators=[InputRequired("This field is required.")])


class SignupForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', render_kw={'class': 'form-control'}, validators=[DataRequired()])
    email = StringField('E-mail', render_kw={'class': 'form-control'}, validators=[DataRequired()])
    password = PasswordField('Password', render_kw={'class': 'form-control'}, validators=[Length(min=6)])
    # image_url = StringField('(Optional) Image URL')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', render_kw={'class': 'form-control'}, validators=[DataRequired()])
    password = PasswordField('Password', render_kw={'class': 'form-control'}, validators=[Length(min=6)])


class EditProfileForm(FlaskForm):
    """Form for editing user profile."""

    username = StringField('Username', render_kw={'class': 'form-control'}, validators=[DataRequired()])
    email = StringField('E-mail', render_kw={'class': 'form-control'}, validators=[DataRequired()])
    bio = TextAreaField('Bio', render_kw={'class': 'form-control'})
    profile_photo = FileField("Profile Image")

class ChangePasswordForm(FlaskForm):
    """Form for changing password."""

    curr_password = PasswordField('Current Password', render_kw={'class': 'form-control'}, validators=[Length(min=6)])
    new_password_one = PasswordField('New Password', render_kw={'class': 'form-control'}, validators=[Length(min=6)])
    new_password_two = PasswordField('Confirm New Password', render_kw={'class': 'form-control'}, validators=[Length(min=6)])