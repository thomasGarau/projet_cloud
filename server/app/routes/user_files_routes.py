from flask import Blueprint, send_from_directory, jsonify, current_app, abort, request
from flask import Response
from werkzeug.utils import secure_filename, safe_join
from .. import db
import os
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from ..services.compression_service import compresse_file, decompresse_file
from ..models.file_models import File
from ..models.user_models import User
from ..models.shared_files_models import SharedFile

user_files_bp = Blueprint('user_files', __name__)

@user_files_bp.route('/user-files/<filename>.<extension>')
@jwt_required()
def user_files(filename, extension):
    full_name = f"{filename}.{extension}"
    username = get_jwt_identity()
    file = File.query.join(File.user).filter(File.name == filename, File.extension == f".{extension}", User.username == username).first()
    if file:
        file_path = safe_join(current_app.config['USER_STORAGE'], username, full_name)
        file.last_opened = datetime.utcnow()
        db.session.commit()
        
        try:
            with open(file_path, 'rb') as compressed_file:
                compressed_content = compressed_file.read()
                file_content = decompresse_file(compressed_content)
                
            response = Response(file_content, mimetype='application/octet-stream')
            response.headers["Content-Disposition"] = "attachment; filename={}".format(full_name)
            return response
        except FileNotFoundError:
            print("File not found", full_name)
            abort(404)
    else:
        print("file not found in db", full_name, username)
        abort(404)

@user_files_bp.route('/recent-user-files-info')
@jwt_required()
def recent_user_files_info():
    username = get_jwt_identity()
    files = File.query.join(File.user).filter(User.username == username).order_by(File.last_opened.desc()).all()
    files_info = []
    for file in files:
        file_path = safe_join(current_app.config['USER_STORAGE'], username, file.name + file.extension)
        if os.path.isfile(file_path):
            file_info = {
                'name': file.name,
                'extension': file.extension,
                'createdAt': file.created_at.strftime("%d/%m/%Y"),
                'userName': username,
                'lastOpened': file.last_opened.strftime("%d/%m/%Y %H:%M:%S") if file.last_opened else "Non ouvert"
            }
            files_info.append(file_info)
    return jsonify(files_info)

@user_files_bp.route('/shared-with-me')
@jwt_required()
def shared_with_me():
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404

    shared_files = SharedFile.query.filter_by(shared_with_user_id=user.id).all()
    
    files_info = []
    for shared_file in shared_files:
        file = shared_file.file
        file_info = {
            'name': file.name,
            'extension': file.extension,
            'createdAt': file.created_at.strftime("%d/%m/%Y"),
            'ownerUserName': shared_file.owner_user.username
        }
        files_info.append(file_info)
    
    return jsonify(files_info)


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
                'userName': username,
                'lastOpened': file.last_opened.strftime("%d/%m/%Y %H:%M:%S") if file.last_opened else "Non ouvert"
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

    username = get_jwt_identity()
    filename = secure_filename(file.filename)
    file_content = file.read()
    original_size = len(file_content)
    compressed_content = compresse_file(file_content)
    file_path = os.path.join(current_app.config['USER_STORAGE'], username, filename)
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'wb') as compressed_file:
        compressed_file.write(compressed_content)

    new_file = File(
        name=os.path.splitext(filename)[0],
        extension=os.path.splitext(filename)[1],
        created_at=datetime.utcnow(),
        last_opened=datetime.utcnow(),
        original_size=original_size,
        compressed_size=len(compressed_content),
        user_id=User.query.filter_by(username=username).first().id
    )
    db.session.add(new_file)
    db.session.commit()

    return jsonify({'message': 'Fichier téléchargé avec succès', 'filename': filename}), 200

