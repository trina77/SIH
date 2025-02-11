import React from "react";

const Banner = () => {
  return (
    <div style={{ display: "flex", gap: "20px" }}>
      <div style={{ flex: 1, backgroundColor: "#f0f8ff", padding: "20px", borderRadius: "8px" }}>
        <h3>Launchpad is now LIVE</h3>
        <p>Upskill, Practice & Crack a Job</p>
        <ul>
          <li>1700+ Job Opportunities</li>
          <li>50+ Practice Tests</li>
          <li>1000+ Free Certificate Courses</li>
        </ul>
        <button style={{ padding: "10px 20px", backgroundColor: "#007bff", color: "#fff", border: "none", borderRadius: "5px" }}>Visit Launchpad Now</button>
      </div>
      <div style={{ flex: 1, backgroundColor: "#fff0f5", padding: "20px", borderRadius: "8px" }}>
        <h3>Create a job-winning resume in minutes</h3>
        <button style={{ padding: "10px 20px", backgroundColor: "#007bff", color: "#fff", border: "none", borderRadius: "5px" }}>Try Now</button>
      </div>
    </div>
  );
};

export default Banner;
