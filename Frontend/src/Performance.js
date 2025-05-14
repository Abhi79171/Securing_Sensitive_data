import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./Performance.css";

export default function Performance() {
  const [metrics, setMetrics] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const userRole = localStorage.getItem("role");

    if (userRole !== "Admin") {
      alert("Access Denied! Only Admins can access this page.");
      navigate("/chat");
      return;
    }

    fetchMetrics();
  }, [navigate]);

  const fetchMetrics = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:5000/performance");
      console.log("Backend response:", res.data); 
      setMetrics(res.data);
    } catch (error) {
      console.error("Error fetching performance metrics:", error);
    }
  };

  return (
    <div className="performance-container">
      <h2>📊 AI Model Performance</h2>
      {metrics ? (
        <table>
          <thead>
            <tr>
              <th>Model</th>
              <th>Accuracy</th>
              <th>Precision</th>
              <th>Recall</th>
              <th>F1 Score</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(metrics).map(([model, scores]) => (
              <tr key={model}>
                <td>{model}</td>
                <td>{scores.accuracy.toFixed(2)}</td>
                <td>{scores.precision.toFixed(2)}</td>
                <td>{scores.recall.toFixed(2)}</td>
                <td>{scores.f1_score.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p>Loading metrics...</p>
      )}
    </div>
  );
}