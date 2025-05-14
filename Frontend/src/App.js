import React from "react";
import Authentication from "./authentication"; 
import ChatInterface from "./ChatInterface"; 
import Dashboard from "./Dashboard"; 
import Queries from "./Queries"; 
import Rules from "./Rules"; 
import Logs from "./Logs"; 
import Performance from "./Performance"; 
import AdminNavbar from "./AdminNavbar"; 
import SensitiveLogs from "./SensitiveLogs"; 
import { BrowserRouter as Router, Route, Routes } from "react-router-dom"; 

function App() {
  return (
    <Router> 
       <AdminNavbar /> 
      <Routes> 
        {/* Default route, renders the Authentication component for login */}
        <Route path="/" element={<Authentication />} />
        
        {/* Route for the Chat Interface component where users interact with the AI */}
        <Route path="/chat" element={<ChatInterface />} />
        
        {/* Admin dashboard route */}
        <Route path="/dashboard" element={<Dashboard />} />
        
        {/* Query monitoring for admins */}
        <Route path="/queries" element={<Queries />} />
        
        {/* Route for rule management where admins can add/edit rules */}
        <Route path="/rules" element={<Rules />} />
        
        {/* Route for viewing logs related to the backend operations */}
        <Route path="/logs" element={<Logs />} />
        
        {/* Performance monitoring of AI models, accessible by admins */}
        <Route path="/performance" element={<Performance />} />
        
        {/* Route to view sensitive data logs (admin view) */}
        <Route path="/sensitive-logs" element={<SensitiveLogs />} />
      </Routes>
    </Router> 
  );
}

export default App; 
