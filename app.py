
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import csv, os

app = Flask(__name__)
DATA_FILE = 'vouchers.csv'
ADMIN_PASSWORD = 'appleadmin'

def load_vouchers():
    vouchers = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                vouchers[row['code']] = row
    return vouchers

def save_voucher(code, start_date, duration):
    exists = os.path.exists(DATA_FILE)
    with open(DATA_FILE, mode='a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['code', 'start_date', 'duration'])
        if not exists:
            writer.writeheader()
        writer.writerow({'code': code, 'start_date': start_date, 'duration': duration})

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        code = request.form['voucher_code']
        vouchers = load_vouchers()
        if code in vouchers:
            start = datetime.strptime(vouchers[code]['start_date'], '%Y-%m-%d')
            days = int(vouchers[code]['duration'])
            valid = datetime.now() <= start + timedelta(days=days)
            result = {
                'valid': valid,
                'message': f"Valid till {(start + timedelta(days=days)).date()}" if valid else "Expired"
            }
        else:
            result = {'valid': False, 'message': 'Code not found'}
    return render_template('index.html', result=result)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST' and 'password' in request.form:
        password = request.form['password']
        return render_template('admin.html', authenticated=(password == ADMIN_PASSWORD))
    return render_template('admin.html', authenticated=False)

@app.route('/admin/add', methods=['POST'])
def add_voucher():
    code = request.form['code']
    start_date = request.form['start_date']
    duration = request.form['type']
    save_voucher(code, start_date, duration)
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
