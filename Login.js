import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./Login.css";
import LoginImage from "../images/Login.png";
import config from "../config"; // Import the base URL

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [otpRequested, setOtpRequested] = useState(false);

  useEffect(() => {
    // Check if the user is already logged in
    const authToken = localStorage.getItem("auth_token");
    if (authToken) {
      // Redirect to Home page if logged in
      navigate("/home");
    }
  }, [navigate]);

  const handleEmailChange = (e) => {
    setEmail(e.target.value);
  };

  const handleOtpChange = (e) => {
    setOtp(e.target.value);
  };

  const handleSignIn = async () => {
    try {
      // Send login OTP request
      const response = await axios.post(`${config.BASE_URL}/login-request`, {
        email,
      });

      if (response.status === 200) {
        setOtpRequested(true); // Show OTP input field
      }
    } catch (error) {
      console.error("Error sending login request:", error);
      alert(error.response?.data?.detail || "Error sending login request");
    }
  };

  const handleVerifyOtp = async () => {
    try {
      // Send OTP verification request
      const response = await axios.post(`${config.BASE_URL}/verify-login-otp`, {
        email,
        otp: parseInt(otp),
      });

      if (response.status === 200) {
        // Save all user details to localStorage to persist login session
        for (const [key, value] of Object.entries(response.data)) {
          localStorage.setItem(key, value);
        }

        // Redirect to Home page
        navigate("/home");
      }
    } catch (error) {
      console.error("Error verifying OTP:", error);
      alert(error.response?.data?.detail || "Error verifying OTP");
    }
  };

  const handleSignUpClick = () => {
    // Redirect to the signup page
    navigate("/signup");
  };

  return (
    <div className="login-page">
      {/* Left-side Image Section */}
      <div className="login-image-container">
        <img src={LoginImage} alt="Background" className="login-image" />
      </div>

      {/* Right-side Login Form */}
      <div className="login-form-container">
        <div className="login-content">
          <h2>Welcome Back!</h2>
          <p>Enter your details below!</p>
          <form>
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={handleEmailChange}
              required
            />
            {otpRequested && (
              <input
                type="text"
                placeholder="One-time password"
                value={otp}
                onChange={handleOtpChange}
                required
              />
            )}
            {!otpRequested ? (
              <button type="button" onClick={handleSignIn}>
                Send OTP
              </button>
            ) : (
              <button type="button" onClick={handleVerifyOtp}>
                Verify OTP
              </button>
            )}
          </form>
          <div className="divider">
            <span>or</span>
          </div>
          <div className="extra-links">
            <a href="#" onClick={handleSignUpClick}>
              Sign Up
            </a>
            <span>|</span>
            <a href="#">Contact Us</a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
