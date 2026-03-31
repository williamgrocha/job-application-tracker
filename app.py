import sqlite3
from flask import Flask, flash, redirect, render_template, request

from helpers import init_db

app = Flask(__name__)  # Start Flask App
init_db()  # Init Database

CATEGORIES = [
    "Remote",
    "Hybrid",
    "On-site"
]

# Index route
@app.route("/")
def index():
    conn = sqlite3.connect("applications.db") #inicia conexão com banco de dados
    cursor = conn.cursor() # inicia cursor pro banco de dados
    cursor.execute( # query de busca
        "SELECT * FROM applications"
        )
    applications = cursor.fetchall() # Armazena o retorno da query em applications
    print(applications)
    conn.close()
    return render_template("index.html", applications=applications) # Return index.html file where shows your job applications


@app.route("/create", methods=["GET", "POST"])
def new_application():
    if request.method == "POST":
        company = request.form.get("company").upper() # type: ignore
        title = request.form.get("job_title").upper() # type: ignore
        salary = request.form.get("salary")
        if salary == "":
            salary = None
        category = request.form.get("category").capitalize() # type: ignore
        if (category not in CATEGORIES):
            category = "onsite"
        deadline = request.form.get("deadline")
        if deadline == "":
            deadline = None
        print(company)

        conn = sqlite3.connect("applications.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO applications (company, job_title, salary, category, deadline, status) VALUES (?, ?, ?, ?, ?, 'saved')",
            (company, title, salary, category, deadline)
        )
        conn.commit()
        conn.close()

        return redirect("/")
    else:
        return render_template("create.html", categories=CATEGORIES)