from flask import Flask, request, jsonify
from pymongo import MongoClient
import requests
from datetime import datetime
from flask_cors import CORS  # Optional

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# MongoDB Atlas connection
client = MongoClient("mongodb+srv://Fehinti:Embrasebot@embrase.6qzd3hi.mongodb.net/")
db = client["chatbot"]
messages_collection = db["messages"]

# Endpoint to handle incoming messages
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

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

        bot_reply = bot_reply.strip()

        # Log bot response
        messages_collection.insert_one({
            "sender": "bot",
            "message": bot_reply,
            "timestamp": datetime.utcnow().isoformat()
        })

    else:
        bot_reply = "Sorry, I couldn't reach the Rasa server."

    return jsonify({"response": bot_reply})


# ✅ Endpoint to return chat history
@app.route('/history', methods=['GET'])
def get_chat_history():
    try:
        # Retrieve last 50 messages (oldest to newest)
        history_cursor = messages_collection.find().sort("timestamp", 1).limit(50)

        history = []
        for msg in history_cursor:
            history.append({
                "sender": msg.get("sender"),
                "message": msg.get("message"),
                "timestamp": msg.get("timestamp")
            })

        return jsonify(history)
    except Exception as e:
        return jsonify({"error": "Failed to fetch history", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
