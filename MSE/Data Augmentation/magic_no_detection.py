import os
import sqlite3
import magic

# Function to identify magic numbers of files
def identify_magic_numbers(file_path):
    # Create a magic instance
    magic_instance = magic.Magic()

    # Identify the magic number
    magic_number = magic_instance.from_file(file_path)

    return magic_number

# Function to create the SQLite database and table
def create_database(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS magic_numbers
                    (id INTEGER PRIMARY KEY, file_path TEXT, magic_number TEXT, os_type TEXT)''')
    conn.commit()
    conn.close()

# Function to insert magic number and file path into the database
def insert_into_database(db_file, file_path, magic_number):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO magic_numbers (file_path, magic_number) VALUES (?, ?)''', (file_path, magic_number))
    conn.commit()
    conn.close()

# Function to analyze directory and insert magic numbers and file paths into the database
def analyze_directory(directory, db_file):
    create_database(db_file)

    for root, dirs, files in os.walk(directory):
        for file_name in files:
            # Combine the root and file name to get the complete file path
            file_path = os.path.join(root, file_name)

            # Check if the file exists
            if not os.path.exists(file_path):
                print("File does not exist:", file_path)
                continue

            try:
                # Handle file paths with whitespaces
                if ' ' in file_path:
                    file_path = '"{}"'.format(file_path)
                magic_number = identify_magic_numbers(file_path)
                # Remove double quotes from file path before inserting into the database
                file_path = file_path.strip('"')
                insert_into_database(db_file, file_path, magic_number)
            except Exception as e:
                print("Error processing file:", file_path, e)

# Main function
def main():
    directory_path = "/home/drawal1713/MSE/sk3ptre"  # Change this to your desired directory
    db_file = "magic_numbers_database.db"
    analyze_directory(directory_path, db_file)
    print("Analysis complete. Magic numbers stored in SQLite database.")

if __name__ == "__main__":
    main()