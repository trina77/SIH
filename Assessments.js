import React, { useEffect, useState } from "react";
import axios from "axios";
import config from "../config";
import "./Assessments.css";
import Dashboard from "./Dashboard";

const Assessments = () => {
  const [exams, setExams] = useState([]);
  const [pastAssessments, setPastAssessments] = useState([]);
  const [upcomingAssessments, setUpcomingAssessments] = useState([]);
  const [pendingVerifications, setPendingVerifications] = useState([]);
  const [assessmentInvitations, setAssessmentInvitations] = useState([]);
  const [showDashboard, setShowDashboard] = useState(false);
  const [message, setMessage] = useState("");
  const [dashboardExam, setDashboardExam] = useState(null);

  const pwdStatus = parseInt(localStorage.getItem("pwd_status"), 10);
  const pwdType = localStorage.getItem("pwd_type");

  useEffect(() => {
    const role = localStorage.getItem("role");
    const userId = localStorage.getItem("user_id");
    const authToken = localStorage.getItem("auth_token");
  
    const fetchExams = async () => {
      try {
        // Fetch logic remains unchanged
      } catch (error) {
        // Error handling logic remains unchanged
      }
    };
  
    fetchExams();
  
    // Play speech on page load
    if (pwdStatus === 1 && pwdType === "PwBD 1") {
      const speech = new SpeechSynthesisUtterance("Attempt any active assessment.");
      speechSynthesis.speak(speech);
    }
  }, [pwdStatus, pwdType]);
  


  useEffect(() => {
    const role = localStorage.getItem("role");
    const userId = localStorage.getItem("user_id");
    const authToken = localStorage.getItem("auth_token");

    const fetchExams = async () => {
      try {
        let response;
        if (role === "admin") {
          response = await axios.post(`${config.BASE_URL}/fetch-exam-admin`, {
            user_id: userId,
            auth_token: authToken,
          });

          if (response.status === 200 && response.data.exams) {
            setExams(response.data.exams);
            localStorage.setItem("exams", JSON.stringify(response.data.exams));
          }
        } else if (role === "user") {
          response = await axios.post(`${config.BASE_URL}/fetch-exam-student`, {
            user_id: userId,
            auth_token: authToken,
          });

          if (response.status === 200 && response.data.exams) {
            const fetchedExams = response.data.exams;
            localStorage.setItem("exams", JSON.stringify(fetchedExams));

            const past = [];
            const upcoming = [];
            const pending = [];
            const invitations = [];

            fetchedExams.forEach((exam) => {
              if (
                exam.is_attempted === 1 &&
                exam.admin_verify === 1 &&
                exam.student_verify === 1
              ) {
                past.push(exam);
              } else if (
                exam.is_attempted === 0 &&
                exam.admin_verify === 1 &&
                exam.student_verify === 1
              ) {
                upcoming.push(exam);
              } else if (
                exam.admin_verify === 0 &&
                exam.student_verify === 1
              ) {
                pending.push(exam);
              } else if (
                exam.admin_verify === 1 &&
                exam.student_verify === 0
              ) {
                invitations.push(exam);
              }
            });

            setPastAssessments(past);
            setUpcomingAssessments(upcoming);
            setPendingVerifications(pending);
            setAssessmentInvitations(invitations);
          }
        }
      } catch (error) {
        setExams([]);
        setPastAssessments([]);
        setUpcomingAssessments([]);
        setPendingVerifications([]);
        setAssessmentInvitations([]);
      }
    };

    fetchExams();
  }, []);

  // Function to handle creating a new assessment
  const handleCreateAssessment = async () => {
    const examName = prompt("Enter the Exam Name:");
    if (!examName) {
      alert("Exam name is required.");
      return;
    }

    const userId = localStorage.getItem("user_id");
    const authToken = localStorage.getItem("auth_token");

    try {
      const response = await axios.post(`${config.BASE_URL}/create-exam`, {
        user_id: userId,
        auth_token: authToken,
        exam_name: examName,
      });

      if (response.status === 200) {
        const newExam = response.data;
        const updatedExams = [...exams, newExam];
        setExams(updatedExams);
        localStorage.setItem("exams", JSON.stringify(updatedExams));
        alert("Exam created successfully!");
      }
    } catch (error) {
      alert("An unexpected error occurred while creating the exam.");
    }
  };

  // Function to handle deleting an assessment
  const handleDeleteAssessment = async (examId) => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete this exam?"
    );
    if (!confirmDelete) {
      return;
    }

    const userId = localStorage.getItem("user_id");
    const authToken = localStorage.getItem("auth_token");

    try {
      const response = await axios.delete(`${config.BASE_URL}/delete-exam`, {
        data: {
          user_id: userId,
          auth_token: authToken,
          exam_id: examId,
        },
      });

      if (response.status === 200) {
        const updatedExams = exams.filter((exam) => exam.exam_id !== examId);
        setExams(updatedExams);
        localStorage.setItem("exams", JSON.stringify(updatedExams));
        alert("Exam deleted successfully!");
      }
    } catch (error) {
      alert("An unexpected error occurred while deleting the exam.");
    }
  };

  // Function to handle going to the dashboard

  const handleGoToDashboard = (exam) => {
    setDashboardExam(exam);
    setShowDashboard(true);
  };

  // Function to handle going back from the dashboard
  const handleGoBack = () => {
    setShowDashboard(false);
  };


  // If the user is an admin, show the dashboard
  if (showDashboard) {
    return <Dashboard exam={dashboardExam} onGoBack={handleGoBack} />;
  }



  // Function to handle enrolling in an assessment
  const handleEnrollAssessment = async () => {
    const examCode = prompt("Enter the Exam Code:");
    if (!examCode) {
      alert("Exam code is required.");
      return;
    }

    const userId = localStorage.getItem("user_id");
    const authToken = localStorage.getItem("auth_token");

    try {
      const response = await axios.post(`${config.BASE_URL}/enroll-exam`, {
        user_id: userId,
        auth_token: authToken,
        exam_code: examCode,
      });

      if (response.status === 200 && response.data.enrollment_details) {
        const newEnrollment = response.data.enrollment_details;

        // Add the complete enrollment to Pending Verification section
        const updatedPendingVerifications = [
          ...pendingVerifications,
          newEnrollment,
        ];
        setPendingVerifications(updatedPendingVerifications);

        // Store updated exam data in localStorage
        const storedExams = JSON.parse(localStorage.getItem("exams")) || [];
        const newExamsList = [...storedExams, newEnrollment];
        localStorage.setItem("exams", JSON.stringify(newExamsList));

        alert(
          "Successfully enrolled in the exam! Waiting for examiner verification."
        );
      }
    } catch (error) {
      if (error.response && error.response.data.detail) {
        alert(error.response.data.detail);
      } else {
        alert("An unexpected error occurred while enrolling in the exam.");
      }
    }
  };



  // Function to handle declining an assessment
  const handleDeclineAssessment = async (mappingId) => {
    const confirmDecline = window.confirm(
      "Are you sure you want to decline this assessment?"
    );
    if (!confirmDecline) {
      return;
    }

    const userId = localStorage.getItem("user_id");
    const authToken = localStorage.getItem("auth_token");

    try {
      const response = await axios.post(`${config.BASE_URL}/unenroll-exam`, {
        user_id: userId,
        auth_token: authToken,
        mapping_id: mappingId,
      });

      if (response.status === 200 && response.data.deleted_data) {
        const updatedInvitations = assessmentInvitations.filter(
          (exam) => exam.mapping_id !== mappingId
        );
        setAssessmentInvitations(updatedInvitations);

        const storedExams = JSON.parse(localStorage.getItem("exams")) || [];
        const updatedExamsList = storedExams.filter(
          (exam) => exam.mapping_id !== mappingId
        );
        localStorage.setItem("exams", JSON.stringify(updatedExamsList));

        alert("Successfully unenrolled from the exam.");
      }
    } catch (error) {
      if (error.response && error.response.data.detail) {
        alert(error.response.data.detail);
      } else {
        alert("An unexpected error occurred while declining the assessment.");
      }
    }
  };

  // Function to handle accepting an assessment
  const handleAcceptAssessment = async (mappingId) => {
    const userId = localStorage.getItem("user_id");
    const authToken = localStorage.getItem("auth_token");

    // Check if user ID and auth token are available
    if (!userId || !authToken) {
      alert("User is not authenticated.");
      return;
    }

    // Prepare the request payload
    const payload = {
      user_id: parseInt(userId),  // Ensure user_id is a number
      auth_token: authToken,
      mapping_id: mappingId,
    };

    try {
      // Make the POST request to verify the exam
      const response = await axios.post("http://127.0.0.1:8000/api/verify-exam", payload, {
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (response.status === 200 && response.data.updated_details) {
        const updatedExam = response.data.updated_details;

        // Filter out the accepted exam from the "Assessment Invitations" category
        const updatedInvitations = assessmentInvitations.filter(
          (exam) => exam.mapping_id !== mappingId
        );
        setAssessmentInvitations(updatedInvitations);

        // Update the exams list in local storage with updated student_verify
        const storedExams = JSON.parse(localStorage.getItem("exams")) || [];
        const updatedExamsList = storedExams.map((exam) =>
          exam.mapping_id === mappingId
            ? { ...exam, student_verify: 1 }  // Set student_verify to 1
            : exam
        );
        localStorage.setItem("exams", JSON.stringify(updatedExamsList));

        // Re-categorize exams based on updated local storage
        const fetchedExams = JSON.parse(localStorage.getItem("exams")) || [];

        // Re-categorize exams into past, upcoming, pending, invitations
        const past = [];
        const upcoming = [];
        const pending = [];
        const invitations = [];

        fetchedExams.forEach((exam) => {
          if (
            exam.is_attempted === 1 &&
            exam.admin_verify === 1 &&
            exam.student_verify === 1
          ) {
            past.push(exam);
          } else if (
            exam.is_attempted === 0 &&
            exam.admin_verify === 1 &&
            exam.student_verify === 1
          ) {
            upcoming.push(exam);
          } else if (
            exam.admin_verify === 0 &&
            exam.student_verify === 1
          ) {
            pending.push(exam);
          } else if (
            exam.admin_verify === 1 &&
            exam.student_verify === 0
          ) {
            invitations.push(exam);
          }
        });

        // Update states with the new categorized exams
        setPastAssessments(past);
        setUpcomingAssessments(upcoming);
        setPendingVerifications(pending);
        setAssessmentInvitations(invitations);

        alert("Exam successfully verified!");
      }
    } catch (error) {
      if (error.response && error.response.data.detail) {
        alert(error.response.data.detail);
      } else {
        alert("An unexpected error occurred while accepting the assessment.");
      }
    }
  };



  return (
    <div className="assessments-container">
      <h1>Assessments</h1>

      {localStorage.getItem("role") === "user" && (
        <button
          className="enroll-assessment-button"
          onClick={handleEnrollAssessment}
        >
          Enroll in Assessment
        </button>
      )}

      {localStorage.getItem("role") === "admin" && (
        <button
          className="create-assessment-button"
          onClick={handleCreateAssessment}
        >
          Create Assessment
        </button>
      )}

      {localStorage.getItem("role") === "admin" && (
        <div className="exam-blocks-container">
          {exams.length > 0 ? (
            exams.map((exam) => (
              <div key={exam.exam_id} className="exam-block">
                <h3>{exam.exam_name}</h3>
                <p>Code: {exam.exam_code}</p>
                <button
                  className="dashboard-button"
                  onClick={() => handleGoToDashboard(exam)}
                >
                  Go to Dashboard
                </button>

                <button
                  className="delete-button"
                  onClick={() => handleDeleteAssessment(exam.exam_id)}
                >
                  Delete
                </button>
              </div>
            ))
          ) : (
            <p>No assessments available.</p>
          )}
        </div>
      )}

      {localStorage.getItem("role") === "user" && (
        <>
          {pastAssessments.length > 0 ? (
            <div className="assessment-section">
              <h2>Past Assessments</h2>
              <div className="exam-blocks-container">
                {pastAssessments.map((exam) => (
                  <div key={exam.mapping_id} className="exam-block">
                    <h3>{exam.exam_name}</h3>
                    <p>Code: {exam.exam_code}</p>
                    <button className="dashboard-button">View Report</button>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p>No past assessments available.</p>
          )}

          {upcomingAssessments.length > 0 ? (
            <div className="assessment-section">
              <h2>Upcoming Assessments</h2>
              <div className="exam-blocks-container">
                {upcomingAssessments.map((exam) => (
                  <div key={exam.mapping_id} className="exam-block">
                    <h3>{exam.exam_name}</h3>
                    <p>Code: {exam.exam_code}</p>
                    <button className="dashboard-button">Start Assessment</button>
                    <button className="admit-card-button">View Admit Card</button>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p>No upcoming assessments available.</p>
          )}

          {pendingVerifications.length > 0 ? (
            <div className="assessment-section">
              <h2>Pending Verification</h2>
              <div className="exam-blocks-container">
                {pendingVerifications.map((exam) => (
                  <div key={exam.mapping_id} className="exam-block">
                    <h3>{exam.exam_name}</h3>
                    <p>Code: {exam.exam_code}</p>
                    <p className="verification-pending-label">
                      Examiner verification pending!
                    </p>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p>No pending verifications available.</p>
          )}

          {assessmentInvitations.length > 0 ? (
            <div className="assessment-section">
              <h2>Assessment Invitations</h2>
              <div className="exam-blocks-container">
                {assessmentInvitations.map((exam) => (
                  <div key={exam.mapping_id} className="exam-block">
                    <h3>{exam.exam_name}</h3>
                    <p>Code: {exam.exam_code}</p>
                    <div className="invitation-buttons">
                    <button
                        className="accept-button"
                        onClick={() => handleAcceptAssessment(exam.mapping_id)}
                      >
                        Accept
                      </button>
                      <button
                        className="decline-button"
                        onClick={() => handleDeclineAssessment(exam.mapping_id)}
                      >
                        Decline
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p>No assessment invitations available.</p>
          )}
        </>
      )}
    </div>
  );
};

export default Assessments;