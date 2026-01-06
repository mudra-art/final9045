from flask import Flask, render_template, request, redirect, session
import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables (works locally; Railway uses Variables panel)
load_dotenv()

app = Flask(__name__)

# Secret key (must be set in Railway Variables)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")

# ================= DATABASE =================
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE"),
        port=int(os.getenv("MYSQLPORT", 3306))
    )

# ================= HOME =================
@app.route("/")
def home():
    return render_template("index.html", user=session.get("user"))

# ================= CONTACT =================
@app.route("/contact", methods=["POST"])
def contact():
    name = request.form["name"]
    email = request.form["email"]
    message = request.form["message"]

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO contact_messages (name, email, message) VALUES (%s, %s, %s)",
        (name, email, message)
    )
    db.commit()
    cursor.close()
    db.close()

    return redirect("/")

# ================= BOOK TRIP =================
@app.route("/book", methods=["POST"])
def book():
    if "user" not in session:
        return redirect("/login")

    destination = request.form["destination"]
    travel_date = request.form["travel_date"]
    persons = request.form["persons"]
    username = session["user"]

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO bookings (username, destination, travel_date, persons) VALUES (%s, %s, %s, %s)",
        (username, destination, travel_date, persons)
    )
    db.commit()
    cursor.close()
    db.close()

    return redirect("/")

# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, password)
        )
        db.commit()
        cursor.close()
        db.close()

        return redirect("/login")

    return render_template("register.html")

# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user:
            session["user"] = user["username"]
            return redirect("/")
        else:
            return "Invalid Email or Password"

    return render_template("login.html")

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= RUN (Railway compatible) =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
