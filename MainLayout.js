import React, { useState } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import Sidebar from "./Sidebar";
import logo from "../images/logo.png"; // Adjust the path

const MainLayout = () => {
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const toggleDropdown = () => {
    setDropdownOpen(!dropdownOpen);
  };

  const handleLogout = () => {
    // Clear all data from localStorage
    localStorage.clear();

    // Redirect to login page
    navigate("/");
  };

  return (
    <div>
      <header
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "10px 20px",
          backgroundColor: "#f0f8ff", // Light blue color
          borderBottom: "1px solid #ddd",
          color: "#000",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <img
            src={logo} // logo picture
            alt="Logo"
            style={{ width: "130px", height: "30px" }}
          />
          <h1 style={{ margin: 0 }}></h1>
        </div>
        <div style={{ position: "relative" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              cursor: "pointer",
            }}
            onClick={toggleDropdown}
          >
            <span style={{ fontSize: "14px", color: "#000" }}>
              Welcome, {localStorage.getItem("first_name") || "User"}
            </span>
            <img
              src="https://via.placeholder.com/40" // profile picture
              alt="Profile"
              style={{
                width: "40px",
                height: "40px",
                borderRadius: "50%",
                border: "1px solid #ddd",
              }}
            />
          </div>
          {dropdownOpen && (
            <div
              style={{
                position: "absolute",
                top: "100%",
                right: 0,
                marginTop: "5px",
                padding: "10px",
                backgroundColor: "#fff",
                border: "1px solid #ddd",
                borderRadius: "5px",
                boxShadow: "0px 0px 10px rgba(0, 0, 0, 0.1)",
              }}
            >
              <button
                onClick={handleLogout}
                style={{
                  backgroundColor: "#f0f8ff",
                  border: "none",
                  padding: "5px 10px",
                  cursor: "pointer",
                  fontSize: "14px",
                }}
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </header>
      <div style={{ display: "flex" }}>
        <Sidebar />
        <div style={{ flex: 1, padding: "20px" }}>
          <Outlet /> {/* This is where the nested route content will be rendered */}
        </div>
      </div>
    </div>
  );
};

export default MainLayout;
