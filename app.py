import os
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash

from helpers import date_br, init_db, brl, login_required, normalize_capitalize

# Start Flask App
app = Flask(__name__)

# env password
app.secret_key = os.environ.get("SECRET_KEY", "default_secret_key")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)

# Init Application's Database
init_db()

# Custom filter
app.jinja_env.filters["brl"] = brl
app.jinja_env.filters["date_br"] = date_br

# Valid Categories
CATEGORIES = [
    "Remote",
    "Hybrid",
    "On-site"
]

# Valid Statuses
STATUSES = [
    "Saved",
    "Applied",
    "Interviewing",
    "Offer",
    "Rejected",
    "Withdrawn"
]


def normalize_application_fields(application):
    """Ensure company and job title are always displayed in capitalized format."""
    if not application:
        return application

    data = dict(application)
    data["company"] = normalize_capitalize(data.get("company"))
    data["job_title"] = normalize_capitalize(data.get("job_title"))
    return data

# Index route
@app.route("/", methods=["POST", "GET"])
@login_required
def index():
    conn = sqlite3.connect("applications.db") # Connect with the DB
    conn.row_factory = sqlite3.Row # Create cursor to the DB using Row factory to access each value by their column names
    res = conn.execute( # Query to get the opened applications
        "SELECT * FROM applications WHERE status NOT IN ('Offer', 'Rejected', 'Withdrawn') AND user_id = ? ORDER BY id DESC", (session.get("user_id"),)
        )
    applications = [normalize_application_fields(app) for app in res.fetchall()] # Store the query return

    res = conn.execute( # Second Query to get the closed applications
        "SELECT * FROM applications WHERE status NOT IN ('Saved', 'Applied', 'Interviewing') AND user_id = ? ORDER BY id DESC", (session.get("user_id"),)
        )
    applications_closed = [normalize_application_fields(app) for app in res.fetchall()] # Store the second query return
    conn.close() # Close the connection to avoid DB locking issues
    if not applications and not applications_closed:
        conn = sqlite3.connect("applications.db") # Connect with the DB
        conn.row_factory = sqlite3.Row # Create cursor to the DB using Row factory to access each value by their column names
        res = conn.execute("SELECT username FROM users WHERE id = ?", (session.get("user_id"),)) # Query to get the username of the user
        user = res.fetchone() # Store the query return
        username = user["username"] # Get the username from the query return
        print(username)

        return render_template("index-empty.html", username=username) # When Users has no applications
    else:
        if not applications:
            return render_template("index.html", closed=applications_closed) # When User has only closed applications
        else:
            return render_template("index.html", applications=applications, closed=applications_closed) # Return index.html file where shows your job applications


@app.route("/create", methods=["GET", "POST"])
@login_required
def new_application():
    if request.method == "POST":
        company = request.form.get("company")
        if not company or company.strip() == "": # Case: company field is empty
            flash("Company is a required field.")
            return redirect("/create")
        company = normalize_capitalize(company)
        
        title = request.form.get("job_title")
        if not title or title.strip() == "": # Case: title field is empty
            flash("Title is a required field.")
            return redirect("/create")
        title = normalize_capitalize(title)
        
        salary = request.form.get("salary")
        link = request.form.get("link")
        if salary == None or salary.strip() == "": # Case: salary field is empty
            salary = 0
        else:
            try:
                salary = float(salary)
                salary = abs(salary) # Convert to absolute value to avoid negative salaries
            except ValueError: # Case: salary field is not a number
                flash("Invalid Salary", "danger")
                return redirect("/create")

        category = request.form.get("category")
        if (category not in CATEGORIES): # Case: invalid category was hard-coded
            flash("Invalid Category.")
            return redirect("/create")

        deadline = request.form.get("deadline")
        if deadline == None or deadline.strip() == "": # Case: deadline field is empty
            deadline = None

        user_id = session.get("user_id")
        conn = sqlite3.connect("applications.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO applications (company, job_title, salary, category, deadline, link, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (company, title, salary, category, deadline, link, user_id)
        )
        conn.commit()
        conn.close()

        return redirect("/dashboard")
    else:
        return render_template("create.html", categories=CATEGORIES)
    

