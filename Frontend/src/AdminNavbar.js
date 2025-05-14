import React from "react";
import { Link, useNavigate } from "react-router-dom"; 
import "./AdminNavbar.css"; 

export default function AdminNavbar() {
  const navigate = useNavigate();

  // Gets the user role from localStorage to check if the user is an Admin
  const role = localStorage.getItem("role");

  // If the user is not an Admin, return null to hide the navbar
  if (role !== "Admin") {
    return null; 
  }

  // Handles the logout functionality when the logout button is clicked
  const handleLogout = () => {
    // Removes the role and user_id from localStorage to log out the user
    localStorage.removeItem("role");
    localStorage.removeItem("user_id");

    // User navigates to redirect to the homepage or login page after logout
    navigate("/");
  };

  return (
    <nav className="admin-navbar"> {/* The container for the navbar */}
      <h2>Admin Panel</h2> {/* Title for the Admin Panel */}
      
      <ul> {}
        <li><Link to="/dashboard">Dashboard</Link></li> {/* Link to the Admin Dashboard */}
        <li><Link to="/queries">Query Monitoring</Link></li> {/* Link to monitor queries */}
        <li><Link to="/rules">Rules Management</Link></li> {/* Link to manage rules */}
        <li><Link to="/logs">API Logs</Link></li> {/* Link to view API logs */}
        <li><Link to="/performance">AI Performance</Link></li> {/* Link to check AI model performance */}
        <li><Link to="/sensitive-logs">Sensitive Data</Link></li> {/* Link to view sensitive data logs */}
      </ul>

      {/* Button to log out the admin */}
      <button onClick={handleLogout} className="logout-button">Logout</button>
    </nav>
  );
}

