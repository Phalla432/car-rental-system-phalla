from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, Car, Booking
from forms import RegistrationForm, LoginForm, CarForm, BookingForm, SearchForm
from werkzeug.utils import secure_filename
from datetime import datetime, date
from sqlalchemy import or_, and_
import os

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def save_car_image(image_file):
    """Save uploaded car image and return filename"""
    if image_file and allowed_file(image_file.filename):
        filename = secure_filename(image_file.filename)
        # Add timestamp to avoid conflicts
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(filepath)
        return filename
    return None

# Routes
@app.route('/')
def index():
    """Home page with featured cars"""
    featured_cars = Car.query.filter_by(is_available=True).limit(6).all()
    return render_template('index.html', cars=featured_cars)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            full_name=form.full_name.data,
            phone=form.phone.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User and admin login"""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            if user.is_admin:
                return redirect(next_page) if next_page else redirect(url_for('admin_dashboard'))
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/cars')
def cars():
    """Browse all available cars with search and filter"""
    page = request.args.get('page', 1, type=int)
    query = request.args.get('query', '')
    category = request.args.get('category', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    # Base query
    cars_query = Car.query.filter_by(is_available=True)
    
    # Apply filters
    if query:
        cars_query = cars_query.filter(
            or_(
                Car.brand.ilike(f'%{query}%'),
                Car.model.ilike(f'%{query}%'),
                Car.description.ilike(f'%{query}%')
            )
        )
    
    if category:
        cars_query = cars_query.filter_by(category=category)
    
    if min_price:
        cars_query = cars_query.filter(Car.price_per_day >= min_price)
    
    if max_price:
        cars_query = cars_query.filter(Car.price_per_day <= max_price)
    
    # Pagination
    cars_paginated = cars_query.paginate(page=page, per_page=app.config['CARS_PER_PAGE'], error_out=False)
    
    return render_template('cars.html', cars=cars_paginated, query=query, category=category)

@app.route('/car/<int:car_id>')
def car_detail(car_id):
    """View car details"""
    car = Car.query.get_or_404(car_id)
    form = BookingForm() if current_user.is_authenticated else None
    return render_template('car_detail.html', car=car, form=form, today=date.today())

@app.route('/book/<int:car_id>', methods=['POST'])
@login_required
def book_car(car_id):
    """Create a new booking"""
    if current_user.is_admin:
        flash('Admins cannot make bookings.', 'warning')
        return redirect(url_for('car_detail', car_id=car_id))
    
    car = Car.query.get_or_404(car_id)
    form = BookingForm()
    
    if form.validate_on_submit():
        # Calculate total days
        start_date = form.start_date.data
        end_date = form.end_date.data
        total_days = (end_date - start_date).days
        
        # Check car availability for selected dates
        conflicting_bookings = Booking.query.filter(
            and_(
                Booking.car_id == car_id,
                Booking.status.in_(['pending', 'approved']),
                or_(
                    and_(Booking.start_date <= start_date, Booking.end_date >= start_date),
                    and_(Booking.start_date <= end_date, Booking.end_date >= end_date),
                    and_(Booking.start_date >= start_date, Booking.end_date <= end_date)
                )
            )
        ).first()
        
        if conflicting_bookings:
            flash('This car is already booked for the selected dates.', 'danger')
            return redirect(url_for('car_detail', car_id=car_id))
        
        # Create booking
        booking = Booking(
            user_id=current_user.id,
            car_id=car_id,
            start_date=start_date,
            end_date=end_date,
            total_days=total_days,
            total_price=total_days * car.price_per_day,
            notes=form.notes.data
        )
        
        db.session.add(booking)
        db.session.commit()
        
        flash(f'Booking request submitted successfully! Total: {booking.total_price:,.0f} ៛', 'success')
        return redirect(url_for('my_bookings'))
    
    # If form validation fails, show errors
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('car_detail', car_id=car_id))

@app.route('/my-bookings')
@login_required
def my_bookings():
    """View user's booking history"""
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    page = request.args.get('page', 1, type=int)
    bookings = Booking.query.filter_by(user_id=current_user.id)\
        .order_by(Booking.booking_date.desc())\
        .paginate(page=page, per_page=app.config['BOOKINGS_PER_PAGE'], error_out=False)
    
    return render_template('my_bookings.html', bookings=bookings, today=date.today())

@app.route('/cancel-booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    """Cancel a booking (only before start date)"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user owns this booking
    if booking.user_id != current_user.id and not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('my_bookings'))
    
    # Check if booking can be cancelled
    if booking.start_date <= date.today():
        flash('Cannot cancel booking that has already started.', 'danger')
        return redirect(url_for('my_bookings'))
    
    if booking.status == 'cancelled':
        flash('Booking is already cancelled.', 'info')
        return redirect(url_for('my_bookings'))
    
    booking.status = 'cancelled'
    db.session.commit()
    flash('Booking cancelled successfully.', 'success')
    
    if current_user.is_admin:
        return redirect(url_for('admin_bookings'))
    return redirect(url_for('my_bookings'))

@app.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')