@app.route("/edit/<int:id>", methods=["GET", "POST"]) # Route for specific id when clicked
@login_required
def edit(id):
    conn = sqlite3.connect("applications.db")
    conn.row_factory = sqlite3.Row
    
    if request.method == "POST":
        company = request.form.get("company")
        if not company or company.strip() == "": # Case: company field empty
            flash("Company is a required field.", "danger")
            return redirect(f"/edit/{id}")
        company = normalize_capitalize(company)
        
        title = request.form.get("job_title") # Case: title field empty
        if not title or title.strip() == "":
            flash("Title is a required field.", "danger")
            return redirect(f"/edit/{id}")
        title = normalize_capitalize(title)
        
        salary = request.form.get("salary") # Case: salary field empty
        if salary == None or salary =="":
            salary = 0
        else:
            try:
                salary = float(salary)
                salary = abs(salary) # Convert to absolute value to avoid negative salaries
            except ValueError:
                flash("Invalid Salary", "danger")
                return redirect(f"/edit/{id}")

        category = request.form.get("category")
        if (category not in CATEGORIES or category == None):
            flash("Invalid Category.", "danger")
            return redirect(f"/edit/{id}")
        
        deadline = request.form.get("deadline")
        if deadline == "":
            deadline = None
        
        link = request.form.get("link")
        status = request.form.get("status")
        if status not in STATUSES:
            flash("Invalid Status.", "danger")
            return redirect(f"/edit/{id}")
        
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM applications WHERE id=?", (id,))
        current_status = cursor.fetchone()

        cursor.execute(
            "UPDATE applications SET company=?, job_title=?, salary=?, category=?, deadline=?, link=?, status=? WHERE id=?",
            (company, title, salary, category, deadline, link, status, id)
        )

        cursor.execute(
            "INSERT INTO last_status (user_id, application_id, old_status, new_status) VALUES (?, ?, ?, ?)",
            (session.get("user_id"), id, current_status[0], status)
        )

        conn.commit()
        conn.close()
        
        return redirect("/")
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM applications WHERE id=?", (id,))
        application = normalize_application_fields(cursor.fetchone())
        conn.close()
        
        if not application:
            return "Application not found", 404
        
        return render_template("edit.html", application=application, categories=CATEGORIES, statuses=STATUSES)
    

@app.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    conn = sqlite3.connect("applications.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM applications WHERE id=?",
        (id,)
        )
    
    cursor.execute(
        "DELETE FROM last_status WHERE application_id=?",
        (id,)
    )
    
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/update_status/<int:id>/<string:status>", methods=["POST"])
@login_required
def update_status(id, status):
    if status not in STATUSES:
        flash("Invalid Status.", "danger")
        return redirect("/")

    conn = sqlite3.connect("applications.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT status FROM applications WHERE id = ? AND user_id = ?",
        (id, session.get("user_id"))
    )
    current_status = cursor.fetchone()

    if not current_status:
        conn.close()
        flash("Application not found.", "danger")
        return redirect("/")

    cursor.execute(
        "UPDATE applications SET status = ? WHERE id = ? AND user_id = ?",
        (status, id, session.get("user_id"))
    )

    if current_status["status"] != status:
        cursor.execute(
            "INSERT INTO last_status (user_id, application_id, old_status, new_status) VALUES (?, ?, ?, ?)",
            (session.get("user_id"), id, current_status["status"], status)
        )

    conn.commit()
    conn.close()
    if status == "Withdrawn" or status == "Applied":
        flash(f"Status Updated: {status}!", "warning")
    elif status == "Rejected":
        flash(f"Status Updated: {status}!", "danger")
    else:
        flash(f"Status Updated: {status}!", "success")
    return redirect("/")

