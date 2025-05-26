
from flask import Flask, render_template, request, redirect, url_for
import json
from datetime import datetime, timedelta

app = Flask(__name__)

DATA_FILE = 'data.json'

def load_data():
    try:
        with open(DATA_FILE, ' 'r') as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/', methods=['GET', 'POST'])
def index():
    message = None
    if request.method == 'POST':
        code = request.form['code'].strip()
        data = load_data()
        if code in data:
            start_date = datetime.strptime(data[code]['start_date'], '%Y-%m-%d')
            duration = 15 if data[code]['type'] == '15' else 30
            end_date = start_date + timedelta(days=duration)
            remaining_days = (end_date - datetime.now()).days
            valid = remaining_days >= 0
            return render_template('index.html', code=code, valid=valid,
                                   end_date=end_date.date(), remaining=remaining_days)
        else:
            message = "Invalid code."
    return render_template('index.html', message=message)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    message = None
    if request.method == 'POST':
        code = request.form['code'].strip()
        start_date = request.form['start_date']
        duration_type = request.form['type']
        data = load_data()
        data[code] = {
            'start_date': start_date,
            'type': duration_type
        }
        save_data(data)
        message = "Voucher saved successfully."
    return render_template('admin.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)
