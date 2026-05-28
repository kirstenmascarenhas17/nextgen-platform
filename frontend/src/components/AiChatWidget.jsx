import React, { useState, useEffect } from 'react';
import './AiChatWidget.css';

export default function AiChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isConnecting, setIsConnecting] = useState(true); 
  
  const [messages, setMessages] = useState([
    { sender: 'ai', text: "Hi! I'm the NextGen AI. Tell me your skills, and I'll recommend the best country for your profile!" }
  ]);

  // ✨ NEW: Helper function to get or create a unique user ID
  const getSessionId = () => {
    let sessionId = localStorage.getItem('nextgen_session_id');
    if (!sessionId) {
      // Create a random ID like 'user_x7b39m'
      sessionId = 'user_' + Math.random().toString(36).substring(2, 15);
      localStorage.setItem('nextgen_session_id', sessionId);
    }
    return sessionId;
  };

  useEffect(() => {
    const fetchHistory = async () => {
      const sessionId = getSessionId(); // Grab the user's nametag

      try {
        // ✨ NEW: Ask the backend ONLY for this specific user's history
        const response = await fetch(`https://nextgen-api-11jg.onrender.com/chat?session_id=${sessionId}`);
        const data = await response.json();
        
        if (data.messages && data.messages.length > 0) {
          const pastMessages = data.messages.map(msg => ({
            sender: msg.sender,
            text: msg.text
          }));
          
          setMessages([
            { sender: 'ai', text: "Hi! I'm the NextGen AI. Tell me your skills, and I'll recommend the best country for your profile!" },
            ...pastMessages
          ]);
        }
      } catch (error) {
        console.error("Failed to load chat history:", error);
      } finally {
        setIsConnecting(false);
      }
    };

    fetchHistory();
  }, []);

  const toggleChat = () => setIsOpen(!isOpen);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    const userMessage = inputText;
    const sessionId = getSessionId(); // Grab the user's nametag

    setMessages(prevMessages => [...prevMessages, { sender: 'user', text: userMessage }]);
    setInputText('');
    setIsTyping(true); 

    try {
      const response = await fetch('https://nextgen-api-11jg.onrender.com/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        // ✨ NEW: Attach the nametag to the message payload
        body: JSON.stringify({ message: userMessage, session_id: sessionId }),
      });

      const data = await response.json();
      setMessages(prevMessages => [...prevMessages, { sender: 'ai', text: data.reply }]);
      
    } catch (error) {
      console.error("Chat error:", error);
      setMessages(prevMessages => [...prevMessages, { sender: 'ai', text: "Sorry, my brain is offline right now!" }]);
    } finally {
      setIsTyping(false); 
    }
  };

  return (
    <div className="chat-widget-container">
      {isOpen && (
        <div className="chat-window">
          <div className="chat-header">
            <h3>NextGen AI Assistant</h3>
            <button onClick={toggleChat} className="close-btn">✖</button>
          </div>
          
          <div className="chat-body">
            {isConnecting && (
              <div className="connecting-overlay">
                <div className="spinner"></div>
                <h4>Waking up the AI...</h4>
                <p>Want highly personalized advice?</p>
                <button className="promo-btn">Register Your Profile</button>
              </div>
            )}

            {!isConnecting && messages.map((msg, index) => (
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
              disabled={isConnecting} 
            />
            <button type="submit" disabled={isConnecting}>Send</button>
          </form>
        </div>
      )}

      {!isOpen && (
        <button onClick={toggleChat} className="floating-chat-btn">
          💬 Chat with AI
        </button>
      )}
    </div>
  );
}