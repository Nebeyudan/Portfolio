import json, os, sqlite3
from flask import Flask, render_template, request, redirect, url_for, abort
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime
from config import Config
from utils import slugify


app = Flask(__name__)
app.config.from_object(Config)
app.wsgi_app = ProxyFix(app.wsgi_app)


@app.after_request
def set_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["X-XSS-Protection"] = "1; mode=block"  
    resp.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline';"
    return resp


BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")


with open(os.path.join(DATA_DIR, "projects.json"), "r", encoding="utf-8") as f:
    PROJECTS = json.load(f)


with open(os.path.join(DATA_DIR, "resume.json"), "r", encoding="utf-8") as f:
    RESUME = json.load(f)


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS messages (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
email TEXT,
subject TEXT,
message TEXT,
ts TEXT
);
"""


def get_db():
    conn = sqlite3.connect(app.config["DB_PATH"])
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.row_factory = sqlite3.Row
    return conn


with get_db() as db:
    db.executescript(SCHEMA_SQL)


@app.route("/")
def home():
# sort so highlight=True projects appear first
    top_projects = sorted(PROJECTS, key=lambda p: p.get("highlight", False), reverse=True)
    return render_template("home.html", projects=top_projects[:6])



@app.route("/projects")
def projects():
# Simply pass all projects directly, no tag filtering or categories
    return render_template("projects.html", projects=PROJECTS)

@app.route("/projects/<slug>")
def project_detail(slug):
    for p in PROJECTS:
        if p.get("slug") == slug:
            return render_template("project_detail.html", p=p)
    abort(404)


@app.route("/resume")
def resume():
    return render_template("resume.html", r=RESUME)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()
        if not (name and email and message):
            return render_template("contact.html", error="Name, email, and message are required."), 400
        with get_db() as db:
            db.execute(
            "INSERT INTO messages(name,email,subject,message,ts) VALUES (?,?,?,?,?)",
            (name, email, subject, message, datetime.utcnow().isoformat()),
            )   
        return redirect(url_for("home"))
    return render_template("contact.html")


@app.route("/admin/messages")
def admin_messages():
    pw = request.args.get("pw")
    if pw != app.config["ADMIN_PASSWORD"]:
        abort(403)
    with get_db() as db:
        rows = db.execute("SELECT * FROM messages ORDER BY id DESC").fetchall()
    return render_template("admin_messages.html", rows=rows)


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run()
