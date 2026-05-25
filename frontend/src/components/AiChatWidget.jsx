import React, { useState } from 'react';
import './AiChatWidget.css';

export default function AiChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  
  // We start with one default greeting from the AI
  const [messages, setMessages] = useState([
    { sender: 'ai', text: "Hi! I'm the NextGen AI. Tell me your skills, and I'll recommend the best country for your profile!" }
  ]);

  const toggleChat = () => setIsOpen(!isOpen);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    const userMessage = inputText;
    setMessages(prevMessages => [...prevMessages, { sender: 'user', text: userMessage }]);
    setInputText('');
    
    // 1. TURN ON TYPING INDICATOR
    setIsTyping(true); 

    try {
      const response = await fetch('https://nextgen-api-11jg.onrender.com/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage }),
      });

      const data = await response.json();
      setMessages(prevMessages => [...prevMessages, { sender: 'ai', text: data.reply }]);
      
    } catch (error) {
      console.error("Chat error:", error);
      setMessages(prevMessages => [...prevMessages, { sender: 'ai', text: "Sorry, my brain is offline right now!" }]);
    } finally {
      // 2. TURN OFF TYPING INDICATOR
      setIsTyping(false); 
    }
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
            
            {isTyping && (
              <div className="message ai-message typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            )}
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