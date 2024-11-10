from pymongo import MongoClient

# Connection URI
uri = ""

# Database Name
db_name = "FYP"

# Collection Name
collection_name = "buffer"

# Connect to the MongoDB server
client = MongoClient(uri)

try:
    # Connect to the specific database
    db = client[db_name]

    # Get the collection
    collection = db[collection_name]

    # Fetch all documents from the collection
    documents = collection.find()

    # Print fetched documents
    print("All documents in the collection:")
    for doc in documents:
        print(doc)

except Exception as e:
    print("Error occurred:", e)
finally:
    # Close the client
    client.close()
