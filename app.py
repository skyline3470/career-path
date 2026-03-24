# ============================================
# Career Path Explorer - Flask Backend
# ============================================
# Run this file to start the server:
#   pip install flask
#   python app.py
# Then open http://localhost:5000 in your browser
# ============================================

import os
import sqlite3

from flask import Flask, jsonify, render_template, request

try:
    import psycopg
except ImportError:
    psycopg = None

app = Flask(__name__)
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
SQLITE_DB = os.getenv("SQLITE_DB_PATH", "/tmp/database.db" if os.getenv("VERCEL") else "database.db")
USE_POSTGRES = DATABASE_URL.startswith(("postgresql://", "postgres://"))
IS_VERCEL = bool(os.getenv("VERCEL"))
DB_INITIALIZED = False


def get_connection():
    """Return a database connection for the configured backend."""
    if USE_POSTGRES:
        if psycopg is None:
            raise RuntimeError(
                "PostgreSQL support requires the 'psycopg' package. "
                "Install it with: pip install psycopg[binary]"
            )
        return psycopg.connect(DATABASE_URL)
    return sqlite3.connect(SQLITE_DB)

# --- Database Setup ---
def init_db():
    """Create the students table if it doesn't exist."""
    conn = get_connection()
    create_table_sql = """
        CREATE TABLE IF NOT EXISTS students (
            id      SERIAL PRIMARY KEY,
            name    TEXT    NOT NULL,
            email   TEXT    NOT NULL,
            career  TEXT    NOT NULL
        )
    """ if USE_POSTGRES else """
        CREATE TABLE IF NOT EXISTS students (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT    NOT NULL,
            email   TEXT    NOT NULL,
            career  TEXT    NOT NULL
        )
    """
    conn.execute(create_table_sql)
    conn.commit()
    conn.close()


def ensure_db_initialized():
    """Initialize the database once per server instance."""
    global DB_INITIALIZED
    if DB_INITIALIZED:
        return
    init_db()
    DB_INITIALIZED = True


def get_storage_warning():
    """Explain when the current storage mode is not persistent."""
    if IS_VERCEL and not USE_POSTGRES:
        return (
            "This deployment is using temporary SQLite storage on Vercel. "
            "Submissions may not appear on later requests. Set DATABASE_URL "
            "to your Neon/PostgreSQL database in Vercel to persist entries."
        )
    return None

# Career data — easy to extend
CAREERS = {
    "engineering": {
        "title": "Engineering",
        "emoji": "⚙️",
        "desc": "Design and build systems, machines, and software that power the world.",
        "skills": ["Mathematics", "Problem Solving", "Logical Thinking", "Teamwork"],
        "subjects": ["Physics", "Mathematics", "Computer Science"],
        "roles": ["Software Engineer", "Civil Engineer", "Mechanical Engineer", "Google, Infosys, L&T"],
    },
    "medicine": {
        "title": "Medicine",
        "emoji": "🩺",
        "desc": "Diagnose, treat, and prevent illness to improve human health and lives.",
        "skills": ["Empathy", "Attention to Detail", "Communication", "Stamina"],
        "subjects": ["Biology", "Chemistry", "Physics"],
        "roles": ["Doctor", "Surgeon", "Nurse", "AIIMS, Apollo, Fortis"],
    },
    "cybersecurity": {
        "title": "Cybersecurity",
        "emoji": "🔐",
        "desc": "Protect systems and networks from digital attacks and data breaches.",
        "skills": ["Ethical Hacking", "Networking", "Cryptography", "Vigilance"],
        "subjects": ["Computer Science", "Mathematics", "Electronics"],
        "roles": ["Security Analyst", "Penetration Tester", "ISRO, TCS, Palo Alto"],
    },
    "business": {
        "title": "Business",
        "emoji": "📊",
        "desc": "Lead organisations, manage resources, and drive growth and strategy.",
        "skills": ["Leadership", "Communication", "Finance", "Decision Making"],
        "subjects": ["Economics", "Mathematics", "Commerce"],
        "roles": ["Manager", "Entrepreneur", "Analyst", "Deloitte, McKinsey, startups"],
    },
    "design": {
        "title": "Design",
        "emoji": "🎨",
        "desc": "Create visual experiences — from logos and apps to architecture and fashion.",
        "skills": ["Creativity", "Adobe Suite", "Typography", "User Empathy"],
        "subjects": ["Art", "Computer Science", "Psychology"],
        "roles": ["UX Designer", "Graphic Designer", "Architect", "Adobe, Zomato, Canva"],
    },
    "government": {
        "title": "Government Jobs",
        "emoji": "🏛️",
        "desc": "Serve the nation through civil services, defence, banking, and public policy.",
        "skills": ["Dedication", "General Knowledge", "Integrity", "Leadership"],
        "subjects": ["History", "Political Science", "Economics"],
        "roles": ["IAS / IPS Officer", "Bank PO", "Defence Officer", "UPSC, SSC, IBPS"],
    },
}

