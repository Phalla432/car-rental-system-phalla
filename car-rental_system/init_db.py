"""
Database Initialization Script
Run this to create database tables and add sample data
"""
from app import app, db
from models import User, Car, Booking
from datetime import date, timedelta

def init_database():
    """Initialize database with tables and sample data"""
    with app.app_context():
        # Drop all tables and recreate (for development)
        print("Creating database tables...")
        db.create_all()
        
        # Check if admin already exists
        admin = User.query.filter_by(email='admin@carrental.com').first()
        if not admin:
            # Create admin user
            admin = User(
                email='admin@carrental.com',
                full_name='Admin User',
                phone='012345678',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("Admin user created: admin@carrental.com / admin123")
        
        # Create sample customer
        customer = User.query.filter_by(email='customer@example.com').first()
        if not customer:
            customer = User(
                email='customer@example.com',
                full_name='John Doe',
                phone='098765432',
                is_admin=False
            )
            customer.set_password('password123')
            db.session.add(customer)
            print("Sample customer created: customer@example.com / password123")
        
        # Add sample cars (Cambodian context)
        if Car.query.count() == 0:
            sample_cars = [
                # Sedans
                Car(
                    brand='Toyota',
                    model='Camry',
                    category='Sedan',
                    seat_capacity=5,
                    price_per_day=120000,  # 120,000 Riel per day
                    description='Comfortable and reliable sedan perfect for business trips or family outings.',
                    fuel_type='Petrol',
                    transmission='Automatic',
                    year=2022,
                    license_plate='PP-1234',
                    image_url='default-car.jpg',
                    is_available=True
                ),
                Car(
                    brand='Hyundai',
                    model='Accent',
                    category='Sedan',
                    seat_capacity=5,
                    price_per_day=80000,
                    description='Economic and fuel-efficient sedan ideal for city driving.',
                    fuel_type='Petrol',
                    transmission='Automatic',
                    year=2021,
                    license_plate='PP-2345',
                    image_url='default-car.jpg',
                    is_available=True
                ),
                Car(
                    brand='Honda',
                    model='Civic',
                    category='Sedan',
                    seat_capacity=5,
                    price_per_day=100000,
                    description='Stylish sedan with excellent performance and comfort.',
                    fuel_type='Petrol',
                    transmission='Automatic',
                    year=2023,
                    license_plate='PP-3456',
                    image_url='default-car.jpg',
                    is_available=True
                ),
                # SUVs
                Car(
                    brand='Lexus',
                    model='RX300',
                    category='SUV',
                    seat_capacity=7,
                    price_per_day=250000,
                    description='Luxury SUV with premium features and spacious interior.',
                    fuel_type='Hybrid',
                    transmission='Automatic',
                    year=2023,
                    license_plate='PP-4567',
                    image_url='default-car.jpg',
                    is_available=True
                ),
                Car(
                    brand='Toyota',
                    model='Highlander',
                    category='SUV',
                    seat_capacity=7,
                    price_per_day=200000,
                    description='Family-friendly SUV with excellent safety features.',
                    fuel_type='Petrol',
                    transmission='Automatic',
                    year=2022,
                    license_plate='PP-5678',
                    image_url='default-car.jpg',
                    is_available=True
                ),
                Car(
                    brand='Ford',
                    model='Explorer',
                    category='SUV',
                    seat_capacity=7,
                    price_per_day=180000,
                    description='Powerful SUV perfect for both city and countryside adventures.',
                    fuel_type='Petrol',
                    transmission='Automatic',
                    year=2021,
                    license_plate='PP-6789',
                    image_url='default-car.jpg',
                    is_available=True
                ),
                # Vans
                Car(
                    brand='Hyundai',
                    model='Starex',
                    category='Van',
                    seat_capacity=12,
                    price_per_day=150000,
                    description='Spacious van perfect for group travels and family trips.',
                    fuel_type='Diesel',
                    transmission='Automatic',
                    year=2022,
                    license_plate='PP-7890',
                    image_url='default-car.jpg',
                    is_available=True
                ),
                Car(
                    brand='Toyota',
                    model='Alphard',
                    category='Van',
                    seat_capacity=8,
                    price_per_day=300000,
                    description='Premium luxury van with VIP seating and entertainment system.',
                    fuel_type='Hybrid',
                    transmission='Automatic',
                    year=2023,
                    license_plate='PP-8901',
                    image_url='default-car.jpg',
                    is_available=True
                ),
                Car(
                    brand='Mercedes-Benz',
                    model='V-Class',
                    category='Van',
                    seat_capacity=7,
                    price_per_day=350000,
                    description='Executive luxury van with premium comfort and technology.',
                    fuel_type='Diesel',
                    transmission='Automatic',
                    year=2023,
                    license_plate='PP-9012',
                    image_url='default-car.jpg',
                    is_available=True
                ),
                # Pickups
                Car(
                    brand='Ford',
                    model='Ranger',
                    category='Pickup',
                    seat_capacity=5,
                    price_per_day=140000,
                    description='Rugged pickup truck suitable for both work and adventure.',
                    fuel_type='Diesel',
                    transmission='Automatic',
                    year=2022,
                    license_plate='PP-0123',
                    image_url='default-car.jpg',
                    is_available=True
                ),
                Car(
                    brand='Toyota',
                    model='Hilux',
                    category='Pickup',
                    seat_capacity=5,
                    price_per_day=150000,
                    description='Legendary reliability and durability for any terrain.',
                    fuel_type='Diesel',
                    transmission='Manual',
                    year=2023,
                    license_plate='PP-1235',
                    image_url='default-car.jpg',
                    is_available=True
                ),
                Car(
                    brand='Mitsubishi',
                    model='Triton',
                    category='Pickup',
                    seat_capacity=5,
                    price_per_day=130000,
                    description='Powerful and efficient pickup perfect for countryside trips.',
                    fuel_type='Diesel',
                    transmission='Automatic',
                    year=2021,
                    license_plate='PP-2346',
                    image_url='default-car.jpg',
                    is_available=True
                ),
            ]
            
            for car in sample_cars:
                db.session.add(car)
            
            print(f"Added {len(sample_cars)} sample cars")
        
        # Commit all changes
        db.session.commit()
        print("\nDatabase initialized successfully!")
        print("\nYou can now login with:")
        print("Admin - Email: admin@carrental.com, Password: admin123")
        print("Customer - Email: customer@example.com, Password: password123")

if __name__ == '__main__':
    init_database()
