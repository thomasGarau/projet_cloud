from flask import Blueprint, send_from_directory, jsonify, current_app, abort, request
from werkzeug.utils import secure_filename, safe_join
from ..models.file_models import File
from ..models.user_models import User
from .. import db
import os
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

user_files_bp = Blueprint('user_files', __name__)

@user_files_bp.route('/user-files/<filename>.<extension>')
@jwt_required()
def user_files(filename, extension):
    full_name = f"{filename}.{extension}"
    username = get_jwt_identity()
    file = File.query.join(File.user).filter(File.name == filename, File.extension == f".{extension}", User.username == username).first()
    if file:
        directory = safe_join(current_app.config['USER_STORAGE'], username)
        try:
            return send_from_directory(directory, full_name, mimetype='application/pdf')
        except FileNotFoundError:
            print("File not found", full_name)
            abort(404)
    else:
        print("file not found in db", full_name, username)
        abort(404)


@user_files_bp.route('/user-files-info')
@jwt_required()
def user_files_info():
    username = get_jwt_identity()
    files = File.query.join(File.user).filter(User.username == username).all()
    files_info = []
    for file in files:
        file_path = safe_join(current_app.config['USER_STORAGE'], username, file.name + file.extension)
        if os.path.isfile(file_path):
            file_info = {
                'name': file.name,
                'extension': file.extension,
                'createdAt': file.created_at.strftime("%d/%m/%Y"),
                'userName': username
            }
            files_info.append(file_info)
    return jsonify(files_info)

@user_files_bp.route('/upload-file', methods=['POST'])
@jwt_required()
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier envoyé'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400

    if file:
        username = get_jwt_identity()
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['USER_STORAGE'], username, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)

        new_file = File(
            name=os.path.splitext(filename)[0],
            extension=os.path.splitext(filename)[1],
            created_at=datetime.utcnow(),
            user_id=User.query.filter_by(username=username).first().id
        )
        db.session.add(new_file)
        db.session.commit()

        return jsonify({'message': 'Fichier téléchargé avec succès', 'filename': filename}), 200

    return jsonify({'error': 'Erreur lors du téléchargement du fichier'}), 500


@user_files_bp.route('/rename-file', methods=['POST'])
@jwt_required()
def rename_file():
    data = request.get_json()
    original_name = data.get('originalName')
    new_name = data.get('newName')
    print(original_name, new_name)
    username = get_jwt_identity()

    file = File.query.join(File.user).filter(File.name == original_name, User.username == username).first()
    if file:
        file_path = safe_join(current_app.config['USER_STORAGE'], username, file.name + file.extension)
        new_file_path = safe_join(current_app.config['USER_STORAGE'], username, new_name + file.extension)

        if os.path.exists(file_path):
            os.rename(file_path, new_file_path)
            file.name = new_name
            db.session.commit()
            return jsonify({'message': 'Fichier renommé avec succès'}), 200
        else:
            return jsonify({'error': 'Fichier non trouvé'}), 404
    else:
        return jsonify({'error': 'Accès non autorisé ou fichier non trouvé'}), 403

@user_files_bp.route('/delete-file/<filename>', methods=['DELETE'])
@jwt_required()
def delete_file(filename):
    username = get_jwt_identity()
    print(filename, username)
    try:
        f_name, extension = filename.rsplit('.', 1)
    except ValueError as e:
        print(f"Erreur en divisant le filename : {e}")
        return jsonify({'error': 'Format de fichier invalide'}), 400
    print(f_name, extension)
    file = File.query.join(File.user).filter(File.name == f_name, File.extension == '.' + extension, User.username == username).first()

    if file:
        file_path = safe_join(current_app.config['USER_STORAGE'], username, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            db.session.delete(file)
            db.session.commit()
            return jsonify({'message': 'Fichier supprimé avec succès'}), 200
        else:
            return jsonify({'error': 'Fichier non trouvé'}), 404
    else:
        return jsonify({'error': 'Accès non autorisé ou fichier non trouvé'}), 403

