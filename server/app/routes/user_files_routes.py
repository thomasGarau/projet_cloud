from flask import Blueprint, send_from_directory, jsonify, current_app, abort, request
from flask import Response
from werkzeug.utils import secure_filename, safe_join
import threading
import os
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from .. import db
from ..services.compression_service import compresse_file, decompresse_file
from ..models.file_models import File
from ..models.user_models import User
from ..models.shared_files_models import SharedFile
from azure.storage.blob import BlobServiceClient

user_files_bp = Blueprint('user_files', __name__)

uploads = {}

from flask import send_file, Response, abort
from azure.storage.blob import BlobServiceClient
import io

@user_files_bp.route('/user-files/<filename>.<extension>')
@jwt_required()
def user_files(filename, extension):
    full_name = f"{filename}.{extension}"
    username = get_jwt_identity()

    # Recherche du fichier dans la base de données (fichiers utilisateur ou partagés)
    file = File.query.join(File.user).filter(
        File.name == filename,
        File.extension == f".{extension}",
        User.username == username
    ).first()

    # Si non trouvé, vérifier les fichiers partagés
    if not file:
        shared_file = SharedFile.query.join(File).join(User).filter(
            File.name == filename,
            File.extension == f".{extension}",
            SharedFile.shared_with_user_id == User.query.filter_by(username=username).first().id
        ).first()

        if shared_file:
            file = shared_file.file
            owner_username = shared_file.owner_user.username  # Nom d'utilisateur du propriétaire
        else:
            current_app.logger.warning(f"Fichier introuvable : {full_name} pour l'utilisateur {username}")
            abort(404)
    else:
        owner_username = username  # Nom d'utilisateur du propriétaire pour les fichiers utilisateurs

    # Mise à jour du champ `last_opened` pour les fichiers personnels
    if file and file.user.username == username:
        file.last_opened = datetime.utcnow()
        db.session.commit()

    # Récupération des informations de connexion Azure
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

    if not connection_string or not container_name:
        return jsonify({"error": "Configuration Azure Blob Storage manquante"}), 500

    try:
        # Connexion au Blob Service Client
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        # Chemin du fichier dans Azure Blob Storage
        blob_name = f"{owner_username}/{filename}.bin"  # Dossier du propriétaire
        blob_client = container_client.get_blob_client(blob_name)

        # Téléchargement du fichier depuis Azure
        stream = io.BytesIO()
        blob_client.download_blob().readinto(stream)
        compressed_content = stream.getvalue()
        stream.close()

        # Décompression du fichier
        file_content = decompresse_file(compressed_content)

        # Retourner le fichier décompressé comme réponse
        response = Response(file_content, mimetype='application/octet-stream')
        response.headers["Content-Disposition"] = f"attachment; filename={full_name}"
        return response

    except Exception as e:
        current_app.logger.error(f"Erreur lors du téléchargement du fichier {full_name} : {e}")
        abort(500)


@user_files_bp.route('/recent-user-files-info')
@jwt_required()
def recent_user_files_info():
    username = get_jwt_identity()

    # Récupération des informations de connexion Azure
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

    if not connection_string or not container_name:
        return jsonify({"error": "Configuration Azure Blob Storage manquante"}), 500

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    files_info = []

    try:
        # Récupérer les fichiers récents depuis la base de données
        files_in_db = File.query.join(File.user).filter(User.username == username).order_by(File.last_opened.desc()).all()

        # Indexer les informations par chemin complet pour correspondre aux blobs Azure
        db_file_info_map = {file.azure_blob_path: file for file in files_in_db}

        # Lister les blobs pour cet utilisateur
        blobs = container_client.list_blobs(name_starts_with=f"{username}/")
        for blob in blobs:
            blob_path = blob.name  # Chemin complet du blob
            file_db_info = db_file_info_map.get(blob_path)

            # Vérifiez si le fichier existe dans la base de données
            if file_db_info:
                file_info = {
                    'name': file_db_info.name,
                    'extension': file_db_info.extension,
                    'createdAt': file_db_info.created_at.strftime("%d/%m/%Y"),
                    'userName': username,
                    'lastOpened': file_db_info.last_opened.strftime("%d/%m/%Y %H:%M:%S") if file_db_info.last_opened else "Non ouvert"
                }
                files_info.append(file_info)

    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des fichiers récents : {e}")
        return jsonify({"error": "Impossible de récupérer les fichiers récents depuis Azure"}), 500

    return jsonify(files_info)


