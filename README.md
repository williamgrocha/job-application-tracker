# APPLIED: A Strategic Job Application Tracker
#### Video Demo: <Link to your YouTube Video>

## Visual Overview

### 📊 The Intelligence Hub (Dashboard)
![Dashboard Overview](link_da_sua_imagem_aqui)
*Real-time metrics and pipeline snapshots to monitor your search progress.*

### 📋 Application Management
![Application List](link_da_sua_imagem_aqui)
*A clean, organized view of active and closed job opportunities.*

### ➕ Streamlined Onboarding
![Add New Application](link_da_sua_imagem_aqui)
*Intuitive forms designed for speed and data accuracy.*

### 👤 Login and Register
![Login & Register](link_da_sua_imagem_aqui)
*Intuitive forms designed for speed and data accuracy.*

---
#### Description:
**Applied** is a comprehensive web-based application designed to solve "Job Search Fatigue"—the chaotic process of managing dozens of job applications across multiple platforms. Developed as the Final Project for **CS50x 2026**, this tool allows developers and professionals to track their career progress with a data-driven approach, moving beyond simple lists into a functional pipeline management system.

The core philosophy of the project is to provide a "Single Source of Truth" for a candidate's journey. By utilizing a **Python and Flask** backend combined with a relational **SQLite** database, the application ensures that every interaction—from saving a job post to receiving an offer—is recorded, categorized, and analyzed.

### Key Features and Functionality

* **Smart Dashboard:** Unlike a static list, the Dashboard provides immediate high-level metrics. It calculates the total volume of applications, tracks weekly velocity (how many jobs were applied to in the last 7 days), and displays a "Pipeline Snapshot" to show exactly where the bottlenecks are (e.g., many "Saved" jobs but few "Interviews").
* **Application Lifecycle Management:** Users can create, read, update, and delete (CRUD) job entries. Each entry includes critical data points such as company name, job title, salary (formatted in BRL), work category (Remote, Hybrid, On-site), and deadlines.
* **Status History Tracking:** One of the most advanced features of the system is the `last_status` table. Whenever a user updates the status of a job (e.g., from "Applied" to "Interviewing"), the system logs this change. This allows the dashboard to generate insights into how many interviews the user has *ever* secured, providing a more accurate picture of their success rate over time.
* **Relational Database Integrity:** The system uses three distinct tables with Foreign Key constraints to ensure data consistency. Users are authenticated via hashed passwords using industry-standard security protocols, and their data is strictly isolated to their own `user_id` via session management.
* **Enterprise-Ready UI:** The interface was designed with a focus on "Clean UI" principles. Using a professional color palette and responsive layouts, it mimics the internal tools used by large corporations and banks, prioritizing data readability and ease of use.

### Technical Stack

* **Backend:** Python 3 with the Flask framework.
* **Database:** SQLite3 for persistent, relational storage.
* **Authentication:** Werkzeug security helpers for password hashing (`pbkdf2:sha256`).
* **Session Management:** `flask_session` configured for filesystem storage to ensure session persistence across server restarts.
* **Frontend:** HTML5, CSS3, and Jinja2 templating, utilizing custom filters for localized currency (BRL) and Brazilian date formats (DD/MM/YYYY).

### Database Schema Design

The project's architecture relies on three relational tables:
1.  **`users`**: Stores unique usernames and secure password hashes.
2.  **`applications`**: The primary data store containing job titles, companies, salaries, categories, and the current status.
3.  **`last_status`**: A logging table that records every status transition. This is crucial for calculating conversion metrics and maintaining a history of the user's progress throughout the job search.

### Design Choices & Engineering Challenges

During development, a significant challenge was handling "Empty States"—the user's experience when they first join the platform. Instead of showing an empty table, a custom `index-empty.html` view was created to guide the user toward their first entry, improving the "Onboarding" experience.

Another critical decision was the implementation of **Robust Input Validation**. The backend logic strips whitespace from inputs and performs server-side type checking on salary fields to prevent database corruption. Negative values are automatically converted to absolute values, and invalid categories or statuses are rejected with user-friendly "Flash" messages.

By choosing **SQLite** and **Flask**, the project remains lightweight yet powerful enough to be deployed in a production environment. The use of **Decorators** (`@login_required`) ensures that all routes are protected, following industry-standard security practices for web applications.

---
