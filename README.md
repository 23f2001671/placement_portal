# Institute Placement Portal
A full-stack web application designed to streamline the campus recruitment process. This platform connects Students, Companies, and the Admin in a centralized ecosystem.

# 1. Admin Dashboard
Approve or reject company registrations and job drives.

Activate/Deactivate student or company accounts (Soft Delete).

View real-time stats (Total students, pending approvals, etc.).

Filter students and companies by name or ID.

Delete Students/Companies from the database.

# 2. Company Dashboard
Create and edit job drives (Title, Description, Eligibility, Deadline).

View all students who applied to a specific drive.

Update student application status (Shortlisted, Selected, Rejected).

Update corporate details and HR contact info.

# 3. Student Dashboard
See approved companies and active placement drives.

Upload and update resumes (PDF/Doc).

Easy application process with duplicate prevention.

Real-time history of all applied drives and their current status.

# Tech Stack
Backend: Python (Flask)

Database: SQLite (SQLAlchemy ORM)

Frontend: Jinja2, HTML5, CSS3, Bootstrap 5

Session Management: Flask-Session with role-based access control

# Getting Started
Follow these steps to get the project running on your local machine.

1. Prerequisites
Ensure you have Python 3.x installed.

2. Setup Virtual Environment
Open your terminal in the project folder and run:

# Create the environment
python -m venv venv
# Activate it (Windows)
venv\Scripts\activate 
# Activate it (Mac/Linux)
source venv/bin/activate

3. Install Dependencies
pip install Flask Flask-SQLAlchemy

4. Initialize the Database
Before running the app, you need to create the database file and the default admin account:
python models.py
This will create a placement.db file and a default admin with:
Username: admin
Password: admin@321

5. Run the Application
python app.py
The app will be live at: http://127.0.0.1:5000

# Project Structure
Plaintext
├── app.py              # Main Flask Controller (Routes & Logic)
├── models.py           # Database Schema & Admin Initialization
├── placement.db        # SQLite Database (generated after run)
├── static/
│   ├── css/            # Custom Stylesheets
│   └── uploads/
│       └── resumes/    # Stored student resumes
└── templates/          # HTML files (Admin, Student, Company folders)

# Security & Logic Highlights
Soft Delete: Uses an is_active flag so data is never truly lost, only hidden.

Cache Control: Implemented headers to prevent "Back-button" access after logging out.

Relational Mapping: Used cascade="all, delete-orphan" to maintain database cleanliness.