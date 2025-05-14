import React, { useState, useEffect, useRef } from "react"; 
import axios from "axios"; 
import "./ChatInterface.css"; 

export default function ChatInterface() {
  const [message, setMessage] = useState(""); 
  const [messages, setMessages] = useState([]); 
  const [file, setFile] = useState(null); 
  const [role, setRole] = useState(null); 
  const [userId, setUserId] = useState(null); 
  const [isLoading, setIsLoading] = useState(false); 
  const chatBoxRef = useRef(null); 

  useEffect(() => {
    const userRole = localStorage.getItem("role");
    const storedUserId = localStorage.getItem("user_id");

    if (!userRole || !storedUserId) {
      window.location.href = "/"; 
    } else {
      setRole(userRole);
      setUserId(storedUserId);
    }
  }, []); 

  useEffect(() => {
    if (userId) {
      fetchChatHistory(userId);
    }
  }, [userId]); 

  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages]); 

  const fetchChatHistory = async (userId) => {
    try {
      const res = await axios.post("http://127.0.0.1:5000/history", { user_id: userId }, { withCredentials: true });
      res.data.reverse();
      const chatHistory = [];
      res.data.forEach(chat => {
        chatHistory.push({ role: "user", content: chat.question });
        chatHistory.push({ role: "assistant", content: chat.response });
      });
      setMessages(chatHistory);
    } catch (error) {
      console.error("Error fetching chat history:", error);
    }
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const sendMessage = async () => {
    if (!message && !file) return;

    setIsLoading(true);

    const formData = new FormData();
    formData.append("user_id", userId);
    formData.append("message", message);
    if (file) {
      formData.append("file", file);
    }

    try {
      const res = await axios.post("http://127.0.0.1:5000/chat", formData, { withCredentials: true });

      // Update messages with user's message
      const newMessages = [...messages, { role: "user", content: message || file.name }];
      // Add assistant's response
      newMessages.push({ role: "assistant", content: res.data.response });

      setMessages(newMessages);
      setMessage("");
      setFile(null);
    } catch (error) {
      console.error("Error sending message:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-wrapper">
      <div className="chat-container">
        <div className="chat-header">
          <h2>Chat Interface ({role})</h2>
          <button className="chat-logout" onClick={() => {
            localStorage.removeItem("role");
            localStorage.removeItem("user_id");
            window.location.href = "/";
          }}>
            Logout
          </button>
        </div>
        <div className="chat-box" ref={chatBoxRef}>
          {messages.map((msg, index) => (
            <div key={index} className={`chat-message ${msg.role}`}>
              {msg.content}
            </div>
          ))}
          {isLoading && <div className="chat-message assistant">Waiting For Response...</div>}
        </div>
        <div className="chat-input">
          <input
            type="text"
            placeholder="Type a message..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            disabled={isLoading}
          />
          <label htmlFor="file-upload">Choose file</label>
          <input id="file-upload" type="file" onChange={handleFileChange} disabled={isLoading} />
          <button onClick={sendMessage} disabled={isLoading}>Send</button>
        </div>
      </div>
    </div>
  );
}