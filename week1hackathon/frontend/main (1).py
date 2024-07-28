# from flask import Flask, request, render_template, jsonify
# import os
# import json
# from datetime import datetime

# app = Flask(__name__)
# UPLOAD_FOLDER = 'uploads'
# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# DATA_FILE = 'data.json'

# def load_data():
#     if os.path.exists(DATA_FILE):
#         with open(DATA_FILE, 'r') as file:
#             return json.load(file)
#     return []

# def save_data(data):
#     with open(DATA_FILE, 'w') as file:
#         json.dump(data, file, indent=4)

# def save_submission(full_name, email, original_filename, saved_filename):
#     current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     submission = {
#         'full_name': full_name,
#         'email': email,
#         'original_filename': original_filename,
#         'saved_filename': saved_filename,
#         'timestamp': current_time
#     }

#     data = load_data()
#     data.append(submission)
#     save_data(data)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/submit', methods=['POST'])
# def submit():
#     full_name = request.form['full_name']
#     email = request.form['email']
#     file = request.files['resume']

#     if file.filename == '':
#         return 'No selected file', 400

#     data = load_data()
#     if any(submission['email'] == email for submission in data):
#         return 'This email has already been used to submit a resume.', 400

#     if file:
#         original_filename = file.filename
#         timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
#         saved_filename = f"{email}_{timestamp}.pdf"
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
#         file.save(filepath)

#         save_submission(full_name, email, original_filename, saved_filename)
#         return 'Resume uploaded successfully!', 200

#     return 'Failed to upload resume', 500

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=3000)
from flask import Flask, request, render_template, jsonify, redirect, url_for
import os
import json
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DATA_FILE = 'data.json'


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    return []


def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)


def save_submission(full_name, email, original_filename, saved_filename):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    submission = {
        'full_name': full_name,
        'email': email,
        'original_filename': original_filename,
        'saved_filename': saved_filename,
        'timestamp': current_time
    }

    data = load_data()
    data.append(submission)
    save_data(data)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/form')
def form():
    return render_template('form.html')


@app.route('/submit', methods=['POST'])
def submit():
    full_name = request.form['full_name']
    email = request.form['email']
    file = request.files['resume']

    if file.filename == '':
        return 'No selected file', 400

    data = load_data()
    if any(submission['email'] == email for submission in data):
        return 'This email has already been used to submit a resume.', 400

    if file:
        original_filename = file.filename
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        saved_filename = f"{email}_{timestamp}.pdf"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
        file.save(filepath)

        save_submission(full_name, email, original_filename, saved_filename)
        return 'Resume uploaded successfully!', 200

    return 'Failed to upload resume', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
