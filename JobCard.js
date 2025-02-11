import React from "react";

const JobCard = () => {
  const jobDetails = {
    title: "WELCOME TO VIDYA SATHI",
    description: "Advancing Inclusive Education",
    courses: [
      "Vidyasath is a pioneering online assessment platform developed to ensure equitable access to learning and evaluation for all individuals, irrespective of physical or cognitive challenges",
      "By integrating state-of-the-art technology with a steadfast commitment to inclusivity, our platform is dedicated to providing comprehensive support to students with special needs, empowering them to achieve academic excellence",
      "For Students: Empowering you with the tools to demonstrate your knowledge and skills in a manner that suits your abilities",
      "For Educators: Offering an efficient, inclusive way to assess and support your students, with robust tracking and reporting tools",
      "For Institutions: A scalable solution for schools, universities, and training centers to offer inclusive education that meets modern standards."
    ],
  };

  return (
    <div style={{ border: "1px solid #ddd", borderRadius: "8px", padding: "20px", marginBottom: "20px" }}>
      <h2>{jobDetails.title}</h2>
      <p>{jobDetails.description}</p>
      <h3>Our Mission
      </h3>
      <ul>
        {jobDetails.courses.map((course, index) => (
          <li key={index}>{course}</li>
        ))}
      </ul>
    </div>
  );
};

export default JobCard;
