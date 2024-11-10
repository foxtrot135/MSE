import os
import sqlite3
import magic


def identify_file_type(file_path):
    magic_instance = magic.Magic()
    file_type = magic_instance.from_file(file_path)
    magic_instance.close()
    return file_type

def create_database(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS files
                    (id INTEGER PRIMARY KEY, file_path TEXT, file_type TEXT)''')
    conn.commit()
    conn.close()

def insert_into_database(db_file, file_path, file_type):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO files (file_path, file_type) VALUES (?, ?)''', (file_path, file_type))
    conn.commit()
    conn.close()

def analyze_directory(directory, db_file):
    create_database(db_file)

    for root, dirs, files in os.walk(directory):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            file_type = identify_file_type(file_path)
            insert_into_database(db_file, file_path, file_type)


def main():
    directory_path = "path/to/your/directory"
    db_file = "files_database.db"
    analyze_directory(directory_path, db_file)
    print("Analysis complete. Data stored in SQLite database.")

if __name__ == "__main__":
    main()
