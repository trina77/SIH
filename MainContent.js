import React from "react";
import JobCard from "./JobCard";
import Banner from "./Banner";

const MainContent = () => {
  return (
    <div style={{ flex: 1, padding: "20px" }}>
      <JobCard />
      <Banner />
    </div>
  );
};

export default MainContent;
