from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import hashlib

app = Flask(__name__)

# --- Connect to XAMPP MySQL ---
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="login"  # your database name
)
cursor = db.cursor()

# --- Hash password ---
def hash_password(password):
    return hashlib.sha3_256(password.encode()).hexdigest()

# --- Check if user exists ---
def user_exist(username):
    cursor.execute("SELECT * FROM clients WHERE USERNAME=%s", (username,))
    return cursor.fetchone() is not None

# --- Validate login ---
def validate_login(username, password):
    password_hash = hash_password(password)
    cursor.execute(
        "SELECT * FROM clients WHERE USERNAME=%s AND PASSWORD=%s",
        (username, password_hash)
    )
    return cursor.fetchone() is not None

# --- Routes ---
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if user_exist(username):
            return "<h3>User already exists! <a href='/register'>Try again</a></h3>"
        else:
            password_hash = hash_password(password)
            cursor.execute(
                "INSERT INTO clients (USERNAME, PASSWORD) VALUES (%s, %s)",
                (username, password_hash)
            )
            db.commit()
            return redirect(url_for('login'))

    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if validate_login(username, password):
            return redirect(url_for("dashboard", user=username))
        else:
            return "<h3>Invalid username or password! <a href='/login'>Try again</a></h3>"

    return render_template("login.html")

@app.route("/dashboard/<user>")
def dashboard(user):
    return render_template("dashboard.html", user=user)

if __name__ == "__main__":
    app.run(debug=True)
