import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './SensitiveLogs.css'; 

const SensitiveLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [role, setRole] = useState(localStorage.getItem('role'));

  useEffect(() => {
    if (role !== 'Admin') {
      setError('You do not have permission to access this page.');
      setLoading(false);
      return;
    }

    const fetchLogs = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/sensitive_logs');
        setLogs(response.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch sensitive data logs.');
        setLoading(false);
      }
    };

    fetchLogs();
  }, [role]);

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="container">
      <h1 className="title">Sensitive Data Logs</h1>
      <table className="logs-table">
        <thead>
          <tr className="table-header">
            <th>ID</th>
            <th>User ID</th>
            <th>Prompt</th>
            <th>Detected Data</th>
            <th>BERT Prediction</th>
            <th>FinBERT Prediction</th>
            <th>Zero-shot Prediction</th>
            <th>Is Sensitive</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log, index) => (
            <tr
              key={log.id}
              className={`table-row ${log.is_sensitive ? 'sensitive' : index % 2 === 0 ? 'even' : 'odd'}`}
            >
              <td>{log.id}</td>
              <td>{log.user_id}</td>
              <td>{log.prompt}</td>
              <td>{log.detected_data}</td>
              <td>{log.bert_prediction}</td>
              <td>{log.finbert_prediction}</td>
              <td>{log.zero_shot_prediction}</td>
              <td>{log.is_sensitive ? 'Yes' : 'No'}</td>
              <td>{log.timestamp}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default SensitiveLogs;