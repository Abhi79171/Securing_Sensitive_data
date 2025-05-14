import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom"; 
import axios from "axios";
import "./Dashboard.css";

export default function Dashboard() {
  const [users, setUsers] = useState([]);
  const navigate = useNavigate(); 

  useEffect(() => {
    const userRole = localStorage.getItem("role");

    if (userRole !== "Admin") {
      alert("Access Denied! Only Admins can access this page.");
      navigate("/chat");
      return;
    }

    fetchUsers();
  }, [navigate]);

  const fetchUsers = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:5000/users");
      setUsers(res.data);
    } catch (error) {
      console.error("Error fetching users:", error);
    }
  };

  const approveUser = async (userId) => {
    await axios.post("http://127.0.0.1:5000/users/approve", { user_id: userId });
    fetchUsers();
  };

  const blockUser = async (userId) => {
    await axios.post("http://127.0.0.1:5000/users/block", { user_id: userId });
    fetchUsers();
  };

  const unblockUser = async (userId) => {
    await axios.post("http://127.0.0.1:5000/users/unblock", { user_id: userId });
    fetchUsers();
  };

  return (
    <div className="dashboard-container">
      <h2>Admin Dashboard</h2>

      <div className="section">
        <h3>👤 User Management</h3>
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Approval</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id}>
                <td>{user.first_name} {user.last_name}</td>
                <td>{user.email}</td>
                <td>{user.role}</td>
                <td>{user.is_approved ? "✅ Approved" : "⏳ Pending"}</td>
                <td>{user.is_blocked ? "🚫 Blocked" : "🟢 Active"}</td>
                <td>
                  {!user.is_approved && <button onClick={() => approveUser(user.id)}>Approve</button>}
                  {user.is_blocked ? (
                    <button onClick={() => unblockUser(user.id)}>Unblock</button>
                  ) : (
                    <button onClick={() => blockUser(user.id)}>Block</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
