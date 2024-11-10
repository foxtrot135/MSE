import os
import sqlite3
import magic
from pymongo import MongoClient

# Function to connect to MongoDB
def connect_to_mongodb(connection_string):
    client = MongoClient(connection_string)
    db = client['FYP']
    collection = db['buffer']
    return collection

# Function to create the SQLite database and table
def create_database(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS magic_numbers
                    (id INTEGER PRIMARY KEY, file_path TEXT, magic_number TEXT, os_type TEXT)''')
    conn.commit()
    conn.close()
    print("Table 'magic_numbers' created successfully with columns: id, file_path, magic_number, os_type")

# Function to identify magic numbers of files
def identify_magic_numbers(file_path):
    # Create a magic instance
    magic_instance = magic.Magic()

    # Read the file as a byte string
    with open(file_path, 'rb') as file:
        file_data = file.read()

    # Identify the magic number
    magic_number = magic_instance.from_buffer(file_data)

    return magic_number

# Function to determine OS type based on magic number
def determine_os_type(magic_number):
    if 'DOS' in magic_number or 'Microsoft Cabinet archive data' in magic_number or  'DLL' in magic_number or 'PE32' in magic_number or 'Apple Desktop Services Store' in magic_number or 'MS-DOS' in magic_number or 'Intel 80386 COFF' in magic_number: 
        return 'Windows'
    elif 'ELF' in magic_number or 'Bourne-Again shell script' in magic_number:
        return 'Linux'
    elif '.apk' in magic_number or 'JAR' in magic_number or 'compiled Java class data' in magic_number or 'Zip archive Data' in magic_number:
        return 'Android'
    elif 'Mach-O' in magic_number:
        return 'MACOS'
    elif 'CDFV2 Encrypted' in magic_number or 'Rich Text Format data' in magic_number or 'UDF filesystem data' in magic_number or 'Microsoft Word 2007+' in magic_number or 'C source' in magic_number or 'C++' in magic_number or  'HTML document' in magic_number :
        return 'Cross-Platform'
    elif 'Composite Document File V2 Document' in magic_number:
        # Check for keywords to determine the OS type
        if 'Windows' in magic_number:
            return 'Windows'
        elif 'Linux' in magic_number:
            return 'Linux'
        elif 'MACOS' in magic_number:
            return 'MACOS'
        else:
            return 'Unknown'
    elif 'RAR archive data' in magic_number:
        if 'Win32' in magic_number:
            return 'Windows'
        else:
            return 'Unknown'
    elif 'LHa (2.x) archive data' in magic_number:
        # Check if it contains an executable file
        if '.exe' in magic_number:
            return 'Windows'
        else:
            return 'Unknown'

# Function to update OS type column based on magic number and append to MongoDB collection
def update_os_type_and_append_to_mongodb(db_file, connection_string):
    # Connect to MongoDB
    collection = connect_to_mongodb(connection_string)

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute('''SELECT id, file_path, magic_number FROM magic_numbers WHERE os_type IS NULL''')
    rows = cursor.fetchall()
    for row in rows:
        file_path = row[1]
        magic_number = row[2]
        os_type = determine_os_type(magic_number)

        # If os_type is unknown, try finding it from another file in the same folder
        if os_type == 'Unknown':
            folder_path = os.path.dirname(file_path)
            files_in_folder = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            for file_in_folder in files_in_folder:
                file_path_in_folder = os.path.join(folder_path, file_in_folder)
                magic_number = identify_magic_numbers(file_path_in_folder)
                os_type = determine_os_type(magic_number)
                if os_type != 'Unknown':
                    break

        # If os_type is still unknown, skip this file
        if os_type == 'Unknown':
            continue

        # Find document in MongoDB collection by matching folder_name with md5_hash field
        folder_name = os.path.basename(os.path.dirname(file_path))
        document = collection.find_one({'md5_hash': folder_name})

        # Append data to document if found, or insert new document if not found
        if document:
            collection.update_one({'_id': document['_id']}, {'$set': {'Architecture_&_Platform': magic_number, 'OS_Type': os_type}})
        else:
            # If document not found, print a message or handle it as per your requirement
            print("Document with md5_hash {} not found in MongoDB.".format(folder_name))

        # Update os_type in SQLite database
        cursor.execute('''UPDATE magic_numbers SET os_type = ? WHERE id = ?''', (os_type, row[0]))

    conn.commit()
    conn.close()

# Main function
def main():
    db_file = "magic_numbers_database.db"
    connection_string = "Mongo DB Connection String"
    create_database(db_file)
    update_os_type_and_append_to_mongodb(db_file, connection_string)
    print("OS types updated in the database and data appended to MongoDB collection.")

if __name__ == "__main__":
    main()
