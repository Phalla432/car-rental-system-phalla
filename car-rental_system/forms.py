from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, FloatField, IntegerField, SelectField, DateField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange
from models import User
from datetime import date

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=8, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class CarForm(FlaskForm):
    brand = StringField('Brand', validators=[DataRequired(), Length(max=50)])
    model = StringField('Model', validators=[DataRequired(), Length(max=100)])
    category = SelectField('Category', choices=[
        ('Sedan', 'Sedan'),
        ('SUV', 'SUV'),
        ('Van', 'Van'),
        ('Pickup', 'Pickup')
    ], validators=[DataRequired()])
    seat_capacity = IntegerField('Seat Capacity', validators=[DataRequired(), NumberRange(min=2, max=15)])
    price_per_day = FloatField('Price per Day (៛)', validators=[DataRequired(), NumberRange(min=0)])
    fuel_type = SelectField('Fuel Type', choices=[
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
        ('Hybrid', 'Hybrid'),
        ('Electric', 'Electric')
    ])
    transmission = SelectField('Transmission', choices=[
        ('Automatic', 'Automatic'),
        ('Manual', 'Manual')
    ])
    year = IntegerField('Year', validators=[NumberRange(min=2000, max=2025)])
    license_plate = StringField('License Plate', validators=[DataRequired(), Length(max=20)])
    description = TextAreaField('Description')
    image = FileField('Car Image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'])])
    is_available = BooleanField('Available for Rent')


class BookingForm(FlaskForm):
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    notes = TextAreaField('Additional Notes')
    
    def validate_start_date(self, start_date):
        if start_date.data < date.today():
            raise ValidationError('Start date cannot be in the past.')
    
    def validate_end_date(self, end_date):
        if hasattr(self, 'start_date') and self.start_date.data:
            if end_date.data <= self.start_date.data:
                raise ValidationError('End date must be after start date.')


class SearchForm(FlaskForm):
    query = StringField('Search')
    category = SelectField('Category', choices=[
        ('', 'All Categories'),
        ('Sedan', 'Sedan'),
        ('SUV', 'SUV'),
        ('Van', 'Van'),
        ('Pickup', 'Pickup')
    ])
    min_price = FloatField('Min Price (៛)')
    max_price = FloatField('Max Price (៛)')
    seats = SelectField('Seats', choices=[
        ('', 'Any'),
        ('4', '4 Seats'),
        ('5', '5 Seats'),
        ('7', '7 Seats'),
        ('8+', '8+ Seats')
    ])