@user_files_bp.route('/shared-with-me')
@jwt_required()
def shared_with_me():
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404

    # Récupération des informations de connexion Azure
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

    if not connection_string or not container_name:
        return jsonify({"error": "Configuration Azure Blob Storage manquante"}), 500

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    files_info = []

    try:
        # Récupérer les fichiers partagés depuis la base de données
        shared_files = SharedFile.query.filter_by(shared_with_user_id=user.id).all()

        # Indexer les informations par chemin complet pour correspondre aux blobs Azure
        db_file_info_map = {sf.file.azure_blob_path: sf for sf in shared_files}

        # Lister les blobs partagés depuis Azure
        blobs = container_client.list_blobs()
        for blob in blobs:
            blob_path = blob.name  # Chemin complet du blob
            shared_file_db_info = db_file_info_map.get(blob_path)

            # Vérifiez si le fichier existe dans la base de données
            if shared_file_db_info:
                file = shared_file_db_info.file
                file_info = {
                    'name': file.name,
                    'extension': file.extension,
                    'createdAt': file.created_at.strftime("%d/%m/%Y"),
                    'ownerUserName': shared_file_db_info.owner_user.username
                }
                files_info.append(file_info)

    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des fichiers partagés : {e}")
        return jsonify({"error": "Impossible de récupérer les fichiers partagés depuis Azure"}), 500

    return jsonify(files_info)


@user_files_bp.route('/user-files-info')
@jwt_required()
def user_files_info():
    username = get_jwt_identity()

    # Récupération des informations de connexion Azure
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

    if not connection_string or not container_name:
        return jsonify({"error": "Configuration Azure Blob Storage manquante"}), 500

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    files_info = []

    try:
        # Récupérer les fichiers de l'utilisateur dans la base de données
        files_in_db = File.query.join(File.user).filter(User.username == username).all()

        # Indexer les informations par le chemin complet du blob
        db_file_info_map = {file.azure_blob_path: file for file in files_in_db}

        # Lister les blobs pour cet utilisateur
        blobs = container_client.list_blobs(name_starts_with=f"{username}/")
        for blob in blobs:
            blob_path = blob.name  # Chemin complet du blob, ex. "username/document.bin"
            file_db_info = db_file_info_map.get(blob_path)

            # Vérifiez si le fichier existe dans la base de données
            if file_db_info:
                file_info = {
                    'name': file_db_info.name,  # Nom du fichier sans extension
                    'extension': file_db_info.extension,  # Extension depuis la BDD
                    'createdAt': blob.creation_time.strftime("%d/%m/%Y") if blob.creation_time else "Inconnue",
                    'userName': username,
                    'lastOpened': file_db_info.last_opened.strftime("%d/%m/%Y") if file_db_info.last_opened else "Inconnue",
                }
                files_info.append(file_info)
            else:
                current_app.logger.warning(f"Blob non trouvé dans la BDD : {blob_path}")

    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des fichiers : {e}")
        return jsonify({"error": "Impossible de récupérer les fichiers depuis Azure Blob Storage"}), 500

    return jsonify(files_info)


@user_files_bp.route('/upload-file', methods=['POST'])
@jwt_required()
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier envoyé'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400
    
    if 'file_id' not in request.form:
        return jsonify({'error': 'Aucun identifiant de fichier envoyé'}), 400
    
    file_id = request.form['file_id']

    username = get_jwt_identity()

    uploads[file_id] = 'starting'
    thread = threading.Thread(target=handle_file_upload, args=(file, username, file_id))
    thread.start()
    
    return jsonify({'message': 'Upload started', 'file_id': file_id}), 202

@user_files_bp.route('/check-status/<file_id>', methods=['GET'])
@jwt_required()
def check_status(file_id):
    status = uploads.get(file_id, 'unknown')
    print("status", status)
    return jsonify({'status': status, 'file_id': file_id}), 200


