import React from "react";
import "./AdmitCard.css"; // Optional CSS for styling the card.
import Alogo from "../images/Alogo.png";

const AdmitCard = () => {
  return (
    <div className="admit-card">
      <header className="admit-card-header">
        <img
          src={Alogo}
          alt="Vidyasathi Logo"
          className="admit-card-logo"
        />
        <h1>Admit Card</h1>
        <div className="photo-id-placeholder">Photo ID</div>
      </header>
      <section className="admit-card-details">
        <h2>Candidate Details</h2>
        <p><strong>Candidate Name:</strong> </p>
        <p><strong>Date of Birth:</strong> </p>
        <p><strong>Roll No:</strong></p>
      </section>
      <section className="exam-details">
        <h2>Exam Details</h2>
        <p><strong>Exam Date:</strong> </p>
        <p><strong>Reporting Time:</strong> </p>
        <p><strong>Gate Closure:</strong> </p>
        <p><strong>Exam Timing:</strong> </p>
        <p><strong>Test Center:</strong> </p>
      </section>
      <section className="general-instructions">
        <h2>General Instructions</h2>
        <ol>
          <li>
            The Hall Ticket must be presented for verification along with one
            original photo identification (not photocopy or scanned copy).
            Examples of acceptable photo identification documents are School ID,
            College ID, Employee ID, Driving License, Passport, PAN card, Voter
            ID, Aadhaar-ID. A printed copy of the hall ticket and original photo
            ID card should be brought to the exam center. Hall ticket and ID
            card copies on the phone will not be permitted.
          </li>
          <li>
            This Hall Ticket is valid only if the candidate's photograph and
            signature images are legible. To ensure this, print the Hall Ticket
            on A4-sized paper using a laser printer, preferably a color photo
            printer.
          </li>
          <li>
            <strong>Timeline:</strong> 1:00 PM - Report to the examination venue
            | 1:40 PM - Candidates will be permitted to occupy their allotted
            seats | 1:50 PM - Candidates can log in and start reading
            instructions prior to the examination | 2:00 PM - Exam starts | 2:30
            PM - Gate closes, candidates will not be allowed after this time |
            3:30 PM Submit button will be enabled | 5:00 PM - Exam ends.
          </li>
          <li>
            Candidates will be permitted to appear for the examination ONLY
            after their credentials are verified by center officials.
          </li>
          <li>
            Candidates are advised to locate the examination center at least a
            day prior to the examination, so they can reach the center on time.
          </li>
          <li>
            Stationery Requirements:
            <ul>
              <li>
                A4 sheets will be provided to candidates for rough work.
                Candidates have to write their name and registration number on
                the A4 Sheets before they start using them. The A4 sheets must
                be returned to the invigilator at the end of the examination.
              </li>
              <li>
                On-screen calculator will be available during the exam.
                Candidates are advised to familiarize themselves with this
                virtual Scientific calculator well ahead of the exam.
              </li>
              <li>
                Bring your own pen/pencil; it will NOT be given at the
                examination center.
              </li>
            </ul>
          </li>
          <li>
            Dress Code: Candidates are expected to come in professional attire
            to write the exams. Candidates wearing SHORTS will NOT be permitted
            inside the exam hall.
          </li>
          <li>
            Mandatory: Hall tickets have to be returned to the invigilator
            before leaving the exam hall. No paper can be taken out of the exam
            hall.
          </li>
        </ol>
      </section>
      <footer className="admit-card-footer">
        <p>
          <strong>Note:</strong> This admit card must be presented for
          verification along with one original photo ID.
        </p>
        <p>© 2024 Vidyasathi</p>
      </footer>
    </div>
  );
};

export default AdmitCard;
