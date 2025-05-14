import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./Logs.css";

export default function Logs() {
  const [logs, setLogs] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const userRole = localStorage.getItem("role");

    if (userRole !== "Admin") {
      alert("Access Denied! Only Admins can access this page.");
      navigate("/chat");
      return;
    }

    fetchLogs();
  }, [navigate]);

  const fetchLogs = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:5000/logs");
      setLogs(res.data);
    } catch (error) {
      console.error("Error fetching logs:", error);
    }
  };

  return (
    <div className="logs-container">
      <h2>📜 System Logs</h2>
      <table>
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Endpoint</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <tr key={log.id}>
              <td>{new Date(log.timestamp).toLocaleString()}</td>
              <td>{log.endpoint}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
