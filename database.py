from datetime import datetime
import sqlite3
import bcrypt

DATABASE_NAME = "driver_drowsiness_detection.db"

def initialize_tables():
    """Initialize the database tables"""

    initialize_users_table()
    initialize_drowsiness_events_table()
    initialize_favorite_contacts_table()

def initialize_users_table():
    """Initialize the SQLite database for storing system users."""

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            fullname VARCHAR(255) NOT NULL,
            picture VARCHAR(255) UNIQUE
        )
    """)

    connection.commit()
    connection.close()

def register_user(username, password, fullname):
    """Register a new user with a username, password (plain text), and fullname."""

    if not username or not password:
        return False, "Username and password cannot be empty."

    hashed_password = hash_password(password)

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (username, password, fullname, picture)
            VALUES (?, ?, ?, '')
        """, (username, hashed_password, fullname))

        connection.commit()
        return True, "User registered successfully."

    except sqlite3.IntegrityError:
        return False, "Username already exists."

    except sqlite3.Error as e:
        return False, f"Database error: {e}"

    except Exception as e:
        return False, f"Unexpected error: {e}"

    finally:
        connection.close()

def login_user(username, password):
    """Login a user by checking the username and password."""

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT password FROM users WHERE username = ?
        """, (username,))
        result = cursor.fetchone()

        if result and bcrypt.checkpw(password.encode("utf-8"), result[0].encode("utf-8")):
            return True, "Login successful."
        else:
            return False, "Invalid username or password."

    except sqlite3.Error as e:
        return False, f"Database error: {e}"

    except Exception as e:
        return False, f"Unexpected error: {e}"

    finally:
        connection.close()

def hash_password(password):
    """Hash the password using bcrypt."""
    if isinstance(password, str):
        password = password.encode('utf-8')  # Only encode if it's a string
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password, salt).decode('utf-8')

def update_profile(user_id, username=None, password=None, fullname=None, picture=None):
    """Update user profile information."""

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    try:
        # Prepare the update query with dynamic columns
        update_fields = []
        update_values = []

        if username:
            update_fields.append("username = ?")
            update_values.append(username)

        if password:
            hashed_password = hash_password(password)
            update_fields.append("password = ?")
            update_values.append(hashed_password)

        if fullname:
            update_fields.append("fullname = ?")
            update_values.append(fullname)

        if picture:
            update_fields.append("picture = ?")
            update_values.append(picture)

        update_values.append(user_id)

        if not update_fields:
            return False, "No fields to update."

        update_query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"

        cursor.execute(update_query, update_values)

        if cursor.rowcount == 0:
            return False, "User not found or no changes made."

        connection.commit()
        return True, "Profile updated successfully."

    except sqlite3.IntegrityError:
        return False, "Username already exists."

    except sqlite3.Error as e:
        return False, f"Database error: {e}"

    except Exception as e:
        return False, f"Unexpected error: {e}"

    finally:
        connection.close()

def initialize_drowsiness_events_table():
    """Initialize the SQLite database for storing drowsiness events."""

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS drowsiness_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP NOT NULL,
            ear_value REAL NOT NULL,
            user_id INTEGER NOT NULL,

            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    connection.commit()
    connection.close()

def insert_drowsiness_event(ear_value, username):
    """Insert a drowsiness event into the SQLite database."""

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    try:
        # Fetch the user_id for the given username
        cursor.execute("""
            SELECT id FROM users WHERE username = ?
        """, (username,))
        result = cursor.fetchone()

        if result:
            user_id = result[0]
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT INTO drowsiness_events (timestamp, ear_value, user_id)
                VALUES (?, ?, ?)
            """, (timestamp, ear_value, user_id))

            connection.commit()
            return True, "Drowsiness event inserted successfully."

        else:
            return False, "User not found."

    except sqlite3.Error as e:
        return False, f"Database error: {e}"

    except Exception as e:
        return False, f"Unexpected error: {e}"

    finally:
        connection.close()

def initialize_favorite_contacts_table():
    """Initialize the SQLite database for storing favorite contacts."""

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorite_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_code INTEGER NOT NULL,
            national_number BIGINT NOT NULL,
            user_id INTEGER NOT NULL,

            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    connection.commit()
    connection.close()

def add_contact(username, country_code, national_number):
    """Add a new contact for the user."""

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    try:
        # Fetch the user_id for the given username
        cursor.execute("""
            SELECT id FROM users WHERE username = ?
        """, (username,))
        result = cursor.fetchone()

        if result:
            user_id = result[0]

            # Check the current number of contacts for this user
            cursor.execute("""
                SELECT COUNT(*) FROM favorite_contacts WHERE user_id = ?
            """, (user_id,))
            contact_count = cursor.fetchone()[0]

            if contact_count >= 3:
                return False, "User already has the maximum allowed number of contacts (3)."

            cursor.execute("""
                INSERT INTO favorite_contacts (country_code, national_number, user_id)
                VALUES (?, ?, ?)
            """, (country_code, national_number, user_id))

            connection.commit()
            return True, "Contact added successfully."

        else:
            return False, "User not found."

    except sqlite3.Error as e:
        return False, f"Database error: {e}"

    except Exception as e:
        return False, f"Unexpected error: {e}"

    finally:
        connection.close()

def get_contacts(username):
    """Get all contacts for the user."""

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    try:
        # Fetch the user_id for the given username
        cursor.execute("""
            SELECT id FROM users WHERE username = ?
        """, (username,))
        result = cursor.fetchone()

        if result:
            user_id = result[0]

            cursor.execute("""
                SELECT id, country_code, national_number FROM favorite_contacts WHERE user_id = ?
            """, (user_id,))
            contacts = cursor.fetchall()

            return True, contacts

        else:
            return False, "User not found."

    except sqlite3.Error as e:
        return False, f"Database error: {e}"

    except Exception as e:
        return False, f"Unexpected error: {e}"

    finally:
        connection.close()

def update_contact(contact_id, country_code, national_number):
    """Update an existing contact."""

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE favorite_contacts
            SET country_code = ?, national_number = ?
            WHERE id = ?
        """, (country_code, national_number, contact_id))

        if cursor.rowcount == 0:
            return False, "Contact not found."

        connection.commit()
        return True, "Contact updated successfully."

    except sqlite3.Error as e:
        return False, f"Database error: {e}"

    except Exception as e:
        return False, f"Unexpected error: {e}"

    finally:
        connection.close()

def delete_contact(contact_id):
    """Delete a contact."""

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    try:
        cursor.execute("""
            DELETE FROM favorite_contacts WHERE id = ?
        """, (contact_id,))

        if cursor.rowcount == 0:
            return False, "Contact not found."

        connection.commit()
        return True, "Contact deleted successfully."

    except sqlite3.Error as e:
        return False, f"Database error: {e}"

    except Exception as e:
        return False, f"Unexpected error: {e}"

    finally:
        connection.close()