def handle_file_upload(file, username, file_id):
    from .. import app
    with app.app_context():
        try:
            app.logger.debug("Début de la fonction")
            uploads[file_id] = 'reading'

            # Variables d'environnement
            container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
            connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

            if not container_name:
                raise ValueError("Le nom du conteneur est introuvable. Vérifiez la variable AZURE_CONTAINER_NAME.")
            if not connection_string:
                raise ValueError("La chaîne de connexion est introuvable. Vérifiez AZURE_STORAGE_CONNECTION_STRING.")

            app.logger.debug(f"Nom du conteneur : {container_name}")

            # Lecture du fichier
            filename = secure_filename(os.path.splitext(file.filename)[0])
            extension = os.path.splitext(file.filename)[1]
            file_content = file.read()
            original_size = len(file_content)
            app.logger.debug(f"Fichier lu, taille originale : {original_size}")

            # Compression
            uploads[file_id] = 'compressing'
            compressed_content = compresse_file(file_content, extension)
            app.logger.debug(f"Taille après compression : {len(compressed_content)}")

            # Azure Blob Storage
            uploads[file_id] = 'uploading'
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            container_client = blob_service_client.get_container_client(container_name)

            # Création du conteneur si nécessaire
            try:
                container_client.create_container()
                app.logger.debug(f"Conteneur {container_name} créé avec succès.")
            except Exception as e:
                app.logger.debug(f"Conteneur {container_name} existe déjà ou erreur : {e}")

            # Upload du fichier
            blob_name = f"{username}/{filename}.bin"
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(compressed_content, overwrite=True)
            app.logger.debug(f"Fichier {blob_name} uploadé avec succès.")

            # Métadonnées en base
            compressed_file_size = len(compressed_content)
            new_file = File(
                name=filename,
                extension=extension,
                created_at=datetime.utcnow(),
                last_opened=datetime.utcnow(),
                original_size=original_size,
                compressed_size=compressed_file_size,
                user_id=User.query.filter_by(username=username).first().id,
                azure_blob_path=blob_name
            )
            db.session.add(new_file)
            db.session.commit()

            uploads[file_id] = 'completed'
            app.logger.debug(f"Métadonnées enregistrées : {new_file.original_size} => {new_file.compressed_size}")
        except Exception as e:
            app.logger.error(f"Erreur lors de l'upload du fichier : {e}")
            uploads[file_id] = 'failed'


@user_files_bp.route('/rename-file', methods=['POST'])
@jwt_required()
def rename_file():
    data = request.get_json()
    original_full_name = data.get('originalName')
    new_full_name = data.get('newName')
    username = get_jwt_identity()

    original_name, original_extension = os.path.splitext(original_full_name)
    new_name, new_extension = os.path.splitext(new_full_name)

    # Vérification dans la base de données
    file = File.query.join(File.user).filter(
        File.name == original_name,
        File.extension == original_extension,
        User.username == username
    ).first()

    if not file:
        return jsonify({'error': 'Accès non autorisé ou fichier non trouvé'}), 403

    # Récupération des informations de connexion Azure
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

    if not connection_string or not container_name:
        return jsonify({"error": "Configuration Azure Blob Storage manquante"}), 500

    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        # Définir les chemins dans Azure
        original_blob_name = f"{username}/{original_name}.bin"
        new_blob_name = f"{username}/{new_name}.bin"

        # Copier le fichier dans Azure
        source_blob = container_client.get_blob_client(original_blob_name)
        new_blob = container_client.get_blob_client(new_blob_name)
        new_blob.start_copy_from_url(source_blob.url)

        # Supprimer l'ancien blob après la copie
        source_blob.delete_blob()

        # Mettre à jour la base de données
        file.name = new_name
        file.azure_blob_path = new_blob_name  # Mettre à jour le chemin dans la BDD
        db.session.commit()

        return jsonify({'message': 'Fichier renommé avec succès'}), 200

    except Exception as e:
        current_app.logger.error(f"Erreur lors du renommage du fichier {original_full_name} : {e}")
        return jsonify({'error': 'Erreur lors du renommage du fichier'}), 500


@user_files_bp.route('/delete-file/<filename>', methods=['DELETE'])
@jwt_required()
def delete_file(filename):
    username = get_jwt_identity()

    try:
        f_name, extension = filename.rsplit('.', 1)
    except ValueError as e:
        current_app.logger.error(f"Erreur en divisant le filename : {e}")
        return jsonify({'error': 'Format de fichier invalide'}), 400

    file = File.query.join(File.user).filter(
        File.name == f_name,
        File.extension == '.' + extension,
        User.username == username
    ).first()

    if not file:
        return jsonify({'error': 'Accès non autorisé ou fichier non trouvé'}), 403

    # Récupération des informations de connexion Azure
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

    if not connection_string or not container_name:
        return jsonify({"error": "Configuration Azure Blob Storage manquante"}), 500

    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        # Définir le chemin dans Azure
        blob_name = f"{username}/{f_name}.bin"
        blob_client = container_client.get_blob_client(blob_name)

        # Supprimer le fichier dans Azure
        blob_client.delete_blob()

        # Supprimer l'entrée dans la base de données
        db.session.delete(file)
        db.session.commit()

        return jsonify({'message': 'Fichier supprimé avec succès'}), 200

    except Exception as e:
        current_app.logger.error(f"Erreur lors de la suppression du fichier {filename} : {e}")
        return jsonify({'error': 'Erreur lors de la suppression du fichier'}), 500


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