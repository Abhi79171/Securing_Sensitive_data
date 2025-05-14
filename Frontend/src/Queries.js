import React, { useEffect, useState } from "react"; 
import { useNavigate } from "react-router-dom"; 
import axios from "axios"; 
import "./Queries.css"; 

export default function Queries() {
  const [queries, setQueries] = useState([]); // State to store the list of queries fetched from the server
  const navigate = useNavigate(); // Hook to navigate programmatically based on certain conditions

  // useEffect hook to verify if the user is an Admin and fetch queries
  useEffect(() => {
    const userRole = localStorage.getItem("role"); // Retrieve role from localStorage

    if (userRole !== "Admin") {
      alert("Access Denied! Only Admins can access this page.");
      navigate("/chat"); // Redirect to the chat page if the user is not an admin
      return;
    }

    fetchQueries(); // If the user is admin, fetch queries data
    const interval = setInterval(fetchQueries, 10000); // Fetch queries every 10 seconds
    return () => clearInterval(interval); // Clear the interval when the component is unmounted
  }, [navigate]); 

  // Function to fetch queries from the server
  const fetchQueries = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:5000/queries"); // Fetch queries from backend
      setQueries(res.data); // Set the fetched queries into the state
    } catch (error) {
      console.error("Error fetching queries:", error); // Handle any errors that occur while fetching data
    }
  };

  return (
    <div className="queries-container">
      <h2>〽️ Query Monitoring</h2> 
      
      <table>
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Question</th>
            <th>Response</th>
          </tr>
        </thead>
        <tbody>
          {queries.map((query, index) => (
            <tr key={index}>
              <td>{new Date(query.timestamp).toLocaleString()}</td>
              <td>{query.question}</td>
              <td>{query.response}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
