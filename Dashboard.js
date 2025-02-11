import React, { useState, useEffect } from "react";
import axios from "axios";
import "./Dashboard.css";
import config from "../config"; // Import the base URL

const Dashboard = ({ exam, onGoBack }) => {
  const [activeSection, setActiveSection] = useState("Student Management");
  const [students, setStudents] = useState([]);
  const [assessmentAttempted, setAssessmentAttempted] = useState([]);
  const [pendingApproval, setPendingApproval] = useState([]);
  const [assessmentsInvitation, setAssessmentsInvitation] = useState([]);
  const [assessmentPending, setAssessmentPending] = useState([]);
  const [mcqs, setMcqs] = useState([]);
  const [showAddQuestionForm, setShowAddQuestionForm] = useState(false);
  const [newQuestion, setNewQuestion] = useState({
    question: "",
    correct_ans: "",
    alt_a: "",
    alt_b: "",
    alt_c: "",
  });
  const [editingMcq, setEditingMcq] = useState(null);
  const [editedQuestion, setEditedQuestion] = useState({
    question: "",
    correct_ans: "",
    alt_a: "",
    alt_b: "",
    alt_c: "",
  });
  const [examTiming, setExamTiming] = useState(null);
  const [timingMessage, setTimingMessage] = useState("");
  const [timingInput, setTimingInput] = useState({
    start_date: "",
    start_time: "",
    end_date: "",
    end_time: "",
  });
  
  const handleSetExamTiming = async (e) => {
    e.preventDefault();
  
    const userId = localStorage.getItem("user_id");
    const authToken = localStorage.getItem("auth_token");
  
    const { start_date, start_time, end_date, end_time } = timingInput;
  
    // Validate input
    if (!start_date || !start_time || !end_date || !end_time) {
      alert("All fields are required.");
      return;
    }
  
    try {
      const response = await axios.post(`${config.BASE_URL}/set-exam-timing`, {
        user_id: parseInt(userId),
        auth_token : authToken,
        exam_id: exam.exam_id,
        start_date,
        start_time,
        end_date,
        end_time,
      });
  
      if (response.status === 200 && response.data.timing_details) {
        setExamTiming(response.data.timing_details); // Update the displayed timing
        alert("Exam timing updated successfully!");
      } else {
        alert(response.data.message || "Failed to update exam timing.");
      }
    } catch (error) {
      if (error.response && error.response.data.message) {
        alert(`Error: ${error.response.data.message}`);
      } else {
        alert("An unexpected error occurred while setting the exam timing.");
      }
    }
  };
  

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-GB"); // Format as DD/MM/YYYY
  };


  const fetchExamTiming = async () => {
    const userId = localStorage.getItem("user_id");
    const authToken = localStorage.getItem("auth_token");

    try {
      const response = await axios.post(`${config.BASE_URL}/fetch-exam-timing`, {
        user_id: parseInt(userId),
        auth_token: authToken,
        exam_id: exam.exam_id,
      });

      if (response.status === 200) {
        if (response.data.timing_details) {
          setExamTiming(response.data.timing_details);
          setTimingMessage(""); // Clear any previous messages
        } else {
          setExamTiming(null);
          setTimingMessage(response.data.message); // Set the message
        }
      }
    } catch (error) {
      if (error.response && error.response.data.message) {
        alert(`Error: ${error.response.data.message}`);
      } else {
        alert("An unexpected error occurred while fetching the exam timing.");
      }
    }
  };


  const handleEditQuestion = (mcq) => {
    setEditingMcq(mcq.mcq_id); // Set the ID of the MCQ being edited
    setEditedQuestion({
      question: mcq.question,
      correct_ans: mcq.correct_ans,
      alt_a: mcq.alt_a,
      alt_b: mcq.alt_b,
      alt_c: mcq.alt_c,
    });
  };

  const handleDeleteQuestion = async (mcqId) => {
    const userId = localStorage.getItem("user_id");
    const authToken = localStorage.getItem("auth_token");

    // Confirm deletion
    const confirmDelete = window.confirm("Are you sure you want to delete this question?");
    if (!confirmDelete) {
      return;
    }

    try {
      // API call to delete the question
      const response = await axios.delete(`${config.BASE_URL}/delete-mcq`, {
        data: {
          user_id: parseInt(userId),
          auth_token: authToken,
          mcq_id: mcqId,
        },
      });

      if (response.status === 200 && response.data.deleted_mcq) {
        const deletedMcqId = response.data.deleted_mcq.mcq_id;

        // Update local storage
        const storedMcqs = JSON.parse(localStorage.getItem("mcq_data")) || [];
        const updatedMcqs = storedMcqs.filter((mcq) => mcq.mcq_id !== deletedMcqId);
        localStorage.setItem("mcq_data", JSON.stringify(updatedMcqs));

        // Update the state
        setMcqs(updatedMcqs);

        alert("MCQ deleted successfully!");
      }
    } catch (error) {
      if (error.response && error.response.data.message) {
        alert(`Error: ${error.response.data.message}`);
      } else {
        alert("An unexpected error occurred while deleting the question.");
      }
    }
  };



  const handleSaveEditedQuestion = async (e) => {
    e.preventDefault(); // Prevent default form submission

    const userId = localStorage.getItem("user_id");
    const authToken = localStorage.getItem("auth_token");

    const { question, correct_ans, alt_a, alt_b, alt_c } = editedQuestion;

    // Validate inputs
    if (!question || !correct_ans || !alt_a || !alt_b || !alt_c) {
      alert("All fields are required.");
      return;
    }

    try {
      const response = await axios.put(`${config.BASE_URL}/update-mcq`, {
        user_id: parseInt(userId),
        auth_token: authToken,
        mcq_id: editingMcq,
        question, // Include the question field
        correct_ans,
        alt_a,
        alt_b,
        alt_c,
      });

      if (response.status === 200 && response.data.updated_mcq) {
        const updatedMcq = response.data.updated_mcq;

        // Update local storage
        const storedMcqs = JSON.parse(localStorage.getItem("mcq_data")) || [];
        const updatedMcqs = storedMcqs.map((mcq) =>
          mcq.mcq_id === updatedMcq.mcq_id
            ? {
              ...mcq,
              question: updatedMcq.question, // Update question field
              correct_ans: updatedMcq.correct_ans,
              alt_a: updatedMcq.alt_a,
              alt_b: updatedMcq.alt_b,
              alt_c: updatedMcq.alt_c,
            }
            : mcq
        );
        localStorage.setItem("mcq_data", JSON.stringify(updatedMcqs));
        setMcqs(updatedMcqs);

        // Reset editing state
        setEditingMcq(null);
        setEditedQuestion({
          question: "",
          correct_ans: "",
          alt_a: "",
          alt_b: "",
          alt_c: "",
        });

        alert("MCQ updated successfully!");
      }
    } catch (error) {
      if (error.response && error.response.data.message) {
        alert(`Error: ${error.response.data.message}`);
      } else {
        alert("An unexpected error occurred while updating the question.");
      }
    }
  };




  const handleAddQuestionSubmit = async (e) => {
    e.preventDefault(); // Prevent default form submission

    const userId = localStorage.getItem("user_id");
    const authToken = localStorage.getItem("auth_token");

    // Validate input
    const { question, correct_ans, alt_a, alt_b, alt_c } = newQuestion;
    if (!question || !correct_ans || !alt_a || !alt_b || !alt_c) {
      alert("All fields are required.");
      return;
    }

    try {
      const response = await axios.post(`${config.BASE_URL}/add-mcq`, {
        user_id: parseInt(userId),
        auth_token: authToken,
        exam_id: exam.exam_id,
        question,
        correct_ans,
        alt_a,
        alt_b,
        alt_c,
      });

      if (response.status === 200 && response.data.mcq_details) {
        const newMcq = response.data.mcq_details;

        // Update localstorage and state
        const storedMcqs = JSON.parse(localStorage.getItem("mcq_data")) || [];
        const updatedMcqs = [...storedMcqs, newMcq];
        localStorage.setItem("mcq_data", JSON.stringify(updatedMcqs));
        setMcqs(updatedMcqs);

        alert("MCQ added successfully!");

        // Reset form and hide it
        setNewQuestion({
          question: "",
          correct_ans: "",
          alt_a: "",
          alt_b: "",
          alt_c: "",
        });
        setShowAddQuestionForm(false);
      }
    } catch (error) {
      if (error.response && error.response.data.message) {
        alert(`Error: ${error.response.data.message}`);
      } else {
        alert("An unexpected error occurred while adding the question.");
      }
    }
  };



  // Function to fetch student data
  const fetchStudentData = async () => {
    const userId = localStorage.getItem("user_id");
    const authToken = localStorage.getItem("auth_token");

    try {
      const response = await axios.post(`${config.BASE_URL}/fetch-student-data`, {
        user_id: parseInt(userId),
        auth_token: authToken,
        exam_id: exam.exam_id,
      });

      if (response.status === 200 && response.data.students) {
        const studentsData = response.data.students;
        localStorage.setItem("student_data", JSON.stringify(studentsData));

        // Categorize students
        const attempted = [];
        const pending = [];
        const invitations = [];
        const assessmentPendingList = [];

        studentsData.forEach((student) => {
          if (
            student.is_attempted === 1 &&
            student.student_verify === 1 &&
            student.admin_verify === 1
          ) {
            attempted.push(student);
          } else if (
            student.is_attempted === 0 &&
            student.student_verify === 1 &&
            student.admin_verify === 0
          ) {
            pending.push(student);
          } else if (
            student.is_attempted === 0 &&
            student.student_verify === 0 &&
            student.admin_verify === 1
          ) {
            invitations.push(student);
          } else if (
            student.is_attempted === 0 &&
            student.student_verify === 1 &&
            student.admin_verify === 1
          ) {
            assessmentPendingList.push(student);
          }
        });

        setStudents(studentsData);
        setAssessmentAttempted(attempted);
        setPendingApproval(pending);
        setAssessmentsInvitation(invitations);
        setAssessmentPending(assessmentPendingList);
      }
    } catch (error) {
      console.error("Error fetching student data:", error);
    }
  };

  // Trigger API call when the dashboard loads if "Student Management" is active
  useEffect(() => {
    if (activeSection === "Student Management") {
      fetchStudentData();
    }
  }, [activeSection]);

  useEffect(() => {
    if (activeSection === "Assessment Management") {
      fetchExamTiming();
    }
  }, [activeSection]);


  useEffect(() => {
    const fetchMcqs = async () => {
      const userId = localStorage.getItem("user_id");
      const authToken = localStorage.getItem("auth_token");

      try {
        const response = await axios.post(`${config.BASE_URL}/fetch-mcq-admin`, {
          user_id: parseInt(userId),
          auth_token: authToken,
          exam_id: exam.exam_id,
        });

        if (response.status === 200 && response.data.mcqs) {
          const fetchedMcqs = response.data.mcqs;
          localStorage.setItem("mcq_data", JSON.stringify(fetchedMcqs));
          setMcqs(fetchedMcqs);
        }
      } catch (error) {
        console.error("Error fetching MCQs:", error);
      }
    };

    if (activeSection === "Question Management") {
      fetchMcqs();
    }
  }, [activeSection]);


  // Function to handle section selection
  const handleSectionClick = (section) => {
    setActiveSection(section);
  };

  const handleApprove = async (mappingId) => {
    const userId = localStorage.getItem("user_id");
    const authToken = localStorage.getItem("auth_token");

    try {
      const response = await axios.post(`${config.BASE_URL}/verify-student`, {
        user_id: parseInt(userId),
        auth_token: authToken,
        mapping_id: mappingId,
      });

      if (response.status === 200 && response.data.updated_details) {
        const updatedDetails = response.data.updated_details;

        // Update the data in localstorage
        const storedStudents = JSON.parse(localStorage.getItem("student_data")) || [];
        const updatedStudents = storedStudents.map((student) =>
          student.mapping_id === updatedDetails.mapping_id
            ? { ...student, admin_verify: updatedDetails.admin_verify }
            : student
        );

        localStorage.setItem("student_data", JSON.stringify(updatedStudents));

        // Re-categorize the updated data
        const attempted = [];
        const pending = [];
        const invitations = [];
        const assessmentPendingList = [];

        updatedStudents.forEach((student) => {
          if (
            student.is_attempted === 1 &&
            student.student_verify === 1 &&
            student.admin_verify === 1
          ) {
            attempted.push(student);
          } else if (
            student.is_attempted === 0 &&
            student.student_verify === 1 &&
            student.admin_verify === 0
          ) {
            pending.push(student);
          } else if (
            student.is_attempted === 0 &&
            student.student_verify === 0 &&
            student.admin_verify === 1
          ) {
            invitations.push(student);
          } else if (
            student.is_attempted === 0 &&
            student.student_verify === 1 &&
            student.admin_verify === 1
          ) {
            assessmentPendingList.push(student);
          }
        });

        // Update state with re-categorized data
        setStudents(updatedStudents);
        setAssessmentAttempted(attempted);
        setPendingApproval(pending);
        setAssessmentsInvitation(invitations);
        setAssessmentPending(assessmentPendingList);

        alert("Student successfully verified.");
      }
    } catch (error) {
      if (error.response && error.response.data.message) {
        alert(`Error: ${error.response.data.message}`);
      } else {
        alert("An unexpected error occurred while verifying the student.");
      }
    }
  };


  const handleDecline = async (mappingId) => {
    const userId = localStorage.getItem("user_id");
    const authToken = localStorage.getItem("auth_token");

    try {
      const response = await axios.post(`${config.BASE_URL}/remove-student`, {
        user_id: parseInt(userId),
        auth_token: authToken,
        mapping_id: mappingId,
      });

      if (response.status === 200 && response.data.deleted_data) {
        const deletedMappingId = response.data.deleted_data.mapping_id;

        // Remove the data from localstorage
        const storedStudents = JSON.parse(localStorage.getItem("student_data")) || [];
        const updatedStudents = storedStudents.filter(
          (student) => student.mapping_id !== deletedMappingId
        );

        localStorage.setItem("student_data", JSON.stringify(updatedStudents));

        // Re-categorize the updated data
        const attempted = [];
        const pending = [];
        const invitations = [];
        const assessmentPendingList = [];

        updatedStudents.forEach((student) => {
          if (
            student.is_attempted === 1 &&
            student.student_verify === 1 &&
            student.admin_verify === 1
          ) {
            attempted.push(student);
          } else if (
            student.is_attempted === 0 &&
            student.student_verify === 1 &&
            student.admin_verify === 0
          ) {
            pending.push(student);
          } else if (
            student.is_attempted === 0 &&
            student.student_verify === 0 &&
            student.admin_verify === 1
          ) {
            invitations.push(student);
          } else if (
            student.is_attempted === 0 &&
            student.student_verify === 1 &&
            student.admin_verify === 1
          ) {
            assessmentPendingList.push(student);
          }
        });

        // Update state with re-categorized data
        setStudents(updatedStudents);
        setAssessmentAttempted(attempted);
        setPendingApproval(pending);
        setAssessmentsInvitation(invitations);
        setAssessmentPending(assessmentPendingList);

        alert("Student removed successfully.");
      }
    } catch (error) {
      if (error.response && error.response.data.message) {
        alert(`Error: ${error.response.data.message}`);
      } else {
        alert("An unexpected error occurred while removing the student.");
      }
    }
  };


  const handleViewReport = (mappingId) => {
    alert(`Viewing report for student with mapping ID: ${mappingId}`);
    // Redirect to report or open modal for report viewing
  };

  const handleInviteExaminee = async () => {
    const adminId = localStorage.getItem("user_id");
    const adminAuthToken = localStorage.getItem("auth_token");
    const studentId = prompt("Enter Examinee's ID:");

    if (!studentId) {
      alert("Examinee ID is required.");
      return;
    }

    try {
      const response = await axios.post(`${config.BASE_URL}/add-student`, {
        admin_id: parseInt(adminId),
        admin_auth_token: adminAuthToken,
        student_id: parseInt(studentId),
        exam_id: exam.exam_id,
      });

      if (response.status === 200 && response.data.mapping_details) {
        const newMapping = response.data.mapping_details;
        const newStudentDetails = response.data.student_details;

        // Add the new mapping and student details to localstorage
        const storedStudents = JSON.parse(localStorage.getItem("student_data")) || [];
        const updatedStudents = [
          ...storedStudents,
          {
            mapping_id: newMapping.mapping_id,
            exam_id: newMapping.exam_id,
            user_id: newMapping.student_id,
            admin_verify: newMapping.admin_verify,
            student_verify: newMapping.student_verify,
            is_attempted: newMapping.is_attempted,
            first_name: newStudentDetails.first_name,
            last_name: newStudentDetails.last_name,
            email: newStudentDetails.email,
          },
        ];

        localStorage.setItem("student_data", JSON.stringify(updatedStudents));

        // Re-categorize the updated data
        const attempted = [];
        const pending = [];
        const invitations = [];
        const assessmentPendingList = [];

        updatedStudents.forEach((student) => {
          if (
            student.is_attempted === 1 &&
            student.student_verify === 1 &&
            student.admin_verify === 1
          ) {
            attempted.push(student);
          } else if (
            student.is_attempted === 0 &&
            student.student_verify === 1 &&
            student.admin_verify === 0
          ) {
            pending.push(student);
          } else if (
            student.is_attempted === 0 &&
            student.student_verify === 0 &&
            student.admin_verify === 1
          ) {
            invitations.push(student);
          } else if (
            student.is_attempted === 0 &&
            student.student_verify === 1 &&
            student.admin_verify === 1
          ) {
            assessmentPendingList.push(student);
          }
        });

        // Update state with re-categorized data
        setStudents(updatedStudents);
        setAssessmentAttempted(attempted);
        setPendingApproval(pending);
        setAssessmentsInvitation(invitations);
        setAssessmentPending(assessmentPendingList);

        alert("Student successfully added to the exam.");
      }
    } catch (error) {
      if (error.response && error.response.data.message) {
        alert(`Error: ${error.response.data.message}`);
      } else {
        alert("An unexpected error occurred while inviting the examinee.");
      }
    }
  };


  return (
    <div className="dashboard-container">
      <button onClick={onGoBack} className="go-back-button">
        Go Back
      </button>
      <div className="dashboard-header">
        <h1>{exam.exam_name}</h1>
        <p>Code: {exam.exam_code}</p>
      </div>
      <div className="dashboard-sidebar">
        <ul>
          <li
            className={activeSection === "Student Management" ? "active" : ""}
            onClick={() => handleSectionClick("Student Management")}
          >
            Student Management
          </li>
          <li
            className={activeSection === "Question Management" ? "active" : ""}
            onClick={() => handleSectionClick("Question Management")}
          >
            Question Management
          </li>
          <li
            className={activeSection === "Assessment Management" ? "active" : ""}
            onClick={() => handleSectionClick("Assessment Management")}
          >
            Assessment Management
          </li>
        </ul>
      </div>
      <div className="dashboard-content">
        <h2>{activeSection}</h2>

        {activeSection === "Student Management" && (
  <>
    <div className="student-section">
      <h3>Assessment Attempted</h3>
      {assessmentAttempted.length > 0 ? (
        assessmentAttempted.map((student) => (
          <div key={student.mapping_id} className="student-card">
            <p>
              <strong>Name:</strong> {student.first_name} {student.last_name}
            </p>
            <p>
              <strong>Email:</strong> {student.email}
            </p>
            <p>
              <strong>User ID:</strong> {student.user_id}
            </p>
            <button
              className="view-report-button"
              onClick={() => handleViewReport(student.mapping_id)}
            >
              View Report
            </button>
          </div>
        ))
      ) : (
        <p>No assessments attempted are available.</p>
      )}
    </div>

    <div className="student-section">
      <h3>Pending Approval</h3>
      {pendingApproval.length > 0 ? (
        pendingApproval.map((student) => (
          <div key={student.mapping_id} className="student-card">
            <p>
              <strong>Name:</strong> {student.first_name} {student.last_name}
            </p>
            <p>
              <strong>Email:</strong> {student.email}
            </p>
            <p>
              <strong>User ID:</strong> {student.user_id}
            </p>
            <button
              className="approve-button"
              onClick={() => handleApprove(student.mapping_id)}
            >
              Approve
            </button>
            <button
              className="decline-button"
              onClick={() => handleDecline(student.mapping_id)}
            >
              Decline
            </button>
          </div>
        ))
      ) : (
        <p>No students are pending approval.</p>
      )}
    </div>

    <div className="student-section">
      <h3>Assessments Invitation</h3>
      <button
        className="invite-examinee-button"
        onClick={handleInviteExaminee}
      >
        Invite Examinee
      </button>
      {assessmentsInvitation.length > 0 ? (
        assessmentsInvitation.map((student) => (
          <div key={student.mapping_id} className="student-card">
            <p>
              <strong>Name:</strong> {student.first_name} {student.last_name}
            </p>
            <p>
              <strong>Email:</strong> {student.email}
            </p>
            <p>
              <strong>User ID:</strong> {student.user_id}
            </p>
          </div>
        ))
      ) : (
        <p>No assessment invitations are available.</p>
      )}
    </div>

    <div className="student-section">
      <h3>Assessment Pending</h3>
      {assessmentPending.length > 0 ? (
        assessmentPending.map((student) => (
          <div key={student.mapping_id} className="student-card">
            <p>
              <strong>Name:</strong> {student.first_name} {student.last_name}
            </p>
            <p>
              <strong>Email:</strong> {student.email}
            </p>
            <p>
              <strong>User ID:</strong> {student.user_id}
            </p>
          </div>
        ))
      ) : (
        <p>No pending assessments are available.</p>
      )}
    </div>
  </>
)}

        {activeSection === "Question Management" && (
          <div className="mcq-section">
            {mcqs.map((mcq, index) => (
              <div key={mcq.mcq_id} className="mcq-block">

                {editingMcq === mcq.mcq_id ? (
                  <form onSubmit={handleSaveEditedQuestion} className="edit-question-form">
                    <input
                      type="text"
                      value={editedQuestion.question}
                      onChange={(e) =>
                        setEditedQuestion({ ...editedQuestion, question: e.target.value })
                      }
                      required
                    />
                    <input
                      type="text"
                      value={editedQuestion.correct_ans}
                      onChange={(e) =>
                        setEditedQuestion({ ...editedQuestion, correct_ans: e.target.value })
                      }
                      required
                    />
                    <input
                      type="text"
                      value={editedQuestion.alt_a}
                      onChange={(e) =>
                        setEditedQuestion({ ...editedQuestion, alt_a: e.target.value })
                      }
                      required
                    />
                    <input
                      type="text"
                      value={editedQuestion.alt_b}
                      onChange={(e) =>
                        setEditedQuestion({ ...editedQuestion, alt_b: e.target.value })
                      }
                      required
                    />
                    <input
                      type="text"
                      value={editedQuestion.alt_c}
                      onChange={(e) =>
                        setEditedQuestion({ ...editedQuestion, alt_c: e.target.value })
                      }
                      required
                    />
                    <div className="form-buttons">
                      <button type="submit" className="save-question-button">
                        Save
                      </button>
                      <button
                        type="button"
                        className="cancel-question-button"
                        onClick={() => setEditingMcq(null)}
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                ) : (
                  <>
                    <p>
                      <strong style={{ color: "brown" }}>Q-{index + 1}) Question:</strong> {mcq.question}
                    </p>
                    <p>
                      <strong style={{ color: "green" }}>Correct Answer:</strong> {mcq.correct_ans}
                    </p>
                    <p>
                      <strong style={{ color: "blue" }}>Option A:</strong> {mcq.alt_a}
                    </p>
                    <p>
                      <strong style={{ color: "blue" }}>Option B:</strong> {mcq.alt_b}
                    </p>
                    <p>
                      <strong style={{ color: "blue" }}>Option C:</strong> {mcq.alt_c}
                    </p>
                    <button
                      className="update-button"
                      onClick={() => handleEditQuestion(mcq)}
                    >
                      Update
                    </button>
                    <button
                      className="delete-button"
                      onClick={() => handleDeleteQuestion(mcq.mcq_id)}
                    >
                      Delete
                    </button>
                  </>
                )}
              </div>
            ))}

            {showAddQuestionForm ? (
              <form onSubmit={handleAddQuestionSubmit} className="add-question-form">
                <h3>Add New Question</h3>
                <input
                  type="text"
                  placeholder="Enter the question"
                  value={newQuestion.question}
                  onChange={(e) => setNewQuestion({ ...newQuestion, question: e.target.value })}
                  required
                />
                <input
                  type="text"
                  placeholder="Enter the correct answer"
                  value={newQuestion.correct_ans}
                  onChange={(e) => setNewQuestion({ ...newQuestion, correct_ans: e.target.value })}
                  required
                />
                <input
                  type="text"
                  placeholder="Enter option A"
                  value={newQuestion.alt_a}
                  onChange={(e) => setNewQuestion({ ...newQuestion, alt_a: e.target.value })}
                  required
                />
                <input
                  type="text"
                  placeholder="Enter option B"
                  value={newQuestion.alt_b}
                  onChange={(e) => setNewQuestion({ ...newQuestion, alt_b: e.target.value })}
                  required
                />
                <input
                  type="text"
                  placeholder="Enter option C"
                  value={newQuestion.alt_c}
                  onChange={(e) => setNewQuestion({ ...newQuestion, alt_c: e.target.value })}
                  required
                />
                <div className="form-buttons">
                  <button type="submit" className="save-question-button">
                    Save
                  </button>
                  <button
                    type="button"
                    className="cancel-question-button"
                    onClick={() => setShowAddQuestionForm(false)}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            ) : (
              <button
                className="add-question-button"
                onClick={() => setShowAddQuestionForm(true)}
              >
                Add New Question
              </button>
            )}

          </div>
        )}
        {activeSection === "Assessment Management" && (
  <div className="assessment-management-section">
    <h3>Exam Timing</h3>
    {examTiming ? (
      <div>
        <p>
          <strong>Start Date:</strong> {formatDate(examTiming.start_date)}
        </p>
        <p>
          <strong>Start Time:</strong> {examTiming.start_time}
        </p>
        <p>
          <strong>End Date:</strong> {formatDate(examTiming.end_date)}
        </p>
        <p>
          <strong>End Time:</strong> {examTiming.end_time}
        </p>
      </div>
    ) : (
      <p>{timingMessage || "Timing is not set. Please set the timing."}</p>
    )}

    <h3>Set Exam Timing</h3>
    <form onSubmit={handleSetExamTiming}>
      <label>
        Start Date:
        <input
          type="date"
          value={timingInput.start_date}
          onChange={(e) =>
            setTimingInput({ ...timingInput, start_date: e.target.value })
          }
          required
        />
      </label>
      <label>
        Start Time (HH:MM:SS):
        <input
          type="time"
          step="1" // Enable seconds input
          value={timingInput.start_time}
          onChange={(e) =>
            setTimingInput({ ...timingInput, start_time: e.target.value })
          }
          required
        />
      </label>
      <label>
        End Date:
        <input
          type="date"
          value={timingInput.end_date}
          onChange={(e) =>
            setTimingInput({ ...timingInput, end_date: e.target.value })
          }
          required
        />
      </label>
      <label>
        End Time (HH:MM:SS):
        <input
          type="time"
          step="1" // Enable seconds input
          value={timingInput.end_time}
          onChange={(e) =>
            setTimingInput({ ...timingInput, end_time: e.target.value })
          }
          required
        />
      </label>
      <button type="submit">Update Timing</button>
    </form>
  </div>
)}

      </div>
    </div>
  );
};

export default Dashboard;
