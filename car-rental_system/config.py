import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    DB_HOST = os.environ.get('DATABASE_HOST') or 'localhost'
    DB_USER = os.environ.get('DATABASE_USER') or 'root'
    DB_PASSWORD = os.environ.get('DATABASE_PASSWORD') or ''
    DB_NAME = os.environ.get('DATABASE_NAME') or 'car_rental_db'
    
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload configuration
    UPLOAD_FOLDER = 'static/uploads/cars'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Pagination
    CARS_PER_PAGE = 12
    BOOKINGS_PER_PAGE = 10
