from datetime import datetime,timedelta
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField,TelField,EmailField,RadioField,SelectField
from wtforms.validators import DataRequired,Length,Email,EqualTo

#CREATING FORM CLASS

class RegisterForm(FlaskForm):

    firstname = StringField('First Name', validators=[DataRequired(message='Enter first name'),Length(min=3,message='First name should not be less than 3 characters')])
    lastname = StringField('Last Name', validators=[DataRequired(message='Enter last name'),Length(min=3,message='last name should not be less than 3 characters')])
    email = EmailField('Email',validators=[DataRequired(message='Enter email address'),Email(message='email should contain @gmail.com')])
    
    # phone = TelField('Enter phone number',validators=[DataRequired(message='Enter phone number'),Length(min=11,max=11,message='phone numbers should be 11 digits')])

    # phone = StringField('Phone Number', validators=[DataRequired(message='Enter phone number'),Length(min=11, max=11, message='Phone number should be 11 digits')])

    password = PasswordField('New Password',validators=[DataRequired(message='Enter password'),EqualTo('confirm',message='passwords must match'),Length(min=5,message='password must be more than 5 characters. ')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Submit')


    class Meta:
        csrf=True
        csrf_time_limit=24*60*60



# from flask_wtf import FlaskForm
# from wtforms import RadioField, SubmitField
# from wtforms.validators import DataRequired

class FruitSizeForm(FlaskForm):
    size = RadioField(
        'Choose a box size',
        choices=[
            ('large', 'Large'),
            ('medium', 'Medium'),
            ('small', 'Small')
        ],
        validators=[DataRequired(message="You must select a size.")]
    )
    submit = SubmitField('CHOOSE THIS BOX')


class DeliveryDetailsForm(FlaskForm):

    address = StringField('Enter your address to find out your delivery day.', validators=[DataRequired(message='Please enter your address')])
    date = SelectField('First delivery date',choices=[
        ('option0','Select date'),
        ('option1',(datetime.now() + timedelta(days=1)).strftime("%A, %B %d, %Y")),
        ('option2',(datetime.now() + timedelta(days=2)).strftime("%A, %B %d, %Y")),
        ('option3',(datetime.now() + timedelta(days=3)).strftime("%A, %B %d, %Y")),
        ('option4',(datetime.now() + timedelta(days=4)).strftime("%A, %B %d, %Y")),
        ('option5',(datetime.now() + timedelta(days=5)).strftime("%A, %B %d, %Y")),
        ('option6',(datetime.now() + timedelta(days=6)).strftime("%A, %B %d, %Y")),
        ('option1',(datetime.now() + timedelta(days=7)).strftime("%A, %B %d, %Y"))
    ])
    phone_number = TelField('Phone number', validators=[DataRequired(message='Enter phone number')])
    safe_place = StringField('Enter safe place')
    btn = SubmitField('Continue')


class LoginForm(FlaskForm):
    email = EmailField('Enter Email',validators=[Email(message='email should contain @gmail.com'),DataRequired(message='email cannot be empty')])
    password = PasswordField('Enter Password',validators=[DataRequired(message='Enter Password')])
    submit = SubmitField('Login')