@app.route("/dashboard")
@login_required
def dashboard():

    user_id = session.get("user_id")

    conn = sqlite3.connect("applications.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Query to get the username for the dashboard greeting
    cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    username = cursor.fetchone()

    # Query to get the total number of applications
    cursor.execute("SELECT COUNT(*) FROM applications WHERE user_id = ?", (user_id,))
    total = cursor.fetchone()

    # Query to get the number of applications created in the last 7 days
    cursor.execute("SELECT COUNT(*) FROM applications WHERE user_id = ? AND date_added >= date('now', '-7 days')", (user_id,))
    this_week = cursor.fetchone()
    
    # Query to get the number of applications that are interviewing
    cursor.execute("SELECT COUNT(*) FROM applications WHERE user_id = ? AND status = 'Interviewing'", (user_id,))
    interviewing = cursor.fetchone()
    print(interviewing[0])

    # Query to get the number of applications that got an offer
    cursor.execute("SELECT COUNT(*) FROM applications WHERE user_id = ? AND status = 'Offer'", (user_id,))
    offers = cursor.fetchone()

    # Query to get the number of applications in the 'applied' status for the pipeline snapshot
    cursor.execute("SELECT COUNT(*) FROM applications WHERE user_id = ? AND status = 'Applied'", (user_id,))
    applied = cursor.fetchone()

    # Query to get the number of applications in the 'saved' status for the pipeline snapshot
    cursor.execute("SELECT COUNT(*) FROM applications WHERE user_id = ? AND status = 'Saved'", (user_id,))
    saved = cursor.fetchone()

    # Query to get the number of applications in the 'rejected' status for the pipeline snapshot
    cursor.execute("SELECT COUNT(*) FROM applications WHERE user_id = ? AND status = 'Rejected'", (user_id,))
    rejected = cursor.fetchone()

    # Query to get all applications for the user to show in the dashboard's table
    cursor.execute("SELECT * FROM applications WHERE user_id = ?", (user_id,))
    applications = [normalize_application_fields(app) for app in cursor.fetchall()]

    # Query to get the number of applications that changed status from 'Interviewing' to any other status for the insights section
    cursor.execute(
    """    
        SELECT COUNT(DISTINCT applications.id)
    FROM applications
    JOIN last_status ON applications.id = last_status.application_id
    WHERE applications.user_id = ?
    AND last_status.old_status = 'Interviewing' 
    """, (user_id,))
    get_interviews = cursor.fetchone()
    interviews = get_interviews[0] + interviewing[0] # Adding the current interviewing applications to the total number of interviews for a more complete insights
    conn.close()

    return render_template("dashboard.html", username=username[0], total=total[0]-saved[0], this_week=this_week[0]-saved[0], interviews=interviews, offers=offers[0], interviewing=interviewing[0], applied=applied[0], saved=saved[0], rejected=rejected[0], applications=applications)

@app.route("/login", methods=["GET", "POST"])
def login():

    # User reached route via POST (as by submitting a form via POST): Validate form submission
    if request.method == "POST":
        if not request.form.get("username"):
            flash("Username is required.", "danger")
            return redirect("/login")
        elif not request.form.get("password"):
            flash("Password is required.", "danger")
            return redirect("/login")
        
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("applications.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        # Check if username exists and if password is correct
        if not user:
            flash("Invalid username.", "danger")
            return redirect("/login")
        
        elif not check_password_hash(user["password"], password):
            flash("Invalid password.", "danger")
            return redirect("/login")
        
        # Remember which user has logged in
        session["user_id"] = user["id"]
        return redirect("/")
    else:
        # GET method: render login page
        return render_template("login.html")
    
@app.route("/register", methods=["GET", "POST"])
def register():

    # Post method: Validate form submission
    if request.method == "POST":
        if not request.form.get("username"):
            flash("Username is required.", "danger")
            return redirect("/register")
        elif not request.form.get("password") or not request.form.get("confirmation") or request.form.get("password").strip() == "" or request.form.get("confirmation").strip() == "":
            flash("Password is required.", "danger")
            return redirect("/register")
        elif request.form.get("password") != request.form.get("confirmation"):
            flash("Passwords do not match.", "danger")
            return redirect("/register")
        
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("applications.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        # Check if the username is already taken
        if existing_user:
            flash("This username has already been taken.", "danger")
            return redirect("/register")
        
        # Hash the password and insert the new user into the database
        hashed_password = generate_password_hash(password)
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()

        # Log the user in by storing their user ID in the session
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        new_user = cursor.fetchone()
        session["user_id"] = new_user["id"]
        conn.close()

        flash("Registration successful!", "success")
        return redirect("/")
    else:
        return render_template("register.html")
    

@app.route("/logout")
@login_required
def logout():
    # Forget any user_id
    session.clear()

    # Flash a message to indicate successful logout
    flash("Logged out successfully!", "success")
    return redirect("/login")