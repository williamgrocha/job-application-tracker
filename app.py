import sqlite3
from flask import Flask, flash, redirect, render_template, request

from helpers import init_db, brl

app = Flask(__name__)  # Start Flask App
init_db()  # Init Database

# Custom filter
app.jinja_env.filters["brl"] = brl

CATEGORIES = [
    "Remote",
    "Hybrid",
    "On-site"
]

# Index route
@app.route("/")
def index():
    conn = sqlite3.connect("applications.db") #inicia conexão com banco de dados
    conn.row_factory = sqlite3.Row # inicia cursor pro banco de dados
    res = conn.execute( # query de busca
        "SELECT * FROM applications"
        )
    applications = res.fetchall() # Armazena o retorno da query em applications
    print(applications)
    print(sqlite3.Row)
    conn.close()

    return render_template("index.html", applications=applications) # Return index.html file where shows your job applications


@app.route("/create", methods=["GET", "POST"])
def new_application():
    if request.method == "POST":
        company = request.form.get("company").upper() # type: ignore
        title = request.form.get("job_title").upper() # type: ignore
        salary = request.form.get("salary")
        if salary == "":
            salary = 0
        category = request.form.get("category").capitalize() # type: ignore
        if (category not in CATEGORIES):
            category = "On-site"
        deadline = request.form.get("deadline")
        if deadline == "":
            deadline = None
        print(category)
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
    

@app.route("/edit", methods=["POST", "GET"])
def edit():


    return render_template(edit.html)