@user_files_bp.route('/rename-file', methods=['POST'])
@jwt_required()
def rename_file():
    data = request.get_json()
    original_full_name = data.get('originalName')
    new_full_name = data.get('newName')
    username = get_jwt_identity()

    original_name, original_extension = os.path.splitext(original_full_name)
    new_name, new_extension = os.path.splitext(new_full_name)

    print("original name : ", original_name, "new name : ", new_name)
    print("original extension : ", original_extension, "new extension : ", new_extension)

    file = File.query.join(File.user).filter(File.name == original_name, File.extension == original_extension, User.username == username).first()
    if file:
        file_path = safe_join(current_app.config['USER_STORAGE'], username, original_name + original_extension)
        new_file_path = safe_join(current_app.config['USER_STORAGE'], username, new_name + original_extension)

        if os.path.exists(file_path):
            os.rename(file_path, new_file_path)
            file.name = new_name
            file.extension = original_extension
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
    try:
        f_name, extension = filename.rsplit('.', 1)
    except ValueError as e:
        print(f"Erreur en divisant le filename : {e}")
        return jsonify({'error': 'Format de fichier invalide'}), 400

    file = File.query.join(File.user).filter(File.name == f_name, File.extension == '.' + extension, User.username == username).first()
    if file:
        file_path = safe_join(current_app.config['USER_STORAGE'], username, filename)

        db.session.delete(file)
        db.session.commit()

        remaining_files = File.query.filter_by(name=f_name, extension='.' + extension).count()
        if remaining_files == 0 and os.path.exists(file_path):
            os.remove(file_path)

        return jsonify({'message': 'Fichier supprimé avec succès'}), 200
    else:
        return jsonify({'error': 'Accès non autorisé ou fichier non trouvé'}), 403



@user_files_bp.route('/storage-info')
@jwt_required()
def storage_info():
    username = get_jwt_identity()
    user_files = File.query.join(File.user).filter(User.username == username).all()
    
    total_original_size = sum(file.original_size for file in user_files)
    total_compressed_size = sum(file.compressed_size or 0 for file in user_files)
    max_storage_size = 5
    
    return jsonify({
        'total_original_size': total_original_size,
        'total_compressed_size': total_compressed_size,
        'space_saved': total_original_size - total_compressed_size,
        'total_space' : max_storage_size,
        'space_available': max_storage_size - total_compressed_size
    })


@user_files_bp.route('/share-file', methods=['POST'])
@jwt_required()
def share_file():
    print("appel de la route share-file")
    data = request.get_json()
    filename = data.get('filename')
    share_with_username = data.get('shareWithUsername')
    f_name, extension = filename.rsplit('.', 1)

    
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    share_with_user = User.query.filter_by(username=share_with_username).first()
    
    if not user or not share_with_user:
        print("Utilisateur non trouvé", username, share_with_username)
        return jsonify({'error': 'Utilisateur non trouvé'}), 404

    file = File.query.filter_by(name=f_name, user_id=user.id).first()
    
    if not file:
        print("Fichier non trouvé", f_name, user.id)
        return jsonify({'error': 'Fichier non trouvé'}), 404

    shared_file = SharedFile(file_id=file.id, owner_user_id=user.id, shared_with_user_id=share_with_user.id)
    db.session.add(shared_file)
    db.session.commit()
    
    return jsonify({'message': 'Fichier partagé avec succès'}), 200




@user_files_bp.route('/stop-sharing-file', methods=['DELETE'])
@jwt_required()
def stop_sharing_file():
    print("appel de la route stop-sharing-file")
    data = request.get_json()
    filename = data.get('filename')
    shared_with_username = get_jwt_identity()
    
    shared_with_user = User.query.filter_by(username=shared_with_username).first()
    if not shared_with_user:
        print("Utilisateur non trouvé", shared_with_username)
        return jsonify({'error': 'Utilisateur non trouvé'}), 404

    f_name, extension = filename.rsplit('.', 1)

    shared_file = SharedFile.query \
        .join(File, SharedFile.file_id == File.id) \
        .filter(
            File.name == f_name,
            File.extension == '.' + extension,
            SharedFile.shared_with_user_id == shared_with_user.id
        ).first()
    
    if not shared_file:
        print("Fichier non trouvé ou non partagé avec cet utilisateur", f_name, extension, shared_with_username)
        return jsonify({'error': 'Fichier non trouvé ou non partagé avec cet utilisateur'}), 404

    db.session.delete(shared_file)
    db.session.commit()
    
    return jsonify({'message': 'Partage du fichier arrêté avec succès'}), 200