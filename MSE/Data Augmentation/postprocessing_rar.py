import os
import subprocess
import zipfile
import shutil

# Directory to store downloaded files
malware_dir = ""

# Function to extract a compressed archive file with 7z
# Function to extract a compressed archive file with 7z or unrar
def extract_archive(file_path, password, destination_dir):
    try:
        # Replace white spaces with '_' in the destination directory path
        destination_dir = destination_dir.replace(' ', '_')

        # Construct the appropriate command based on file extension
        if file_path.endswith('.zip'):
            command = ['7z', 'x', '-y', file_path, '-o' + destination_dir]
        elif file_path.endswith('.rar'):
            command = ['unrar', 'x', '-y', file_path, destination_dir]
        elif file_path.endswith('.7z'):
            command = ['7z', 'x', '-y', file_path, '-o' + destination_dir]
        else:
            print("Unsupported archive format for file '%s'." % file_path)
            return False

        # Add password option if provided
        if password:
            command.extend(['-p' + password])

        # Enclose file paths in quotes to handle spaces and special characters
        command = [arg if ' ' not in arg else '"' + arg + '"' for arg in command]

        print("Executing command:", " ".join(command))

        # Execute the command
        subprocess.call(command)
        print("File '%s' extracted successfully." % file_path)

        # Delete the original archive file after extraction
        os.remove(file_path)
        print("Deleted file: %s" % file_path)

        return True
    except subprocess.CalledProcessError as e:
        print("Error extracting file '%s': %s" % (file_path, e))
        return False
    except OSError as e:
        print("Error: %s" % e)
        return False

# Function to extract nested zip files
def extract_nested_zip(file_path, destination_dir):
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            # Extract all contents of the zip file to a temporary directory
            temp_dir = os.path.join(destination_dir, 'temp')
            zip_ref.extractall(temp_dir)
            
            # Move all files from the temporary directory to the destination directory
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    src_path = os.path.join(root, file)
                    dest_path = os.path.join(destination_dir, os.path.relpath(src_path, temp_dir))
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.move(src_path, dest_path)
            
            # Remove the temporary directory
            shutil.rmtree(temp_dir)
            
        print("Nested zip file '%s' extracted successfully." % file_path)
        
        # Delete the extracted zip file after extraction
        os.remove(file_path)
        print("Deleted file: %s" % file_path)
        
    except Exception as e:
        print("Error extracting nested zip file '%s': %s" % (file_path, e))


# Function to traverse directories, identify remaining archive files, and extract them
def extract_remaining_archive_files():
    for root, dirs, files in os.walk(malware_dir):
        for md5_hash in files:
            file_path = os.path.join(root, md5_hash)
            # Skip unsupported files
            if not md5_hash.endswith(('.zip', '.rar', '.7z')):
                print("Skipping unsupported file '%s'." % file_path)
                continue
            # Extract file
            extract_archive(file_path, 'infected', root)

            # Extract nested zip files
            if md5_hash.endswith('.zip'):
                extract_nested_zip(file_path, os.path.dirname(file_path))

# Extract any remaining archive files (zip, rar, 7z)
extract_remaining_archive_files()