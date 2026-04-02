import sqlite3
from flask import Flask, flash, redirect, render_template, request

from helpers import init_db, brl

app = Flask(__name__)  # Start Flask App

app.secret_key = "secret_pw" # This password is only here because this is not a deployed product

init_db()  # Init Database

# Custom filter
app.jinja_env.filters["brl"] = brl

CATEGORIES = [ # Valid Categories
    "Remote",
    "Hybrid",
    "On-site"
]

STATUSES = [ # Valid Statuses
    "Saved",
    "Applied",
    "Interviewing",
    "Offer",
    "Rejected",
    "Withdrawn"
]

# Index route
@app.route("/", methods=["POST", "GET"])
def index():
    conn = sqlite3.connect("applications.db") # Connect with the DB
    conn.row_factory = sqlite3.Row # Create cursor to the DB using Row factory to access each value by their column names
    res = conn.execute( # Query to get the opened applications
        "SELECT * FROM applications WHERE status NOT IN ('Offer', 'Rejected', 'Withdrawn') ORDER BY id DESC"
        )
    applications = res.fetchall() # Store the query return

    res = conn.execute( # Second Query to get the closed applications
        "SELECT * FROM applications WHERE status NOT IN ('Saved', 'Applied', 'Interviewing') ORDER BY id DESC"
        )
    applications_closed = res.fetchall() # Store the second query return
    conn.close() # Close the connection to avoid DB locking issues
    if not applications and not applications_closed:
        return render_template("index-empty.html") # When Users has no applications
    else:
        if not applications:
            return render_template("index.html", closed=applications_closed) # When User has only closed applications
        else:
            return render_template("index.html", applications=applications, closed=applications_closed) # Return index.html file where shows your job applications


@app.route("/create", methods=["GET", "POST"])
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
            salary = float(salary)
        if not isinstance(salary, (int, float)):
            flash("Invalid Salary", "danger")
            return redirect("/create")

        category = request.form.get("category")
        if (category not in CATEGORIES): # Case: invalid category was hard-coded
            flash("Invalid Category.")
            return redirect("/create")

        deadline = request.form.get("deadline")
        if deadline == None or deadline.strip() == "": # Case: deadline field is empty
            deadline = None

        conn = sqlite3.connect("applications.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO applications (company, job_title, salary, category, deadline, link) VALUES (?, ?, ?, ?, ?, ?)",
            (company, title, salary, category, deadline, link)
        )
        conn.commit()
        conn.close()

        return redirect("/")
    else:
        return render_template("create.html", categories=CATEGORIES)
    

@app.route("/edit/<int:id>", methods=["GET", "POST"]) # Route for specific id when clicked
def edit(id):
    conn = sqlite3.connect("applications.db")
    conn.row_factory = sqlite3.Row
    
    if request.method == "POST":
        company = request.form.get("company")
        if not company or company.strip() == "": # Case: company field empty
            flash("Company is a required field.", "danger")
            return redirect("/edit/<int:id>")
        
        title = request.form.get("job_title") # Case: title field empty
        if not title or title.strip() == "":
            flash("Title is a required field.", "danger")
            return redirect("/edit/<int:id>")
        
        salary = request.form.get("salary") # Case: salary field empty
        if salary == None or salary =="":
            salary = 0
            try:
                salary = float(salary)
            except ValueError:
                flash("Invalid Salary", "danger")

        category = request.form.get("category")
        if (category not in CATEGORIES or category == None):
            flash("Invalid Category.", "danger")
            return redirect("/edit/<int:id>")
        
        deadline = request.form.get("deadline")
        if deadline == "":
            deadline = None
        
        link = request.form.get("link")
        status = request.form.get("status")
        if status not in STATUSES:
            flash("Invalid Status.", "danger")
            return redirect("/edit/<int:id>")
        
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
def dashboard():
    conn = sqlite3.connect("applications.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications")
    applications = cursor.fetchall()
    conn.close()

    return render_template("dashboard.html", applications=applications)