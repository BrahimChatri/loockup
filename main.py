from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import csv
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # needed for flash messages

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Store CSV data in memory after upload
csv_data = {}

def load_csv(filepath):
    global csv_data
    with open(filepath, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        csv_data = {row['PartNumber']: row['EMP_Location'] for row in reader}

@app.route('/', methods=['GET', 'POST'])
def index():
    location = None
    error = None
    part_number = ''

    if request.method == 'POST':
        if 'csvfile' in request.files:
            file = request.files['csvfile']
            if file and file.filename.endswith('.csv'):
                filepath = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(filepath)
                try:
                    load_csv(filepath)
                    flash('CSV file loaded successfully!', 'success')
                except Exception as e:
                    flash(f'Failed to load CSV: {e}', 'error')
            else:
                flash('Please upload a valid CSV file.', 'error')

        # Check if part number submitted via form input
        if 'part_number' in request.form:
            part_number = request.form['part_number'].strip()
            if not csv_data:
                error = 'Please upload a CSV file first.'
            elif part_number == '':
                error = 'Please enter a part number.'
            else:
                location = csv_data.get(part_number)
                if not location:
                    error = 'Part number not found in CSV.'

    return render_template('index.html', location=location, error=error, part_number=part_number)

@app.route('/lookup', methods=['POST'])
def lookup():
    data = request.json
    part_number = data.get('part_number', '').strip()
    if not csv_data:
        return jsonify({'error': 'CSV file not loaded'}), 400
    location = csv_data.get(part_number)
    if location:
        return jsonify({'location': location})
    else:
        return jsonify({'error': 'Part number not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
