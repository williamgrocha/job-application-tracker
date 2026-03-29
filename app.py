import sqlite3
from flask import Flask, flash, redirect, render_template, request

from helpers import init_db

app = Flask(__name__)  # Start Flask App
init_db()  # Init Database

# Index route
@app.route("/")
def index():
    return render_template("index.html") # Return index.html file where shows your job applications


@app.route("/create", methods=["GET", "POST"])
def new_application():
    if request.method == "POST":
        company = request.form.get("company")
        title = request.form.get("job_title")
        salary = request.form.get("salary")
        category = request.form.get("category")


        return render_template("create.html")
    else:
        return render_template("create.html")