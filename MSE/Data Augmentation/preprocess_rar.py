import os
import pymongo
import requests
import subprocess
import zipfile
import logging
from pathlib import Path

# MongoDB connection settings
MONGO_URI = "MongoDB Connection String "
mongo_client = pymongo.MongoClient(MONGO_URI)

# Directory to store downloaded files
MALWARE_DIR = Path("")

# MongoDB database and collection
db = mongo_client["MSE"]
collection = db["win"]

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create the directory if it doesn't exist
MALWARE_DIR.mkdir(parents=True, exist_ok=True)
downloaded_files_file = MALWARE_DIR / "downloaded_files.txt"

def read_downloaded_files():
    if downloaded_files_file.exists():
        return set(downloaded_files_file.read_text().splitlines())
    return set()

def rename_files_with_spaces(dir_path):
    for file in dir_path.rglob('* *'):
        new_name = file.name.replace(' ', '_')
        file.rename(file.parent / new_name)

def extract_archive(file_path, passwords, destination_dir):
    for password in passwords:
        try:
            command = ['7z', 'x', '-y', str(file_path), '-o' + str(destination_dir)]
            if password:
                command.append('-p' + password)
            subprocess.run(command, check=True)
            rename_files_with_spaces(destination_dir)
            file_path.unlink()
            logging.info(f"File '{file_path}' extracted with password '{password}' and renamed successfully.")
            return
        except subprocess.CalledProcessError:
            logging.warning(f"Password '{password}' failed for file '{file_path}'. Trying next password...")
    logging.error(f"All passwords failed for extracting '{file_path}'. File not extracted.")

def handle_zip_extraction():
    passwords = ['infected', '1337', 'harounisthebest', 'Uirusu', 'password', '123456', 'root', '1234']
    processed_files = set()
    for file_path in MALWARE_DIR.rglob('*.zip'):
        if file_path in processed_files:
            continue
        extract_archive(file_path, passwords, file_path.parent)
        processed_files.add(file_path)
        # Delete the ZIP file after extraction
        file_path.unlink()

def download_and_extract():
    passwords = ['infected', '1337', 'harounisthebest', 'password', '123456', 'root', '1234']
    downloaded_files = read_downloaded_files()
    for document in collection.find({}, {"md5_hash": 1, "download_link": 1}):
        md5_hash = document.get("md5_hash")
        download_link = document.get("download_link")
        if not md5_hash or not download_link:
            logging.warning(f"MD5 hash or download link missing for document: {document}")
            continue
        if md5_hash in downloaded_files:
            logging.info(f"File with MD5 hash '{md5_hash}' already downloaded. Skipping...")
            continue
        try:
            response = requests.get(download_link)
            if response.status_code == 200:
                file_path = MALWARE_DIR / f"{md5_hash}.zip"
                file_path.write_bytes(response.content)
                unzip_dir = MALWARE_DIR / md5_hash
                unzip_dir.mkdir(exist_ok=True)
                extract_archive(file_path, passwords, unzip_dir)
                with downloaded_files_file.open("a") as file:
                    file.write(md5_hash + "\n")
            else:
                logging.error(f"Failed to download file with MD5 hash '{md5_hash}' from link: {download_link}")
        except Exception as e:
            logging.error(f"Error downloading file with MD5 hash '{md5_hash}': {e}")

if __name__ == "__main__":
    download_and_extract()
    handle_zip_extraction()
