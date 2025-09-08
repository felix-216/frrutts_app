from datetime import datetime,timedelta
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField,TelField,EmailField,RadioField,SelectField,TextAreaField,FileField,IntegerField
from wtforms.validators import DataRequired,Length,Email,EqualTo
from flask_wtf.file import FileAllowed

#CREATING FORM CLASS

class RegisterForm(FlaskForm):

    firstname = StringField('First Name', validators=[DataRequired(message='Enter first name')])
    lastname = StringField('Last Name', validators=[DataRequired(message='Enter last name')])
    email = EmailField('Email',validators=[DataRequired(message='Enter email address'),Email(message='email should contain @gmail.com')])
    
    # phone = TelField('Enter phone number',validators=[DataRequired(message='Enter phone number'),Length(min=11,max=11,message='phone numbers should be 11 digits')])

    # phone = StringField('Phone Number', validators=[DataRequired(message='Enter phone number'),Length(min=11, max=11, message='Phone number should be 11 digits')])

    password = PasswordField('New Password',validators=[DataRequired(message='Enter password'),EqualTo('confirm',message='passwords must match')])
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
    
    phone_number = TelField('Phone number', validators=[DataRequired(message='Enter phone number')])
    btn = SubmitField('Proceed To Payment')


class LoginForm(FlaskForm):
    email = EmailField('Enter Email',validators=[Email(message='email should contain @gmail.com'),DataRequired(message='email cannot be empty')])
    password = PasswordField('Enter Password',validators=[DataRequired(message='Enter Password')])
    submit = SubmitField('Login')



class UpdateProfileForm(FlaskForm):
    firstname = StringField(' Firstname',validators=[DataRequired()])
    lastname = StringField(' lastname',validators=[DataRequired()])
    email = EmailField(' email',validators=[Email(),DataRequired()])
    address = StringField(' House Address',validators=[DataRequired()])
    phone = TelField('phone number',validators=[DataRequired()])
    dp = FileField('Choose file')
    submit = SubmitField('Update Profile')

class CreateBox(FlaskForm):
    boxname = StringField('Enter Box Name',validators=[DataRequired()])
    boxsize = SelectField('Choose Box size',choices=[
        ('large', 'Large'),
        ('medium', 'Medium'),
        ('small', 'Small')
    ], validators=[DataRequired()])

    boxprice = IntegerField('Enter box price',validators=[DataRequired()])
    boximage = FileField('Enter box image',validators=[FileAllowed(['jpg','jpeg','png','gif'],'Images only'),DataRequired()])


class UpdatePasswordForm(FlaskForm):
    oldpassword = PasswordField('Enter Old Password',validators=[DataRequired()])
    
    newpassword = PasswordField('Enter New Password', validators=[DataRequired(), EqualTo('confirmpassword', message='Passwords must match')])
    confirmpassword = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Update Password')



class UpdateBox(FlaskForm):
    boxname = StringField('Enter Box Name',validators=[DataRequired()])
    boxsize = SelectField('Choose Box size',choices=[
        ('large', 'Large'),
        ('medium', 'Medium'),
        ('small', 'Small')
    ], validators=[DataRequired()])

    boxprice = IntegerField('Enter box price',validators=[DataRequired()])
    boximage = FileField('Enter box image',validators=[FileAllowed(['jpg','jpeg','png','gif'],'Images only')])