import json
import requests
import os
import time
import shutil
from pymongo import MongoClient

#def delete_task_folder(task_id):
 #   task_folder_path = os.path.expanduser("/home/fxt/.cuckoo/storage/analyses/{}".format(task_id))
  #  try:
   #     if os.path.exists(task_folder_path):
    #        shutil.rmtree(task_folder_path)
     #       print("Task ID folder '{}' deleted successfully.".format(task_id))
      #  else:
       #     print("Task ID folder '{}' does not exist.".format(task_id))
 #   except Exception as e:
  #      print("Error deleting task ID folder '{}': {}".format(task_id, e))

def check_task_status(task_id):
    try:
        response = requests.get("http://0.0.0.0:1337/tasks/view/{}".format(task_id), headers=HEADERS)
        if response.status_code == 200:
            return response.json().get("task", {}).get("status")
        else:
            print("Failed to retrieve task status for task ID: {}".format(task_id))
            return None
    except Exception as e:
        print("Error checking task status for task ID {}: {}".format(task_id, e))
        return None

# Function to preprocess and insert data into MongoDB
def preprocess_and_insert_data(json_data, folder_name):
    # Parse JSON data
    data = json.loads(json_data)
    print("JSON Data:", data)

    # Connect to MongoDB
    client = MongoClient("")
    db = client["FYP"]  # Replace with your actual database name
    collection = db["gitrepo"]  # Replace with your actual collection name

    # Extract MD5 hash from folder name
    md5_hash = folder_name.split('_')[0]

    # Update existing document based on MD5 hash
    print("Appending the following data to the document for MD5 hash:", md5_hash)

    # Extract score from info object and print it
    score = data.get('info', {}).get('score')
    if score is not None:
        print("Score for MD5 hash '{}': {}".format(md5_hash, score))
        collection.update_one({"md5_hash": md5_hash}, {"$addToSet": {"score": score}})
        print("Score field appended to the document for MD5 hash:", md5_hash)
    else:
        print("No score found for MD5 hash '{}'.".format(md5_hash))

# MongoDB connection settings
mongo_client = MongoClient("")
db = mongo_client["FYP"]
collection = db["gitrepo"]

# Example usage:
DIRECTORY_PATH = ""
HEADERS = {"Authorization": "Bearer <Token>"}

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
                                            preprocess_and_insert_data(json.dumps(analysis_results), folder_name)
                                            print("Analysis results uploaded to MongoDB.")
                                            time.sleep(15)
                                            #delete_task_folder(task_id)
                                        else:
                                            print("Analysis results not yet received. Waiting...")
                                        break
                                    else:
                                        time.sleep(12)  # Wait for 12 seconds before checking status again
                        except requests.exceptions.RequestException as e:
                            print("Error:", e)
            except Exception as e:
                print("Error processing file '{}': {}".format(file_path, e))
