import pymongo

# Replace these values with your MongoDB connection details
mongo_host = '10.188.247.252'  # Replace with your laptop's IP address
mongo_port = 27017  # Default MongoDB port
database_name = 'smartparking'
collection_name = 'datadump'

# Sample data to insert into the database
data_to_insert = {
    'plate': '123ABC',
    'bluetooth': '987XYZ'
}

# Connect to the MongoDB database
try:
    client = pymongo.MongoClient(f'mongodb://{mongo_host}:{mongo_port}/')
    db = client[database_name]
    collection = db[collection_name]

    # Insert data into the collection
    collection.insert_one(data_to_insert)

    print('Data inserted successfully!')
except Exception as e:
    print(f'Error: {e}')
finally:
    client.close()
