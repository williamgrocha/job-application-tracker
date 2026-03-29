import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

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
        return render_template("create.html")
    else:
        return render_template("create.html")