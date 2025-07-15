from pymongo import MongoClient

# Replace with your connection string
connection_string = "mongodb+srv://Fehinti:Embrasebot@embrase.6qzd3hi.mongodb.net/"

# Connect to MongoDB
client = MongoClient(connection_string)

# Access or create database and collection
db = client["chatbot"]              # Your database name
collection = db["messages"]         # Your collection name

# Insert a test document
result = collection.insert_one({
    "sender": "user",
    "message": "Hello, this is a test",
    "timestamp": "2025-07-15T10:00:00"
})

print("Inserted ID:", result.inserted_id)
