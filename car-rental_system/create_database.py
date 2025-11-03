import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection parameters
DB_HOST = os.environ.get('DATABASE_HOST') or 'localhost'
DB_USER = os.environ.get('DATABASE_USER') or 'root'
DB_PASSWORD = os.environ.get('DATABASE_PASSWORD') or ''
DB_NAME = os.environ.get('DATABASE_NAME') or 'car_rental_db'

try:
    # Connect to MySQL server (without specifying a database)
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    with connection.cursor() as cursor:
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"[OK] Database '{DB_NAME}' created successfully (or already exists)")
    
    connection.commit()
    connection.close()
    print("[OK] Database setup complete!")
    
except pymysql.Error as e:
    print(f"[ERROR] Error connecting to MySQL: {e}")
    print("\nPlease make sure:")
    print("1. MySQL server is running")
    print("2. Your credentials are correct")
    print("3. You have permission to create databases")
