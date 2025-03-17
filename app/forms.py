from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User

class SignUpForm(FlaskForm):
    username = StringField('', validators=[DataRequired(), Length(max=150)],
                         render_kw={"class": "form-control", "placeholder": "User Name"})
    email = EmailField('', validators=[DataRequired(), Email()],
                     render_kw={"class": "form-control", "placeholder": "Email Address"})
    first_name = StringField('', validators=[DataRequired(), Length(max=100)],
                          render_kw={"class": "form-control", "placeholder": "First Name"})
    last_name = StringField('', validators=[DataRequired(), Length(max=100)],
                         render_kw={"class": "form-control", "placeholder": "Last Name"})
    password1 = PasswordField('', validators=[
        DataRequired(),
        Length(min=8),
        EqualTo('password2', message='Passwords must match')
    ], render_kw={"class": "form-control", "placeholder": "Password"})
    password2 = PasswordField('', validators=[DataRequired()],
                           render_kw={"class": "form-control", "placeholder": "Confirm Password"})

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already exists')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already exists')

class AddRecordForm(FlaskForm):
    first_name = StringField('', validators=[DataRequired()],
                          render_kw={"class": "form-control", "placeholder": "First Name"})
    last_name = StringField('', validators=[DataRequired()],
                         render_kw={"class": "form-control", "placeholder": "Last Name"})
    email = StringField('', validators=[DataRequired(), Email()],
                     render_kw={"class": "form-control", "placeholder": "Email"})
    phone = StringField('', validators=[DataRequired()],
                     render_kw={"class": "form-control", "placeholder": "Phone"})
    address = StringField('', validators=[DataRequired()],
                       render_kw={"class": "form-control", "placeholder": "Address"})
    city = StringField('', validators=[DataRequired()],
                    render_kw={"class": "form-control", "placeholder": "City"})
    state = StringField('', validators=[DataRequired()],
                     render_kw={"class": "form-control", "placeholder": "State"})
    zipcode = StringField('', validators=[DataRequired()],
                       render_kw={"class": "form-control", "placeholder": "Zipcode"})
    
# from flask_wtf import FlaskForm
# from wtforms import StringField, SubmitField
# from wtforms.validators import DataRequired, Email, Length

# class AddRecordForm(FlaskForm):
#     first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
#     last_name = StringField('Last Name', validators=[DataRequired(), Length(max=100)])
#     email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
#     phone = StringField('Phone', validators=[Length(max=20)])
#     address = StringField('Address', validators=[Length(max=200)])
#     city = StringField('City', validators=[Length(max=100)])
#     state = StringField('State', validators=[Length(max=100)])
#     zipcode = StringField('Zipcode', validators=[Length(max=10)])
#     submit = SubmitField('Update Record')