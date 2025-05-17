from flask import Flask, render_template, request, jsonify
import csv
import io

app = Flask(__name__)

csv_data = {}

def normalize_part_number(pn: str) -> str:
    pn = pn.strip()
    if len(pn) > 0 and pn[0].lower() == 'p':
        pn = 'P' + pn[1:]
    return pn

@app.route('/', methods=['GET', 'POST'])
def index():
    global csv_data
    error = ''
    location = ''
    part_number = ''

    if request.method == 'POST':
        # Check if CSV file uploaded
        if 'csv_file' in request.files:
            file = request.files['csv_file']
            if file.filename == '':
                error = 'No file selected.'
            else:
                try:
                    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                    reader = csv.DictReader(stream)
                    csv_data = {row['PartNumber']: row['EMP_Location'] for row in reader}
                    error = f'CSV file "{file.filename}" loaded successfully.'
                except Exception as e:
                    error = f'Failed to load CSV: {e}'

        # Check if part number submitted
        if 'part_number' in request.form:
            part_number = normalize_part_number(request.form['part_number'])
            if not csv_data:
                error = 'Please upload a CSV file first.'
            elif part_number == '':
                error = 'Please enter a part number.'
            else:
                location = csv_data.get(part_number)
                if not location:
                    error = 'Part number not found in CSV.'

    return render_template('index.html', error=error, location=location, part_number=part_number)

@app.route('/lookup', methods=['POST'])
def lookup():
    global csv_data
    data = request.json
    part_number = normalize_part_number(data.get('part_number', ''))
    if not csv_data:
        return jsonify({'error': 'CSV file not loaded'}), 400
    location = csv_data.get(part_number)
    if location:
        return jsonify({'location': location})
    else:
        return jsonify({'error': 'Part number not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=50000)
