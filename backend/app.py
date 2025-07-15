from flask import Flask, request, jsonify
from pymongo import MongoClient
import requests
from datetime import datetime

app = Flask(__name__)

# MongoDB Atlas connection
client = MongoClient("mongodb+srv://Fehinti:Embrasebot@embrase.6qzd3hi.mongodb.net/")
db = client["chatbot"]
messages_collection = db["messages"]

# Endpoint to handle incoming messages
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')

    # Log user message
    messages_collection.insert_one({
        "sender": "user",
        "message": user_message,
        "timestamp": datetime.utcnow().isoformat()
    })

    # Send to Rasa
    rasa_response = requests.post(
        'http://localhost:5005/webhooks/rest/webhook',
        json={"sender": "user", "message": user_message}
    )

    bot_reply = ""
    if rasa_response.ok:
        responses = rasa_response.json()
        for r in responses:
            bot_reply += r.get("text", "") + " "

        # Log bot response
        messages_collection.insert_one({
            "sender": "bot",
            "message": bot_reply.strip(),
            "timestamp": datetime.utcnow().isoformat()
        })

    return jsonify({"response": bot_reply.strip()})


if __name__ == '__main__':
    app.run(debug=True)
