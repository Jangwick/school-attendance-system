# School Attendance System

A web-based application built with Flask and modern frontend technologies to streamline the process of marking and managing student attendance using QR codes.

## Overview

This system allows teachers to manage their assigned subjects, view enrolled students, generate unique QR codes for each student, and mark attendance efficiently by scanning these QR codes using a webcam. It also provides reporting features to track attendance trends and individual student performance.

## Features

-   **User Authentication:** Secure login for teachers using email and password.
-   **Dashboard:** Overview of assigned subjects, total students, and quick links.
-   **Subject Management:** Displays subjects assigned to the logged-in teacher.
-   **Student Management:**
    -   View all students in the system.
    -   View students enrolled in a specific subject.
    -   Add, Edit, and Delete student records.
    -   Search functionality for students.
-   **QR Code Generation:** Generate unique QR codes based on student School IDs.
    -   Display QR codes in a modal or dedicated page.
    -   Download QR code as a PNG image.
    -   Print QR code.
-   **QR Code Scanning:** Use the device camera (webcam) to scan student QR codes for attendance marking.
    -   Real-time feedback on successful scans or errors (e.g., student not found, already marked).
    -   Cooldown period to prevent accidental double scans.
    -   Visual confirmation with student details upon successful scan.
-   **Manual Attendance Marking:** Option to manually mark students present from the attendance dashboard.
-   **Attendance Dashboard:**
    -   View daily attendance summary (present vs. total).
    -   Visualize weekly attendance trends with charts.
    -   Display attendance distribution (present/absent) for the day.
    -   Show top-performing students based on attendance rate.
-   **Reporting:**
    -   Generate detailed attendance reports per subject.
    -   View attendance status (Present/Absent) for each student across all class dates.
    -   Calculate and display individual student attendance percentages.
    -   Calculate overall subject average attendance.
    -   Categorize students based on attendance percentage (Perfect, Good, Warning, Critical).
    -   Export reports to Excel (.xlsx) format.
-   **Responsive Design:** User interface adapts to different screen sizes (desktop, tablet, mobile).
-   **Toast Notifications:** User-friendly feedback for actions like adding/updating/deleting students or marking attendance.
-   **Modals:** Used for displaying QR codes, adding/editing students, and confirming deletions.

## Technology Stack

-   **Backend:** Python, Flask
    -   **Database:** SQLAlchemy ORM, SQLite
    -   **Authentication:** Flask-Login
    -   **QR Code:** `qrcode` library
-   **Frontend:**
    -   HTML5
    -   Tailwind CSS (via CDN with `@tailwindcss/browser`)
    -   JavaScript (Vanilla JS)
    -   **Charting:** Chart.js
    -   **QR Scanning:** `jsQR` library
    -   **Excel Export:** SheetJS (xlsx)
    -   **Icons:** Bootstrap Icons
-   **Development Server:** Werkzeug (Flask's built-in server)

## Project Structure

```
├── instance/
│   └── database.db         # SQLite database file
├── static/                 # Static files (CSS, JS, Images) - Currently minimal as using CDNs
├── templates/
│   ├── attendance/         # Attendance marking, scanning, dashboard templates
│   │   ├── dashboard.html
│   │   ├── mark.html
│   │   └── scan.html
│   ├── auth/               # Authentication templates
│   │   └── login.html
│   ├── charts/             # Reusable chart components
│   │   ├── attendance_distribution.html
│   │   ├── student_performance.html
│   │   └── weekly_trend.html
│   ├── dashboard/          # Main dashboard template
│   │   └── index.html
│   ├── includes/           # Reusable HTML snippets (e.g., navbar)
│   │   └── navbar.html
│   ├── layouts/            # Base layout template
│   │   └── base.html
│   ├── modals/             # Modal dialog templates
│   │   ├── add_student_modal.html
│   │   ├── edit_student_modal.html
│   │   └── qr_code_modal.html
│   ├── reports/            # Report templates
│   │   ├── index.html
│   │   └── subject.html
│   └── students/           # Student listing and QR code templates
│       ├── by_subject.html
│       ├── index.html
│       └── qr_code.html
├── app.py                  # Main Flask application file (routes, logic)
├── config.py               # Flask configuration settings (e.g., SECRET_KEY, DB URI)
├── models.py               # Database models (User, Student, Subject, Attendance, etc.)
├── README.md               # This file
├── requirements.txt        # Python dependencies
└── utils.py                # Utility functions (e.g., adding sample data)
```

## Installation and Setup

1.  **Clone the Repository:**
    ```bash
    git clone <repository-url>
    cd "scan mo login"
    ```

2.  **Create and Activate Virtual Environment:**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: `opencv-python` and `pyzbar` might have system-level dependencies. If installation fails, consult their respective documentation for prerequisites on your OS.)*

4.  **Configure:**
    -   Review `config.py`. Ensure `SECRET_KEY` is set to a strong, unique value, especially for production.
    -   The `SQLALCHEMY_DATABASE_URI` is set for SQLite by default (`sqlite:///instance/database.db`).

5.  **Run the Application:**
    ```bash
    flask run
    # or
    python app.py
    ```
    The application will initialize the database and add sample data on the first run.

6.  **Access the Application:**
    Open your web browser and navigate to `http://127.0.0.1:5000` (or the address provided by Flask).

## Usage

1.  **Login:** Use the demo credentials provided on the login page (`john.smith@school.edu` / `password123`) or credentials for any user created in `utils.py`.
2.  **Dashboard:** View your assigned subjects.
3.  **Students:**
    -   Navigate to the "Students" section to see all students.
    -   Click "Add Student" to add new students and assign them to subjects.
    -   Use the Edit/Delete buttons on each student row.
    -   Click "QR Code" to view/print/download a student's QR code.
4.  **Subject View:** Click a subject on the dashboard to see students enrolled in that specific subject.
5.  **Attendance Dashboard:** Access via the subject view. See charts and manually mark attendance.
6.  **Scan QR:** Access via the subject view or attendance dashboard. Start the camera and scan student QR codes.
7.  **Reports:**
    -   Navigate to the "Reports" section.
    -   Search for subjects.
    -   Click on a subject to view the detailed attendance report.
    -   Use the "Export to Excel" button.

## Database

-   The application uses SQLite by default, storing the database file in the `instance/` folder.
-   The database schema is defined in `models.py`.
-   The database is created automatically on the first request if it doesn't exist (`db.create_all()` in `app.py`).
-   Sample data (users, subjects, students, assignments) is added via `utils.add_sample_data()` for demonstration purposes.

## Key Libraries Used

-   **Flask:** Micro web framework for Python.
-   **Flask-SQLAlchemy:** ORM for database interaction.
-   **Flask-Login:** Handles user sessions and authentication.
-   **Werkzeug:** Provides security functions (password hashing) and the development server.
-   **qrcode[pil]:** Generates QR code images.
-   **jsQR:** JavaScript library for decoding QR codes from camera streams.
-   **Chart.js:** JavaScript library for creating charts.
-   **SheetJS (xlsx):** JavaScript library for generating Excel files.