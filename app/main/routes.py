import os
import requests
from flask import (
        render_template, flash, redirect, url_for, request, g,
        jsonify, current_app
        )
from flask_login import current_user, login_required
from app import db
from app.models import User
from app.main import bp
from werkzeug.utils import secure_filename

basedir = os.path.abspath(os.path.dirname(__file__))
api_url = current_app.config['REMOTE_URL']
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@bp.route('/upload_signature', methods=['GET', 'POST'])
@login_required
def upload_signature():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            file.save('temp_image.jpg')
            payload = {'file': open('temp_image.jpg', 'rb')}
            response = requests.post(api_url + '/predict', files=payload)
            if response.status_code == 200:
                data = response.json()
                prediction = data.get('prediction')
                flash('Signature Verification Complete')
                return render_template('upload_signature.html', prediction=float(prediction))
            else:
                flash("An error occured while retrieving the signature" + str(response.text))
                return render_template('upload_signature.html')
        else:
            flash('Invalid Image File')
            return render_template('upload_signature.html')
    return render_template('upload_signature.html')


@bp.route('/upload_references', methods=['GET', 'POST'])
@login_required
def upload_references():
    if request.method == 'POST':
        # Get the user ID
        user_id = current_user.id

        # Create a directory for the user's reference images
        user_dir = os.path.join(UPLOAD_FOLDER, f'user_{user_id}')
        os.makedirs(user_dir, exist_ok=True)

        # Handle the file uploads
        files = request.files.getlist('references[]')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(user_dir, filename)
                file.save(file_path)

        flash('Reference images uploaded successfully.')
        return redirect(url_for('main.index'))
    return render_template('upload_references.html')


def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
