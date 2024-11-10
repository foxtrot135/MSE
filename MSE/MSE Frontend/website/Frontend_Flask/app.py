from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.exceptions import BadRequest
import json

app = Flask(__name__)

# Custom JSON encoder to handle ObjectId serialization
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

# Set the custom JSON encoder for Flask app
app.json_encoder = CustomJSONEncoder

# Connection URI
uri = ""

# Database Name
db_name = "FYP"

# Collection Name
collection_name = "buffer"

@app.route('/')
def index():
    # Render the home page template
    return render_template('index.html')

@app.route('/database')
def database():
    # Connect to MongoDB
    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]

    # Fetch all documents from the collection
    documents = collection.find()

    # Pass the documents to the database page template for rendering
    return render_template('database.html', documents=documents)

@app.route('/search', methods=['POST'])
def search():
    # Receive the search query and OS type from the form data
    search_query = request.form.get('query')
    os_type = request.form.get('os')  # Added to handle OS selection

    print("Received search query:", search_query)  # Print the search query received by Flask
    print("Received OS type:", os_type)  # Print the OS type received by Flask

    if not search_query:
        return jsonify({"error": "Search query is missing or empty"}), 400

    # Connect to MongoDB
    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]

    # Construct query based on search query and OS type
    query = { "$text": { "$search": f'"{search_query}"' } }
    if os_type != 'All':
        query['OS_Type'] = os_type

    # Project specific fields related to the malware
    projection = {'file_name': 1, 'md5_hash': 1, 'OS_Type': 1, 'download_link': 1, 'Architecture_&_Platform': 1, 'score': 1, '_id': False}

    # Query MongoDB based on the search query and OS type, and project specific fields
    results = collection.find(query, projection)

    # Modify search results to show the highest score
    search_results = []
    for result in results:
        if 'score' in result and isinstance(result['score'], list):
            highest_score = max(result['score'])
            result['score'] = highest_score
        search_results.append({k: str(v) if isinstance(v, ObjectId) else v for k, v in result.items()})

    print("Request sent to MongoDB:", search_results)  # Print the request being sent to MongoDB

    # Return the search results to the client-side JavaScript
    return jsonify(search_results)

@app.route('/malware/windows')
def windows_malware():
    # Connect to MongoDB
    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]

    # Query MongoDB for malware related to Windows
    query = {"OS_Type": "Windows"}
    windows_malware = collection.find(query)

    # Pass the Windows malware documents to the template for rendering
    return render_template('windows_malware.html', windows_malware=windows_malware)

@app.route('/win')
def windows_malware_html():
    # Connect to MongoDB
    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]

    # Query MongoDB for malware related to Windows
    query = {"OS_Type": "Windows"}
    windows_malware = collection.find(query, projection={'file_name': 1, 'md5_hash': 1, 'OS_Type': 1, 'download_link': 1, 'Architecture_&_Platform': 1, '_id': False})

    # Pass the Windows malware documents to the template for rendering
    return render_template('win.html', windows_malware=windows_malware)

@app.errorhandler(BadRequest)
def handle_bad_request(error):
    response = jsonify({"error": "Invalid ObjectId"})
    response.status_code = 400
    return response

if __name__ == '__main__':
    app.run(host='172.20.10.13', port='5000',debug=True)
