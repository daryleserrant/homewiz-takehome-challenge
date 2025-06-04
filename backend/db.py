import sqlite3
from backend.utils import config
import os
import random

DB_FILE = config["SETTINGS"]["DATABASE_FILE"]

def initialize_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        name TEXT,
        email TEXT UNIQUE,
        phone TEXT
    );
    """)

    # Properties Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        address TEXT,
        beds INTEGER,
        available BOOLEAN DEFAULT 1
    );
    """)

    # Availability Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS availability (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        property_id INTEGER,
        start_time DATETIME,
        end_time DATETIME,
        FOREIGN KEY (property_id) REFERENCES properties(id)
    );
    """)

    # Bookings Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        property_id INTEGER,
        slot_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (property_id) REFERENCES properties(id),
        FOREIGN KEY (slot_id) REFERENCES availability(id)
    );
    """)

    conn.commit()
    conn.close()

def insert_user(name: str, email: str, phone: str) -> int:
    """
    Inserts a new user into the users table.
    Returns the new user's id.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, email, phone) VALUES (?, ?, ?)",
        (name, email, phone)
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def find_existing_user(email: str):
    """
    Checks if a user with the specified email exists in the users table.
    Returns the user_id if the user exists, None otherwise.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM users WHERE email = ? LIMIT 1",
        (email,)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    else:
        return None

def check_inventory(beds: int) -> int:
    """
    Queries the database for all properties with the given number of beds that are available.
    Returns the property id of a randomly selected property if found, otherwise returns None.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM properties WHERE beds = ? AND available = 1",
        (beds,)
    )
    results = cursor.fetchall()
    conn.close()
    if results:
        return random.choice(results)[0]
    else:
        return None

def get_next_available_slot(property_id: int) -> dict:
    """
    Returns the next available slot (row) from the availability table for the given property_id
    that is not already booked in the bookings table. Returns None if no slots are available.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id, a.start_time, a.end_time
        FROM availability a
        LEFT JOIN bookings b ON a.id = b.slot_id
        WHERE a.property_id = ?
          AND b.slot_id IS NULL
        ORDER BY a.start_time ASC
        LIMIT 1
    """, (property_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            "id": result[0],
            "start_time": result[1],
            "end_time": result[2]
        }
    else:
        return None

def insert_booking(user_id: int, property_id: int, slot_id: int) -> int:
    """
    Inserts a new booking into the bookings table.
    Returns the new booking's id.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO bookings (user_id, property_id, slot_id) VALUES (?, ?, ?)",
        (user_id, property_id, slot_id)
    )
    booking_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return booking_id

def get_property_by_id(property_id: int) -> dict:
    """
    Retrieves a property record from the properties table by ID.
    Returns the property row as a dictionary, or None if not found.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, address, beds, available FROM properties WHERE id = ?",
        (property_id,)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "address": row[1],
            "beds": row[2],
            "available": row[3]
        }
    else:
        return None

def seed_db():
    if not os.path.exists("backend/seed.sql"):
        print("Seed.sql file not found.")
        return

    with sqlite3.connect(DB_FILE) as conn:
        with open("backend/seed.sql", "r") as f:
            conn.executescript(f.read())
        print("Seed data loaded.")

def setup_db():
    if not os.path.exists(DB_FILE):
        initialize_db()
        seed_db()
if __name__ == "__main__":
    initialize_db()
    print("Database initialized successfully.")