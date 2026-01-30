from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secretkey"

# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                password TEXT,
                role TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS courses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS enrollments(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                course_id INTEGER)""")

    # Default admin
    c.execute("SELECT * FROM users WHERE email='admin@gmail.com'")
    if not c.fetchone():
        c.execute("INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)",
                  ("Admin","admin@gmail.com","admin123","admin"))

    conn.commit()
    conn.close()

init_db()

# ---------- HOME ----------
@app.route("/")
def home():
    return render_template("home.html")

# ---------- REGISTER ----------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)",
                  (name,email,password,"student"))
        conn.commit()
        conn.close()
        return redirect("/login")
    return render_template("register.html")

# ---------- LOGIN ----------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email,password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["role"] = user[4]
            if user[4] == "admin":
                return redirect("/admin")
            else:
                return redirect("/dashboard")

    return render_template("login.html")

# ---------- STUDENT DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM courses")
    courses = c.fetchall()
    conn.close()
    return render_template("dashboard.html", courses=courses)

# ---------- ENROLL COURSE ----------
@app.route("/enroll/<int:course_id>")
def enroll(course_id):
    user_id = session["user_id"]
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO enrollments (user_id,course_id) VALUES (?,?)",
              (user_id,course_id))
    conn.commit()
    conn.close()
    return redirect("/dashboard")

# ---------- ADMIN PANEL ----------
@app.route("/admin", methods=["GET","POST"])
def admin():
    if session.get("role") != "admin":
        return redirect("/")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if request.method == "POST":
        title = request.form["title"]
        desc = request.form["description"]
        c.execute("INSERT INTO courses (title,description) VALUES (?,?)", (title,desc))
        conn.commit()

    c.execute("SELECT * FROM courses")
    courses = c.fetchall()

    c.execute("SELECT name,email FROM users WHERE role='student'")
    students = c.fetchall()

    conn.close()
    return render_template("admin.html", courses=courses, students=students)

# ---------- DELETE COURSE ----------
@app.route("/delete_course/<int:id>")
def delete_course(id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("DELETE FROM courses WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/admin")

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)