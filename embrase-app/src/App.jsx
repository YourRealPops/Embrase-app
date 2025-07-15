import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Load chat history on component mount
  useEffect(() => {
    fetchChatHistory();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchChatHistory = async () => {
    try {
      const response = await fetch('http://localhost:5000/history');
      const data = await response.json();

      // Reconstruct chat message flow: user → bot → user → bot
      const reconstructedMessages = [];
      for (let i = 0; i < data.length; i++) {
        const msg = data[i];
        reconstructedMessages.push({
          text: msg.message,
          isBot: msg.sender === "bot",
        });
      }

      setMessages(reconstructedMessages);
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();

    if (!inputText.trim()) return;

    const userMessage = { text: inputText, isBot: false };
    setMessages(prev => [...prev, userMessage]);
    const currentInputText = inputText;
    setInputText('');
    setIsTyping(true);

    try {
      const response = await fetch('http://localhost:5000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: currentInputText }),
      });

      const data = await response.json();

      setMessages(prev => [
        ...prev,
        { text: data.response, isBot: true }
      ]);

    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [
        ...prev,
        {
          text: "I'm sorry, I'm having trouble responding right now. Please try again later.",
          isBot: true
        }
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Your Friendly Chatbot</h1>
        <p>A safe space to talk about how you're feeling</p>
      </header>

      <div className="chat-container">
        <div className="messages-container">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`message ${message.isBot ? 'bot-message' : 'user-message'}`}
            >
              <div className="message-bubble">
                {message.text}
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="message bot-message">
              <div className="message-bubble typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form className="input-area" onSubmit={handleSendMessage}>
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Type your message here..."
            className="message-input"
          />
          <button type="submit" className="send-button">Send</button>
        </form>
      </div>

      <footer className="app-footer">
        <p>
          This is not a substitute for professional mental health support.
          Call your local emergency number if you're in crisis.
        </p>
      </footer>
    </div>
  );
}

export default App;
