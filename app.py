import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash

from helpers import init_db, brl, init_users_db, login_required

# Start Flask App
app = Flask(__name__)

# This password is only here because this is not a deployed product
app.secret_key = "secret_pw"

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)

# Init Application's Database
init_db()

# Init Users Database
init_users_db()

# Custom filter
app.jinja_env.filters["brl"] = brl

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

# Index route
@app.route("/", methods=["POST", "GET"])
@login_required
def index():
    conn = sqlite3.connect("applications.db") # Connect with the DB
    conn.row_factory = sqlite3.Row # Create cursor to the DB using Row factory to access each value by their column names
    res = conn.execute( # Query to get the opened applications
        "SELECT * FROM applications WHERE status NOT IN ('Offer', 'Rejected', 'Withdrawn') AND user_id = ? ORDER BY id DESC", (session.get("user_id"),)
        )
    applications = res.fetchall() # Store the query return

    res = conn.execute( # Second Query to get the closed applications
        "SELECT * FROM applications WHERE status NOT IN ('Saved', 'Applied', 'Interviewing') AND user_id = ? ORDER BY id DESC", (session.get("user_id"),)
        )
    applications_closed = res.fetchall() # Store the second query return
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
        
        title = request.form.get("job_title")
        if not title or title.strip() == "": # Case: title field is empty
            flash("Title is a required field.")
            return redirect("/create")
        
        salary = request.form.get("salary")
        link = request.form.get("link")
        if salary == None or salary.strip() == "": # Case: salary field is empty
            salary = 0
        else:
            try:
                salary = float(salary)
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

        return redirect("/")
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
        
        title = request.form.get("job_title") # Case: title field empty
        if not title or title.strip() == "":
            flash("Title is a required field.", "danger")
            return redirect(f"/edit/{id}")
        
        salary = request.form.get("salary") # Case: salary field empty
        if salary == None or salary =="":
            salary = 0
        else:
            try:
                salary = float(salary)
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
        cursor.execute(
            "UPDATE applications SET company=?, job_title=?, salary=?, category=?, deadline=?, link=?, status=? WHERE id=?",
            (company.upper(), title.upper(), salary, category, deadline, link, status, id)
        )
        conn.commit()
        conn.close()
        
        return redirect("/")
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM applications WHERE id=?", (id,))
        application = cursor.fetchone()
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
    cursor = conn.cursor()
    cursor.execute("UPDATE applications SET status = ? WHERE id = ?", (status, id))
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
    conn = sqlite3.connect("applications.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications")
    applications = cursor.fetchall()
    conn.close()

    return render_template("dashboard.html", applications=applications)

@app.route("/login", methods=["GET", "POST"])
def login():

    #Forget any user_id
    session.clear()

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

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            return redirect("/")
    else:
        return render_template("login.html")
    
@app.route("/register", methods=["GET", "POST"])
def register():
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

        if existing_user:
            flash("This username has already been taken.", "danger")
            return redirect("/register")

        hashed_password = generate_password_hash(password)
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()

        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        new_user = cursor.fetchone()
        session["user_id"] = new_user["id"]
        conn.close()
        USERNAME = username

        flash("Registration successful!", "success")
        return redirect("/")
    else:
        return render_template("register.html")
    

@app.route("/logout")
@login_required
def logout():
    session.clear()

    flash("Logged out successfully!", "success")
    return redirect("/login")