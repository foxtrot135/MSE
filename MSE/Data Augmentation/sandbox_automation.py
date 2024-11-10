import json
import requests
import os
import time
from pymongo import MongoClient

def delete_task_folder(task_id):
    task_folder_path = os.path.expanduser("~/.cuckoo/storage/analysis/{}".format(task_id))
    try:
        if os.path.exists(task_folder_path):
            os.rmdir(task_folder_path)
            print("Task ID folder '{}' deleted successfully.".format(task_id))
        else:
            print("Task ID folder '{}' does not exist.".format(task_id))
    except Exception as e:
        print("Error deleting task ID folder '{}': {}".format(task_id, e))

def check_task_status(task_id):
    try:
        response = requests.get("http://0.0.0.0:1337/tasks/view/{}".format(task_id), headers=HEADERS)
        if response.status_code == 200:
            return response.json().get("task", {}).get("status")
	    print(response.json().get("task", {}).get("status"))
        else:
            print("Failed to retrieve task status for task ID: {}".format(task_id))
            return None
    except Exception as e:
        print("Error checking task status for task ID {}: {}".format(task_id, e))
        return None

# Function to identify OS type based on file type
def identify_os_type(type_value):
    if type_value is None:
        return "Unknown"
    elif isinstance(type_value, list):
        for item in type_value:
            if "PE32" in item or "MS-DOS" in item or "DOS/MBR" in item:
                return "Windows"
            elif "ELF" in item:
                return "Linux"
            elif ".apk" in item or "Java archive data (JAR)" in item or "Zip archive data, at least v2.0 to extract" in item:
                return "Android"
            elif "Apple Desktop Services Store" in item:
                return "Mac OSX"
            elif "Data" in item or "HTML document, ASCII text" in item or "CRLF" in item or "Composite Document" in item or "XML" in item:
                # Do nothing here if any of these conditions are met
                pass
    return "Unknown"

# Function to preprocess and insert data into MongoDB
def preprocess_and_insert_data(json_data, file_name, folder_name):
    # Parse JSON data
    data = json.loads(json_data)
    print("JSON Data:", data)
    # Extract type field from target -> file
    type_value = data.get('target', {}).get('file', {}).get('type')
    print("File Type:", type_value)

    if type_value is not None:
        # Identify OS type based on file type
        os_type = identify_os_type(type_value)
        
        # Connect to MongoDB
        client = MongoClient("")
        db = client["FYP"]  # Replace with your actual database name
        collection = db["gitrepo"]  # Replace with your actual collection name

        # Update existing document based on file name
        print("Appending the following data to the document for file:", file_name)
        print("Type Value:", type_value)
        print("OS Type:", os_type)
        print("File Name:", file_name)
        collection.update_one({"file_name": folder_name + ".zip"}, {"$addToSet": {"type": type_value, "Target_OS": os_type}})
        print("Type and OS fields appended to the document for file:", file_name)
    else:
        print("No 'type' field found in the JSON data.")

# MongoDB connection settings
mongo_client = MongoClient("")
db = mongo_client["FYP"]
collection = db["gitrepo"]

DIRECTORY_PATH = ""
HEADERS = {"Authorization": "Bearer "}

# Iterate through every folder in the directory path
for root, dirs, files in os.walk(DIRECTORY_PATH):
    for folder_name in dirs:
        # Construct the full path to the folder
        malware_folder_path = os.path.join(DIRECTORY_PATH, folder_name)

        # Iterate through every file in the folder
        for file_name in os.listdir(malware_folder_path):
            # Replace spaces with underscores in the file name
            file_name_with_underscore = file_name.replace(" ", "_")
            # Construct the full path to the file
            file_path = os.path.join(malware_folder_path, file_name_with_underscore)
            try:
                # Check if it's a file
                if os.path.isfile(file_path):
                    with open(file_path, "rb") as sample:
                        files = {"file": (file_name, sample)}
                        payload = {
                            "timeout": 60,  # Timeout parameter set to 60 seconds
                            "unique": True,  # Only submit samples that have not been analyzed before
                            "enforce_timeout": True  # Enable to enforce the execution for the full timeout value
                        }
                        try:
                            r = requests.post("http://0.0.0.0:1337/tasks/create/file", headers=HEADERS, files=files, data=payload)
                            r.raise_for_status()  # Raise an exception for HTTP errors
                            task_id = r.json().get("task_id")
                            if task_id is not None:
                                print("Task submitted successfully for file {}. Task ID: {}".format(file_path, task_id))
                                while True:
                                    status = check_task_status(task_id)
                                    if status == "completed" or status == "reported":
                                        analysis_results = requests.get("http://0.0.0.0:1337/tasks/report/{}".format(task_id), headers=HEADERS).json()
                                        if analysis_results:
                                            # Preprocess and insert data into MongoDB
                                            preprocess_and_insert_data(json.dumps(analysis_results), file_name, folder_name)
                                            print("Analysis results uploaded to MongoDB.")
                                            delete_task_folder(task_id)
                                        else:
                                            print("Analysis results not yet received. Waiting...")
                                        break
                                    else:
                                        time.sleep(12)  # Wait for 12 seconds before checking status again
                        except requests.exceptions.RequestException as e:
                            print("Error:", e)
            except Exception as e:
                print("Error processing file '{}': {}".format(file_path, e))