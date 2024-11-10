import pymongo

def connect_to_mongodb(database_name='FYP', collection_name='gitrepo'):
    # MongoDB connection string
    mongo_uri = ""

    # Connect to MongoDB
    client = pymongo.MongoClient(mongo_uri)
    db = client.get_database(database_name)
    collection = db.get_collection(collection_name)
    return collection

def retrieve_download_links(collection):
    # Retrieve the download links from the collection
    download_links_cursor = collection.find({}, {'download_link': 1})
    download_links = [link['download_link'] for link in download_links_cursor]
    return download_links

def retrieve_hash_values(collection):
    # Retrieve the hash values from the collection
    hash_values_cursor = collection.find({}, {'md5_hash'})
    hash_values = [hash_value['md5_hash'] for hash_value in hash_values_cursor]
    return hash_values

def download_links_retrieval():
    # Connect to MongoDB
    collection = connect_to_mongodb()

    # Retrieve download links
    download_links = retrieve_download_links(collection)
    # print("Download Links:")
    # for link in download_links[:]:  # Process only the first 5 links
    #     print(link)

    # Retrieve hash values
    # hash_values = retrieve_hash_values(collection)
    # print("\nHash Values:")
    # for hash_value in hash_values[:]:  # Process only the first 5 hash values
    #     print("")

