from flask import Flask, render_template, session, request, redirect, url_for, flash

from datetime import timedelta, datetime
from os.path import exists
import hashlib

from pysqlcipher3 import dbapi2 as sqlite3
from flask import g

app = Flask(__name__)

if exists("session_key"):
    with open("session_key", "rb") as session_key_file:
        app.secret_key = session_key_file.read()
else:
    raise Exception("No session_key found")

DATABASE = "reday.db"


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        # this seemed like an easy way again escape chars
        h = hashlib.sha512()
        h.update(bytes(session["password"], "utf-8"))
        hexed = h.hexdigest()
        db.cursor().execute("PRAGMA key='{}'".format(hexed))
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@app.route("/close")
def closedb():
    session.pop("password", None)
    return redirect(url_for("opendb"))


@app.route("/open", methods=["GET", "POST"])
def opendb():
    bad_password = False
    if request.method == "POST":
        password = request.form.get("password")
        try:
            session["password"] = password
            get_db().cursor().execute("select 1 from entries").fetchone()
            flash("Successfully logged in")
            return redirect(url_for("write"))
        except:
            session.pop("password", None)
            bad_password = True
    return render_template("open.html", bad_password=bad_password)


@app.route("/read")
@app.route("/read/<int:offset>")
def read(offset=0):
    db = get_db()
    entries = (
        db.cursor()
        .execute("select * from entries order by date limit 15 offset ?", (offset,))
        .fetchall()
    )
    return render_template("read.html", entries=entries, offset=offset)


@app.route("/")
@app.route("/write", methods=["GET", "POST"])
def write():
    if not exists(DATABASE):
        return redirect(url_for("init"))
    if "password" not in session:
        return redirect(url_for("opendb"))

    db = get_db()

    if request.method == "POST":
        for date in request.form.keys():
            content = request.form[date]
            if content:
                db.cursor().execute(
                    "insert or replace into entries values (?, ?)", (date, content)
                )
        db.commit()
        flash("Saved changes")

    week = []
    entries = dict(
        db.cursor().execute("select * from entries order by date limit 7").fetchall()
    )
    for i in range(7):
        date = (datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d")
        if date in entries:
            content = entries[date]
        else:
            content = ""
        week.append((date, content))

    return render_template("write.html", week=week)


@app.route("/init", methods=["GET", "POST"])
def init():
    bad_password = False
    if request.method == "POST":
        if request.form["password"] != request.form["password-verify"]:
            bad_password = True
        else:
            session["password"] = request.form["password"]
            db = get_db()
            with open("tables.sql", "r") as tables_file:
                db.cursor().execute(tables_file.read())
                db.commit()
            flash("Database inited")
            return redirect(url_for("write"))
    return render_template("init.html", bad_password=bad_password)
