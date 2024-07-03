import os
import pandas as pd
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import matplotlib.pyplot as plt
import seaborn as sns

app = Flask(__name__)
CORS(app)


# Route for the home page
@app.route('/')
def home():
    return render_template('index.html', title='Data Analysis Tool with Chatbot')


# Route to handle file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join('uploads', filename)
        file.save(filepath)
        data = pd.read_csv(filepath)
        summary_stats = data.describe().to_dict()
        first_rows = data.head().to_dict(orient='records')

        return jsonify({
            'summary_statistics': summary_stats,
            'first_rows': first_rows
        })
    else:
        return jsonify({'error': 'Invalid file type'}), 400


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['csv']


def secure_filename(filename):
    return filename


# Route to handle chat messages
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'reply': 'Sorry, I did not understand that.'}), 400

    # Simulate a bot response (you can replace this with more complex logic)
    bot_reply = f"You said: {user_message}"

    return jsonify({'reply': bot_reply})


# Route to generate dashboard
@app.route('/dashboard', methods=['POST'])
def dashboard():
    data = request.json.get('data')
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    df = pd.DataFrame(data)

    # Example plot
    plt.figure(figsize=(10, 6))
    sns.histplot(df.select_dtypes(include=['number']).iloc[:, 0])
    plot_path = os.path.join('static', 'plot.png')
    plt.savefig(plot_path)

    return jsonify({'plot_url': plot_path})


if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)
