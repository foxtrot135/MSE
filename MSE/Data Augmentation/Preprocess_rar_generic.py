import os
import pymongo
import requests
import subprocess
import zipfile
import shutil
import post_processing
import sys

# MongoDB connection settings
mongo_client = pymongo.MongoClient("")
db = mongo_client["FYP"]
collection = db["buffer"]

# Directory to store downloaded files
malware_dir = ""

# Create the Malwares directory if it doesn't exist
if not os.path.exists(malware_dir):
    os.makedirs(malware_dir)

# File to store downloaded file names
downloaded_files_file = os.path.join(malware_dir, "downloaded_files.txt")

def read_downloaded_files():
    downloaded_files = set()
    if os.path.exists(downloaded_files_file):
        with open(downloaded_files_file, "r") as file:
            for line in file:
                downloaded_files.add(line.strip())
    return downloaded_files

def extract_archive(file_path, password, destination_dir):
    try:
        destination_dir = destination_dir.replace(' ', '_')
        command = ['7z', 'x', '-y', file_path, '-o' + destination_dir]
        if password:
            command.extend(['-p' + password])
        subprocess.call(command)
        print("File '%s' extracted successfully." % file_path)
        os.remove(file_path)
        print("Deleted file: %s" % file_path)
        
        return True
    except subprocess.CalledProcessError as e:
        print("Error extracting file '%s': %s" % (file_path, e))
        return False
    except Exception as e:
        print("An error occurred during extraction of file '%s': %s" % (file_path, e))
        return False


def extract_nested_zip(file_path, destination_dir):
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
  
            temp_dir = os.path.join(destination_dir, 'temp')
            zip_ref.extractall(temp_dir)
        
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



# Function to traverse directories, identify remaining zip files, and extract them
def extract_remaining_zip_files():
    processed_files = set()  # Track processed files
    for root, dirs, files in os.walk(malware_dir):
        for file_name in files:
            if file_name.endswith('.zip'):
                file_path = os.path.join(root, file_name)
                # Skip file if it has already been processed
                if file_path in processed_files:
                    continue
                # Extract file and mark as processed
                if extract_archive(file_path, 'infected', root):
                    processed_files.add(file_path)
                    # Extract nested zip files
                    extract_nested_zip(file_path, os.path.dirname(file_path))
                else:
                    print("Failed to extract file: %s" % file_path)

# Retrieve download links and file names from MongoDB
# Retrieve download links and MD5 hashes from MongoDB
downloaded_files = read_downloaded_files()
for document in collection.find({}, {"md5_hash": 1, "download_link": 1}):
    md5_hash = document.get("md5_hash")
    download_link = document.get("download_link")

    # Skip document if MD5 hash or download link is missing
    if not md5_hash or not download_link:
        print("MD5 hash or download link missing for document: %s" % document)
        continue
    
    try:
        # Check if the file has already been downloaded
        if md5_hash in downloaded_files:
            print("File with MD5 hash '%s' already downloaded. Skipping..." % md5_hash)
            continue

        # Download the file
        response = requests.get(download_link)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Save the file locally in the Malwares directory
            file_path = os.path.join(malware_dir, md5_hash + ".zip")
            with open(file_path, "wb") as file:
                file.write(response.content)
            print("File with MD5 hash '%s' downloaded successfully." % md5_hash)
            if file_path.endswith('.zip'):
                unzip_dir = os.path.join(malware_dir, os.path.splitext(md5_hash)[0])
                if not os.path.exists(unzip_dir):
                    os.makedirs(unzip_dir)
                extract_archive(file_path, 'infected', unzip_dir)
                print("File with MD5 hash '%s' extracted and stored in '%s'." % (md5_hash, unzip_dir))
                # Recursively extract compressed archives inside the extracted directory
                extract_remaining_zip_files()
            
            # Write downloaded file name to text file
            with open(downloaded_files_file, "a") as file:
                file.write(md5_hash + "\n")
            sys.exit(0)
            # Unzip the file if it's a ZIP archive
            
        else:
            print("Failed to download file with MD5 hash '%s' from link: %s" % (md5_hash, download_link))
    except Exception as e:
        print("Error downloading file with MD5 hash '%s': %s" % (md5_hash, e))

# Extract any remaining zip files in the Malwares directory
extract_remaining_zip_files()
