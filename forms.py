from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, FloatField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange

# for registration any kind backend
class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4)])
    role = SelectField('Role', choices=[('patient','Patient'),('doctor','Doctor')])
    specialization = StringField('Specialization (doctors)')
    submit = SubmitField('Register')

# login registration backend
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
 
 # profile registraion back
class ProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Update')

# doc details forms back
class DoctorProfileForm(FlaskForm):
    specialization = StringField('Specialization', validators=[DataRequired()])
    bio = TextAreaField('Bio')
    submit = SubmitField('Update Profile')

# symptoms and doc booking back
class BookForm(FlaskForm):
    symptoms = TextAreaField('Symptoms', validators=[DataRequired()])
    submit = SubmitField('Book')

# rating back
class RateForm(FlaskForm):
    score = IntegerField('Score', validators=[DataRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField('Rate')

# chatting room back
class ChatForm(FlaskForm):
    message = StringField('Message', validators=[DataRequired(), Length(min=2)])
    submit = SubmitField('Send')

# pass rest back for link sending
class ResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Link')

# pass rest back and reseting
class ResetForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')
