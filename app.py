import sqlite3
from flask import Flask, flash, redirect, render_template, request

from helpers import init_db, brl

app = Flask(__name__)  # Start Flask App

app.secret_key = "secret_pw" # This password is only here because this is an educational project

init_db()  # Init Database

# Custom filter
app.jinja_env.filters["brl"] = brl

CATEGORIES = [
    "Remote",
    "Hybrid",
    "On-site"
]

# Index route
@app.route("/", methods=["POST", "GET"])
def index():
    conn = sqlite3.connect("applications.db") #inicia conexão com banco de dados
    conn.row_factory = sqlite3.Row # inicia cursor pro banco de dados em rows
    res = conn.execute( # query de busca
        "SELECT * FROM applications"
        )
    applications = res.fetchall() # Armazena o retorno da query em applications
    conn.close()

    if not applications:
        return render_template("index-empty.html")
    else:
        return render_template("index.html", applications=applications) # Return index.html file where shows your job applications


@app.route("/create", methods=["GET", "POST"])
def new_application():
    if request.method == "POST":
        company = request.form.get("company") # type: ignore
        if not company or company.strip() == "":
            flash("Company is a required field.")
            return redirect("/create")
        title = request.form.get("job_title") # type: ignore
        if not title or title.strip() == "":
            flash("Title is a required field.")
            return redirect("/create")
        salary = request.form.get("salary")
        link = request.form.get("link")
        if salary == "":
            salary = 0
        category = request.form.get("category") # type: ignore
        if (category not in CATEGORIES):
            flash("Invalid Category.")
            return redirect("/create")

        deadline = request.form.get("deadline")
        if deadline == "":
            deadline = None
        conn = sqlite3.connect("applications.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO applications (company, job_title, salary, category, deadline, status, link) VALUES (?, ?, ?, ?, ?, 'saved', ?)",
            (company, title, salary, category, deadline, link)
        )
        conn.commit()
        conn.close()

        return redirect("/")
    else:
        return render_template("create.html", categories=CATEGORIES)
    

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = sqlite3.connect("applications.db")
    conn.row_factory = sqlite3.Row
    
    if request.method == "POST":
        company = request.form.get("company")
        print(company)
        if not company or company.strip() == "":
            flash("Company is a required field.")
            return redirect("/edit/<int:id>")
        title = request.form.get("job_title")
        print(title)
        if not title or title.strip() == "":
            flash("Title is a required field.")
            return redirect("/edit/<int:id>")
        salary = request.form.get("salary")
        if salary == "":
            salary = 0
        category = request.form.get("category")
        if (category not in CATEGORIES or category == None):
            flash("Invalid Category.")
            return redirect("/edit/<int:id>")
        deadline = request.form.get("deadline")
        if deadline == "":
            deadline = None
        link = request.form.get("link")
        
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE applications SET company=?, job_title=?, salary=?, category=?, deadline=?, link=? WHERE id=?",
            (company.upper(), title.upper(), salary, category, deadline, link, id)
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
        
        return render_template("edit.html", application=application, categories=CATEGORIES)
    

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