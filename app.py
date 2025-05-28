from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from datetime import datetime, timedelta
import csv
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB = 'vouchers.db'

def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS vouchers
                     (code TEXT PRIMARY KEY, start_date TEXT, type TEXT)''')
        conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check():
    code = request.form['code'].strip()
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT start_date, type FROM vouchers WHERE code=?", (code,))
        row = c.fetchone()
        if row:
            start_date, vtype = row
            if start_date:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                days = 15 if vtype == "15" else 30
                expiry = start + timedelta(days=days)
                remaining = (expiry - datetime.now()).days
                if remaining >= 0:
                    return render_template("result.html", status="valid", expiry=expiry.strftime("%Y-%m-%d"), remaining=remaining)
                else:
                    return render_template("result.html", status="expired")
            else:
                return render_template("result.html", status="not_started")
        else:
            return render_template("result.html", status="invalid")

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM vouchers")
        vouchers = c.fetchall()
    return render_template("admin.html", vouchers=vouchers)

@app.route('/add_voucher', methods=['POST'])
def add_voucher():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    code = request.form['code'].strip()
    start_date = request.form['start_date'].strip()
    vtype = request.form['type'].strip()
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO vouchers (code, start_date, type) VALUES (?, ?, ?)", (code, start_date, vtype))
        conn.commit()
    return redirect(url_for("admin"))

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    file = request.files['file']
    if file and file.filename.endswith('.csv'):
        stream = file.stream.read().decode("UTF8").splitlines()
        reader = csv.reader(stream)
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            for row in reader:
                if len(row) >= 2:
                    code, vtype = row[0].strip(), row[1].strip()
                    c.execute("INSERT OR IGNORE INTO vouchers (code, type) VALUES (?, ?)", (code, vtype))
            conn.commit()
    return redirect(url_for("admin"))

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form['password'] == "admin123":
            session["logged_in"] = True
            return redirect(url_for("admin"))
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)