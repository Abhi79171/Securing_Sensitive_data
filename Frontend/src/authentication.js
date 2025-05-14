import React, { useState } from "react"; 
import axios from "axios"; 
import "./authentication.css"; 

export default function Authentication() {

  const [isRegistering, setIsRegistering] = useState(false); 
  const [form, setForm] = useState({ first_name: "", last_name: "", email: "", password: "" }); 
  const [message, setMessage] = useState(""); 

  // Function to handle input changes and update the form state
  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value }); 
  };

  // Function to handle user registration
  const register = async () => {
    try {
      const registrationData = { ...form, role: "Employee" }; // Adding default role as Employee
      const res = await axios.post("http://127.0.0.1:5000/register", registrationData, { withCredentials: true }); // Sending the registration data to the server
      setMessage(res.data.message); // Show server response message
      setIsRegistering(false); // Switch to login form after successful registration
    } catch (error) {
      setMessage(error.response?.data?.error || "Error registering"); // Show error message if registration fails
    }
  };

  // Function to handle user login
  const login = async () => {
    try {
      const res = await axios.post("http://127.0.0.1:5000/login", { email: form.email, password: form.password }, { withCredentials: true }); // Sending login credentials to the server
      setMessage(res.data.message); // Show server response message
      
      // If login is successful, store user data in local storage and redirect to the appropriate page
      if (res.data.role) {
        localStorage.setItem("role", res.data.role); 
        localStorage.setItem("user_id", res.data.id);
        if (res.data.role === "Employee") {
          window.location.href = "/chat"; // Redirects to chat for employees
        } else {
          window.location.href = "/dashboard"; // Redirect to dashboard for admins
        }
      } else {
        setMessage("Login failed. No role assigned."); // Shows error if no role is assigned
      }
    } catch (error) {
      setMessage(error.response?.data?.error || "Login failed"); // Shows error message if login fails
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-wrapper">
        <h2 className="auth-title">{isRegistering ? "Register" : "Login"}</h2> {/* Toggles the form title based on the isRegistering state */}
        
        <form
          onSubmit={(e) => {
            e.preventDefault(); // Prevents page reload on form submission
            isRegistering ? register() : login(); // Calls register or login based on the current form state
          }}
        >
          {isRegistering && ( // If registering, show additional fields for first name and last name
            <>
              <input
                type="text"
                name="first_name"
                placeholder="First Name"
                value={form.first_name}
                onChange={handleChange}
                className="auth-input"
                required
              />
              <input
                type="text"
                name="last_name"
                placeholder="Last Name"
                value={form.last_name}
                onChange={handleChange}
                className="auth-input"
                required
              />
            </>
          )}
  
          {/* Input fields for email and password (common for both login and register) */}
          <input
            type="email"
            name="email"
            placeholder="Email"
            value={form.email}
            onChange={handleChange}
            className="auth-input"
            required
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            value={form.password}
            onChange={handleChange}
            className="auth-input"
            required
          />
  
          {/* Submit button that changes text based on the current form state */}
          <button type="submit" className="auth-button">
            {isRegistering ? "Register" : "Login"}
          </button>
        </form>
  
        {/* Toggle between login and registration forms */}
        <p className="auth-toggle" onClick={() => setIsRegistering(!isRegistering)}>
          {isRegistering ? "Already have an account? Login" : "Don't have an account? Register"}
        </p>
        {/* Display any messages (e.g., errors or success) */}
        <p className="auth-message">{message}</p>
      </div>
    </div>
  );
}