# Quiz logic — maps answer combos to careers
QUIZ_MAP = {
    ("math",    "solving"):   "engineering",
    ("math",    "managing"):  "business",
    ("math",    "designing"): "cybersecurity",
    ("math",    "helping"):   "engineering",
    ("biology", "helping"):   "medicine",
    ("biology", "solving"):   "medicine",
    ("biology", "managing"):  "government",
    ("biology", "designing"): "design",
    ("business","managing"):  "business",
    ("business","helping"):   "government",
    ("business","solving"):   "business",
    ("business","designing"): "design",
    ("computers","solving"):  "cybersecurity",
    ("computers","designing"):"design",
    ("computers","managing"): "business",
    ("computers","helping"):  "medicine",
}

# ---- Routes ----

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/careers")
def careers():
    return render_template("careers.html", careers=CAREERS)

@app.route("/career/<slug>")
def career_detail(slug):
    career = CAREERS.get(slug)
    if not career:
        return "Career not found", 404
    return render_template("career_detail.html", career=career, slug=slug)

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    result = None
    if request.method == "POST":
        subject = request.form.get("subject", "").lower()
        work    = request.form.get("work", "").lower()
        slug    = QUIZ_MAP.get((subject, work), "engineering")
        result  = CAREERS[slug]
        result["slug"] = slug
    return render_template("quiz.html", result=result)

@app.route("/form", methods=["GET", "POST"])
def form():
    success = False
    error = None
    warning = get_storage_warning()
    if request.method == "POST":
        name   = request.form.get("name", "").strip()
        email  = request.form.get("email", "").strip()
        career = request.form.get("career", "").strip()
        if name and email and career:
            try:
                ensure_db_initialized()
                conn = get_connection()
                insert_sql = (
                    "INSERT INTO students (name, email, career) VALUES (%s, %s, %s)"
                    if USE_POSTGRES
                    else "INSERT INTO students (name, email, career) VALUES (?, ?, ?)"
                )
                conn.execute(insert_sql, (name, email, career))
                conn.commit()
                conn.close()
                success = True
            except Exception as exc:
                error = str(exc)
    return render_template(
        "form.html",
        careers=CAREERS,
        success=success,
        error=error,
        warning=warning,
    )

@app.route("/admin")
def admin():
    rows = []
    error = None
    warning = get_storage_warning()
    try:
        ensure_db_initialized()
        conn = get_connection()
        rows = conn.execute("SELECT id, name, email, career FROM students ORDER BY id DESC").fetchall()
        conn.close()
    except Exception as exc:
        error = str(exc)
    return render_template("admin.html", students=rows, error=error, warning=warning)

@app.route("/health")
def health():
    database = "postgresql" if USE_POSTGRES else "sqlite"
    warning = get_storage_warning()
    try:
        ensure_db_initialized()
        conn = get_connection()
        row = conn.execute("SELECT 1").fetchone()
        conn.close()
        return jsonify({
            "status": "ok",
            "database": database,
            "database_ok": bool(row and row[0] == 1),
            "warning": warning,
        }), 200
    except Exception as exc:
        return jsonify({
            "status": "error",
            "database": database,
            "database_ok": False,
            "message": str(exc),
            "warning": warning,
        }), 500

# ---- Start ----
if __name__ == "__main__":
    ensure_db_initialized()
    app.run(debug=True)
