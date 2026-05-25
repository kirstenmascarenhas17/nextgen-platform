import React, { useState } from 'react';
import './AiChatWidget.css';

export default function AiChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [inputText, setInputText] = useState('');
  
  // We start with one default greeting from the AI
  const [messages, setMessages] = useState([
    { sender: 'ai', text: "Hi! I'm the NextGen AI. Tell me your skills, and I'll recommend the best country for your profile!" }
  ]);

  const toggleChat = () => setIsOpen(!isOpen);

  const handleSend = (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    // Add user message to the chat
    setMessages([...messages, { sender: 'user', text: inputText }]);
    setInputText('');
    
    // We will wire this up to your FastAPI Gemini backend in the next step!
  };

  return (
    <div className="chat-widget-container">
      {/* The Chat Window (Only shows if isOpen is true) */}
      {isOpen && (
        <div className="chat-window">
          <div className="chat-header">
            <h3>NextGen AI Assistant</h3>
            <button onClick={toggleChat} className="close-btn">✖</button>
          </div>
          
          <div className="chat-body">
            {messages.map((msg, index) => (
              <div key={index} className={`message ${msg.sender === 'ai' ? 'ai-message' : 'user-message'}`}>
                {msg.text}
              </div>
            ))}
          </div>

          <form onSubmit={handleSend} className="chat-footer">
            <input 
              type="text" 
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Ask for advice..." 
            />
            <button type="submit">Send</button>
          </form>
        </div>
      )}

      {/* The Floating Button */}
      {!isOpen && (
        <button onClick={toggleChat} className="floating-chat-btn">
          💬 Chat with AI
        </button>
      )}
    </div>
  );
}