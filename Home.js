import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Home.css";

export const Home = () => {
  const navigate = useNavigate();
  const [userName, setUserName] = useState("Guest");

  useEffect(() => {
    // Check if the user is logged in
    const authToken = localStorage.getItem("auth_token");
    if (!authToken) {
      navigate("/login");
    } else {
      // Retrieve the user's name (fallback to "Guest" if not available)
      const storedUserName = localStorage.getItem("user_name") || "Guest";
      setUserName(storedUserName);
    }
  }, [navigate]);

  return (
    <div className="dashboard-container">
     
      <main className="dashboard-main">
        <div className="Header_UwU" align="left">
        <h1 className="welcome">Welcome, {userName}</h1>
        <p className="description">
          Give your assessments seamlessly and in a user-friendly way!
        </p>
        </div>
    

        <div className="grid-container">
          <div className="grid-item">
            <div className="grid-icon">01.</div>
            <p className="grid-label">Assessment</p>
          </div>
          <div className="grid-item">
            <div className="grid-icon">02.</div>
            <p className="grid-label">Viva</p>
          </div>
          <div className="grid-item">
            <div className="grid-icon">03.</div>
            <p className="grid-label">My Dashboard</p>
          </div>
          <div className="grid-item">
            <div className="grid-icon">04.</div>
            <p className="grid-label">Results</p>
          </div>
          <div className="grid-item">
            <div className="grid-icon">05.</div>
            <p className="grid-label">My Profile</p>
          </div>
          <div className="grid-item">
            <div className="grid-icon">06.</div>
            <p className="grid-label">Settings</p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Home;
