
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta
import csv, os

app = Flask(__name__)
app.secret_key = 'apple_secret_key'

DATA_FILE = 'vouchers.csv'
ADMIN_PASSWORD = 'admin123'

def read_vouchers():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, newline='') as csvfile:
        return list(csv.DictReader(csvfile))

def write_voucher(code, start_date, duration):
    vouchers = read_vouchers()
    vouchers.append({'code': code, 'start_date': start_date, 'duration': duration})
    with open(DATA_FILE, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['code', 'start_date', 'duration'])
        writer.writeheader()
        writer.writerows(vouchers)

@app.route('/', methods=['GET', 'POST'])
def index():
    message, expiry, days_left = '', '', ''
    if request.method == 'POST':
        code = request.form['code']
        vouchers = read_vouchers()
        for v in vouchers:
            if v['code'] == code:
                start = datetime.strptime(v['start_date'], '%Y-%m-%d')
                duration = int(v['duration'])
                end = start + timedelta(days=duration)
                now = datetime.now()
                days_left = (end - now).days
                expiry = end.strftime('%Y-%m-%d')
                message = 'Valid' if days_left >= 0 else 'Expired'
                return render_template('result.html', code=code, message=message, expiry=expiry, days_left=days_left)
        message = 'Invalid code'
    return render_template('index.html', message=message)

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin'))
    return render_template('admin_login.html', error='Invalid' if request.method == 'POST' else '')

@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        code = request.form['code']
        start_date = request.form['start_date']
        duration = request.form['duration']
        write_voucher(code, start_date, duration)
    vouchers = read_vouchers()
    return render_template('admin.html', vouchers=vouchers)

if __name__ == '__main__':
    app.run(debug=True)
