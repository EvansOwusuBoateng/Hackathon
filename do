from flask import Flask, render_template, request, redirect, url_for, g
from werkzeug.utils import secure_filename
from pathlib import Path
import pandas as pd
from data_preprocessing import wrangle
from dashboard import dash_app

app = Flask(__name__)

# Define the upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the uploads folder if it doesn't exist
Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html', title='FoodYum Dashboard')


@app.route('/dash')
def render_dash():
    return dash_app.layout


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = Path(app.config['UPLOAD_FOLDER']) / filename
            file.save(file_path)

            # Load the CSV file and preprocess the data
            data = pd.read_csv(file_path)
            processed_data, null_values, duplicate_rows = wrangle(data)

            # Store processed data in the Dash app's state
            dash_app.data = processed_data
            dash_app.null_values = null_values
            dash_app.duplicate_rows = duplicate_rows

            return redirect(url_for('render_dash'))
    return render_template('index.html', title='AnalytiCore')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    app.run(debug=True)