# Admin Routes
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard with statistics"""
    if not current_user.is_admin:
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('index'))
    
    # Statistics
    total_cars = Car.query.count()
    available_cars = Car.query.filter_by(is_available=True).count()
    total_users = User.query.filter_by(is_admin=False).count()
    total_bookings = Booking.query.count()
    pending_bookings = Booking.query.filter_by(status='pending').count()
    
    # Recent bookings
    recent_bookings = Booking.query.order_by(Booking.booking_date.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_cars=total_cars,
                         available_cars=available_cars,
                         total_users=total_users,
                         total_bookings=total_bookings,
                         pending_bookings=pending_bookings,
                         recent_bookings=recent_bookings)

@app.route('/admin/cars')
@login_required
def admin_cars():
    """Admin: Manage cars"""
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    page = request.args.get('page', 1, type=int)
    cars = Car.query.order_by(Car.created_at.desc())\
        .paginate(page=page, per_page=app.config['CARS_PER_PAGE'], error_out=False)
    
    return render_template('admin/cars.html', cars=cars)

@app.route('/admin/car/add', methods=['GET', 'POST'])
@login_required
def admin_add_car():
    """Admin: Add new car"""
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    form = CarForm()
    if form.validate_on_submit():
        # Handle image upload
        image_filename = 'default-car.jpg'
        if form.image.data:
            saved_file = save_car_image(form.image.data)
            if saved_file:
                image_filename = saved_file
        
        car = Car(
            brand=form.brand.data,
            model=form.model.data,
            category=form.category.data,
            seat_capacity=form.seat_capacity.data,
            price_per_day=form.price_per_day.data,
            fuel_type=form.fuel_type.data,
            transmission=form.transmission.data,
            year=form.year.data,
            license_plate=form.license_plate.data,
            description=form.description.data,
            image_url=image_filename,
            is_available=form.is_available.data
        )
        
        db.session.add(car)
        db.session.commit()
        flash('Car added successfully!', 'success')
        return redirect(url_for('admin_cars'))
    
    return render_template('admin/car_form.html', form=form, title='Add Car')

@app.route('/admin/car/edit/<int:car_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_car(car_id):
    """Admin: Edit car"""
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    car = Car.query.get_or_404(car_id)
    form = CarForm(obj=car)
    
    if form.validate_on_submit():
        car.brand = form.brand.data
        car.model = form.model.data
        car.category = form.category.data
        car.seat_capacity = form.seat_capacity.data
        car.price_per_day = form.price_per_day.data
        car.fuel_type = form.fuel_type.data
        car.transmission = form.transmission.data
        car.year = form.year.data
        car.license_plate = form.license_plate.data
        car.description = form.description.data
        car.is_available = form.is_available.data
        
        # Handle image upload
        if form.image.data:
            saved_file = save_car_image(form.image.data)
            if saved_file:
                car.image_url = saved_file
        
        db.session.commit()
        flash('Car updated successfully!', 'success')
        return redirect(url_for('admin_cars'))
    
    return render_template('admin/car_form.html', form=form, title='Edit Car', car=car)

@app.route('/admin/car/delete/<int:car_id>', methods=['POST'])
@login_required
def admin_delete_car(car_id):
    """Admin: Delete car"""
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    car = Car.query.get_or_404(car_id)
    
    # Check if car has active bookings
    active_bookings = Booking.query.filter_by(car_id=car_id)\
        .filter(Booking.status.in_(['pending', 'approved'])).first()
    
    if active_bookings:
        flash('Cannot delete car with active bookings.', 'danger')
        return redirect(url_for('admin_cars'))
    
    db.session.delete(car)
    db.session.commit()
    flash('Car deleted successfully!', 'success')
    return redirect(url_for('admin_cars'))

@app.route('/admin/bookings')
@login_required
def admin_bookings():
    """Admin: View all bookings"""
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = Booking.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    bookings = query.order_by(Booking.booking_date.desc())\
        .paginate(page=page, per_page=app.config['BOOKINGS_PER_PAGE'], error_out=False)
    
    return render_template('admin/bookings.html', bookings=bookings, status_filter=status_filter)

@app.route('/admin/booking/approve/<int:booking_id>', methods=['POST'])
@login_required
def admin_approve_booking(booking_id):
    """Admin: Approve booking"""
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    booking = Booking.query.get_or_404(booking_id)
    booking.status = 'approved'
    db.session.commit()
    flash('Booking approved!', 'success')
    return redirect(url_for('admin_bookings'))

@app.route('/admin/customers')
@login_required
def admin_customers():
    """Admin: View all customers"""
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    page = request.args.get('page', 1, type=int)
    customers = User.query.filter_by(is_admin=False)\
        .order_by(User.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/customers.html', customers=customers)

@app.route('/admin/reports')
@login_required
def admin_reports():
    """Admin: View reports"""
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    # Get report data
    from sqlalchemy import func
    from datetime import timedelta
    
    today = date.today()
    week_ago = today - timedelta(days=7)
    
    # Daily bookings (last 7 days)
    daily_bookings = db.session.query(
        func.date(Booking.booking_date).label('date'),
        func.count(Booking.id).label('count'),
        func.sum(Booking.total_price).label('revenue')
    ).filter(Booking.booking_date >= week_ago)\
     .group_by(func.date(Booking.booking_date))\
     .all()
    
    # Bookings by status
    status_summary = db.session.query(
        Booking.status,
        func.count(Booking.id).label('count')
    ).group_by(Booking.status).all()
    
    # Most popular cars
    popular_cars = db.session.query(
        Car.brand,
        Car.model,
        func.count(Booking.id).label('bookings')
    ).join(Booking, Car.id == Booking.car_id)\
     .group_by(Car.id)\
     .order_by(func.count(Booking.id).desc())\
     .limit(5).all()
    
    # Total revenue
    total_revenue = db.session.query(func.sum(Booking.total_price))\
        .filter(Booking.status.in_(['approved', 'completed'])).scalar() or 0
    
    return render_template('admin/reports.html',
                         daily_bookings=daily_bookings,
                         status_summary=status_summary,
                         popular_cars=popular_cars,
                         total_revenue=total_revenue)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
