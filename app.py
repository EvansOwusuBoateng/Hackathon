from flask import Flask, render_template, request, redirect, url_for, g
from werkzeug.utils import secure_filename
from pathlib import Path
import pandas as pd

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


@app.route('/dash/')
def render_dash():
    # This import is placed here to avoid circular import issues
    from dashboard import dash_app
    return dash_app.index()


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
            g.global_data = pd.read_csv(file_path)
            return redirect(url_for('render_dash'))
    return render_template('index.html', title='FoodYum Dashboard')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    app.run()
