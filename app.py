import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import init_db

app = Flask(__name__)
init_db()

@app.route("/")
def index():
    return render_template("index.html")