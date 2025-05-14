// Import React, hooks, and other necessary libraries
import React, { useEffect, useState } from "react";   
import { useNavigate } from "react-router-dom"; 
import axios from "axios";  
import "./Rules.css"; 

// Rules component where the admin can manage sensitive data rules
export default function Rules() {
  // State variables for managing rules and input field for adding new rules
  const [rules, setRules] = useState([]); 
  const [newRule, setNewRule] = useState(""); 
  const navigate = useNavigate(); 
  // Effect hook to check if the user has admin privileges and fetch rules data
  useEffect(() => {
    const userRole = localStorage.getItem("role"); 

    // If the user is not an admin, redirect to the chat page and show an alert
    if (userRole !== "Admin") {
      alert("Access Denied! Only Admins can access this page.");
      navigate("/chat"); 
      return;
    }

    // Fetch the rules when the component is mounted
    fetchRules();
  }, [navigate]); 
  // Function to fetch the current rules from the backend
  const fetchRules = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:5000/rules");  
      setRules(res.data); // Update the state with the fetched rules
    } catch (error) {
      console.error("Error fetching rules:", error); 
    }
  };

  // Function to add a new rule
  const addRule = async () => {
    if (!newRule) return; // Prevent adding an empty rule
    try {
      // Making POST request to add a new rule
      await axios.post("http://127.0.0.1:5000/rules/add", { rule: newRule });
      setNewRule(""); // 
      fetchRules(); // 
    } catch (error) {
      console.error("Error adding rule:", error); // Handle any errors that occur during the request
    }
  };

  // Function to delete an existing rule
  const deleteRule = async (ruleId) => {
    try {
      // Making POST request to delete the rule by its ID
      await axios.post("http://127.0.0.1:5000/rules/delete", { id: ruleId });
      fetchRules(); // 
    } catch (error) {
      console.error("Error deleting rule:", error); // 
  };
  }
  return (
    <div className="rules-container">
      <h2>⚙️ Sensitive Data Rules</h2> {/* Title of the page */}
      
      {/* Form for adding new rules */}
      <div className="rules-form">
        <input
          type="text"
          value={newRule}
          onChange={(e) => setNewRule(e.target.value)}  // 
          placeholder="Enter a new sensitive rule..."  //
        />
        <button onClick={addRule}>Add Rule</button> {/* Button to add the new rule */}
      </div>
      
      {/* Table to display current rules */}
      <table>
        <thead>
          <tr>
            <th>Rule</th>  {/* Column for the rule description */}
            <th>Actions</th>  {/* Column for action buttons */}
          </tr>
        </thead>
        <tbody>
          {/* Map over each rule and display in the table */}
          {rules.map((rule) => (
            <tr key={rule.id}>
              <td>{rule.rule}</td>  {/* Display the rule */}
              <td>
                <button onClick={() => deleteRule(rule.id)}>🗑️ Delete</button>  {/* Delete button for each rule */}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
