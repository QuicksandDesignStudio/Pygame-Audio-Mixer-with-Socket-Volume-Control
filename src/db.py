import sqlite3


def create_sensor_table():
    # Connect to the database
    conn = sqlite3.connect("sensor_database.db")

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    # Create the table with auto-incrementing "Id" column
    cursor.execute(
        """CREATE TABLE sensor_record
                      (Id INTEGER PRIMARY KEY AUTOINCREMENT,
                      created_at DATETIME,
                      sensor_profile TEXT)"""
    )

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print("Database and table created successfully!")


def save_sensor_record(created_at, sensor_profile):
    # Connect to the database
    conn = sqlite3.connect("sensor_database.db")

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    # Insert a new row into the table
    cursor.execute(
        "INSERT INTO sensor_record (created_at, sensor_profile) VALUES (?, ?)",
        (created_at, sensor_profile),
    )

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
