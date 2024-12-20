from flask import Blueprint, send_from_directory, jsonify, current_app, abort, request
from flask import Response
from werkzeug.utils import secure_filename, safe_join
import threading
import os
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from .. import db
from ..services.compression_service import compresse_file, decompresse_file
from ..models.file_models import File
from ..models.user_models import User
from ..models.shared_files_models import SharedFile
from azure.storage.blob import BlobServiceClient, generate_blob_sas, generate_container_sas, BlobSasPermissions, ContainerSasPermissions, ContainerClient
from azure.storage.queue import QueueClient
import json
import tempfile
from flask import send_file

user_files_bp = Blueprint('user_files', __name__)

uploads = {}


from flask import send_file, Response, abort
from azure.storage.blob import BlobServiceClient
import io

from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta

@user_files_bp.route('/user-files/<filename>.<extension>')
@jwt_required()
def user_files(filename, extension):
    full_name = f"{filename}.{extension}"
    username = get_jwt_identity()
    current_app.logger.info(f"Tentative d'accès au fichier : {full_name} par {username}")

    # Recherche du fichier dans la base de données
    file = File.query.join(File.user).filter(
        File.name == filename,
        File.extension == f".{extension}",
        User.username == username
    ).first()

    if not file:
        shared_file = SharedFile.query.join(File).join(User).filter(
            File.name == filename,
            File.extension == f".{extension}",
            SharedFile.shared_with_user_id == User.query.filter_by(username=username).first().id
        ).first()

        if shared_file:
            file = shared_file.file
            owner_username = shared_file.owner_user.username
        else:
            current_app.logger.warning(f"Fichier introuvable : {full_name} pour l'utilisateur {username}")
            abort(404)
    else:
        owner_username = username

    # Vérification des configurations Azure
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
    account_name = os.getenv("AZURE_ACCOUNT_NAME")
    account_key = os.getenv("AZURE_ACCOUNT_KEY")

    if not all([connection_string, container_name, account_name, account_key]):
        current_app.logger.error("Configuration Azure Blob Storage manquante.")
        return jsonify({"error": "Configuration Azure Blob Storage manquante"}), 500

    try:
        # Connexion au container client
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        # Chemins possibles pour le fichier
        temporary_blob_name = f"{owner_username}/{filename}.{extension}"
        compressed_blob_name = f"{owner_username}/{filename}_compressed.bin"

        # Détermine le fichier à utiliser
        blob_name = next(
            (name for name in [temporary_blob_name, compressed_blob_name] if container_client.get_blob_client(name).exists()),
            None
        )

        if not blob_name:
            current_app.logger.warning(f"Aucun fichier trouvé dans Azure pour : {full_name}")
            abort(404)

        # Générer un lien SAS
        sas_token = generate_blob_sas(
            account_name=account_name,
            account_key=account_key,
            container_name=container_name,
            blob_name=blob_name,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        
        # Construire une URL sans les credentials dans le host
        sas_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
        print("sas_url", sas_url)
        return jsonify({
            "fileUrl": sas_url,
            "originalName": f"{filename}{extension}",
        })

    except Exception as e:
        current_app.logger.error(f"Erreur lors de la génération du lien SAS pour {full_name} : {e}")
        abort(500)


@user_files_bp.route('/recent-user-files-info')
@jwt_required()
def recent_user_files_info():
    username = get_jwt_identity()

    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

    if not connection_string or not container_name:
        return jsonify({"error": "Configuration Azure Blob Storage manquante"}), 500

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    files_info = []

    try:
        files_in_db = File.query.join(File.user).filter(
            User.username == username
        ).order_by(File.last_opened.desc()).all()

        # Indexer les fichiers par chemin potentiel pour le fichier compressé ou temporaire
        db_file_info_map = {
            f"{username}/{file.name}{file.extension}": file for file in files_in_db
        }
        db_file_info_map.update({
            f"{username}/{file.name}_compressed.bin": file for file in files_in_db
        })

        blobs = container_client.list_blobs(name_starts_with=f"{username}/")
        for blob in blobs:
            blob_path = blob.name
            file_db_info = db_file_info_map.get(blob_path)

            if file_db_info:
                # Retourner le nom et l'extension d'origine pour le client
                file_info = {
                    'name': file_db_info.name,
                    'extension': file_db_info.extension,  # Extension d'origine depuis la BDD
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

    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

    if not connection_string or not container_name:
        return jsonify({"error": "Configuration Azure Blob Storage manquante"}), 500

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    files_info = []

    try:
        shared_files = SharedFile.query.filter_by(shared_with_user_id=user.id).all()

        db_file_info_map = {
            f"{sf.owner_user.username}/{sf.file.name}{sf.file.extension}": sf for sf in shared_files
        }
        db_file_info_map.update({
            f"{sf.owner_user.username}/{sf.file.name}_compressed.bin": sf for sf in shared_files
        })

        blobs = container_client.list_blobs()
        for blob in blobs:
            blob_path = blob.name
            shared_file_db_info = db_file_info_map.get(blob_path)

            if shared_file_db_info:
                file = shared_file_db_info.file
                file_info = {
                    'name': file.name,
                    'extension': file.extension,  # Extension d'origine depuis la BDD
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

    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

    if not connection_string or not container_name:
        return jsonify({"error": "Configuration Azure Blob Storage manquante"}), 500

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    files_info = []

    try:
        files_in_db = File.query.join(File.user).filter(User.username == username).all()

        db_file_info_map = {
            f"{username}/{file.name}{file.extension}": file for file in files_in_db
        }
        db_file_info_map.update({
            f"{username}/{file.name}_compressed.bin": file for file in files_in_db
        })

        blobs = container_client.list_blobs(name_starts_with=f"{username}/")
        for blob in blobs:
            blob_path = blob.name
            file_db_info = db_file_info_map.get(blob_path)

            if file_db_info:
                file_info = {
                    'name': file_db_info.name,
                    'extension': file_db_info.extension,  # Extension d'origine depuis la BDD
                    'createdAt': blob.creation_time.strftime("%d/%m/%Y") if blob.creation_time else "Inconnue",
                    'userName': username,
                    'lastOpened': file_db_info.last_opened.strftime("%d/%m/%Y %H:%M:%S") if file_db_info.last_opened else "Non ouvert",
                }
                files_info.append(file_info)

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

    # Thread pour gérer l'upload
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
        blob_client = None  # Pour gérer la suppression en cas d'erreur
        try:
            app.logger.debug("Début de la fonction")
            uploads[file_id] = 'reading'

            # Variables d'environnement
            container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
            connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
            queue_name = os.getenv("AZURE_QUEUE_NAME")
            queue_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")  # Réutilisation

            if not container_name or not connection_string or not queue_name:
                raise ValueError("Configuration Azure Blob Storage ou Queue Storage manquante.")

            app.logger.debug(f"Nom du conteneur : {container_name}")
            app.logger.debug(f"Nom de la file d'attente : {queue_name}")

            # Lecture du fichier
            filename = secure_filename(os.path.splitext(file.filename)[0])
            extension = os.path.splitext(file.filename)[1]
            file_content = file.read()
            original_size = len(file_content)
            app.logger.debug(f"Fichier lu, taille originale : {original_size}")

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

            # Upload du fichier temporaire
            blob_name = f"{username}/{filename}{extension}"
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(file_content, overwrite=True)
            app.logger.debug(f"Fichier {blob_name} uploadé avec succès.")

            # Générer un lien SAS pour accès immédiat
            sas_token = generate_blob_sas(
                account_name=os.getenv("AZURE_ACCOUNT_NAME"),
                container_name=container_name,
                blob_name=blob_name,
                account_key=os.getenv("AZURE_ACCOUNT_KEY"),
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=1)  # Lien valide pour 1 heure
            )
            file_url = f"https://{os.getenv('AZURE_ACCOUNT_NAME')}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"

            # Enregistrer le fichier dans la base de données
            uploads[file_id] = 'saving_metadata'
            user = User.query.filter_by(username=username).first()
            if not user:
                raise ValueError(f"Utilisateur {username} introuvable dans la base de données")

            new_file = File(
                name=filename,
                extension=extension,
                created_at=datetime.utcnow(),
                last_opened=datetime.utcnow(),
                original_size=original_size,
                user_id=user.id,
                azure_blob_path=file_url  # Enregistrer le lien temporaire
            )
            db.session.add(new_file)
            db.session.commit()  # Commit explicite

            # Envoyer un message dans Azure Queue Storage pour compression
            queue_client = QueueClient.from_connection_string(queue_connection_string, queue_name)
            message = {
                "username": username,
                "filename": filename,
                "extension": extension,
                "blob_name": blob_name,
                "container_name": container_name
            }
            queue_client.send_message(json.dumps(message))
            app.logger.debug(f"Message envoyé à la file d'attente : {message}")

            uploads[file_id] = 'completed'
            app.logger.debug(f"Métadonnées enregistrées : {new_file.original_size} => {new_file.azure_blob_path}")

        except Exception as e:
            app.logger.error(f"Erreur lors de l'upload du fichier : {e}")
            uploads[file_id] = 'failed'

            # Suppression du blob si l'upload est réussi mais la BDD échoue
            if blob_client:
                try:
                    blob_client.delete_blob()
                    app.logger.debug(f"Blob {blob_name} supprimé suite à une erreur.")
                except Exception as azure_error:
                    app.logger.error(f"Erreur lors de la suppression du blob {blob_name} : {azure_error}")


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

    # Calculer la taille totale des fichiers originaux
    total_original_size = sum(file.original_size for file in user_files)
    
    # Récupérer la taille totale des fichiers compressés depuis Azure
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
    total_compressed_size = get_user_compressed_storage(username, container_name, connection_string)

    # Calculer les informations de stockage
    max_storage_size = 5  # 5 Go
    space_saved = total_original_size - total_compressed_size
    space_available = max_storage_size - total_compressed_size

    return jsonify({
        'total_original_size': total_original_size,
        'total_compressed_size': total_compressed_size,
        'space_saved': space_saved,
        'total_space': max_storage_size,
        'space_available': space_available
    })

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


def get_user_compressed_storage(username, container_name, connection_string):
    """
    Récupère la taille totale des fichiers compressés pour un utilisateur spécifique.

    :param username: Nom d'utilisateur
    :param container_name: Nom du conteneur Azure Blob
    :param connection_string: Chaîne de connexion Azure
    :return: Taille totale en octets des fichiers compressés
    """
    container_client = ContainerClient.from_connection_string(connection_string, container_name)
    total_compressed_size = 0

    # Lister tous les blobs dans le dossier de l'utilisateur
    blobs = container_client.list_blobs(name_starts_with=f"{username}/")
    
    for blob in blobs:
        total_compressed_size += blob.size

    return total_compressed_size


def generate_sync_sas(user_folder):
    """Génère un lien SAS pour un dossier utilisateur spécifique."""
    # Récupérer les paramètres depuis les variables d'environnement
    storage_account_name = os.getenv("AZURE_ACCOUNT_NAME")
    storage_account_key = os.getenv("AZURE_ACCOUNT_KEY")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

    if not all([storage_account_name, storage_account_key, container_name]):
        raise ValueError("Les variables d'environnement AZURE_ACCOUNT_NAME, AZURE_ACCOUNT_KEY et AZURE_STORAGE_CONTAINER_NAME doivent être définies.")

    # Générer le lien SAS pour le conteneur avec des permissions restreintes
    sas_token = generate_container_sas(
        account_name=storage_account_name,
        container_name=container_name,
        account_key=storage_account_key,
        permission=ContainerSasPermissions(read=True, write=True, list=True),
        expiry=datetime.utcnow() + timedelta(days=30)  # Valide 30 jours
    )

    # Retourner l'URL complète avec le préfixe de dossier
    return f"https://{storage_account_name}.blob.core.windows.net/{container_name}/{user_folder}?{sas_token}"


@user_files_bp.route('/get_sync_script', methods=['POST'])
@jwt_required()
def get_sync_script():
    """
    Génère un script PowerShell pour synchroniser un dossier local avec un dossier Azure Blob Storage.
    Le chemin local est envoyé par le client dans le corps de la requête.
    """
    AZCOPY_DOWNLOAD_URL = "https://aka.ms/downloadazcopy-v10-windows"

    # Récupérer le chemin local depuis la requête
    data = request.json
    user_folder = get_jwt_identity()
    local_path = data.get("local_path")  # Chemin local choisi par l'utilisateur

    if not user_folder or not local_path:
        return jsonify({"error": "Le dossier utilisateur et le chemin local sont requis"}), 400

    # Générer le lien SAS
    try:
        sas_url = generate_sync_sas(user_folder)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Créer le script PowerShell
    script_content = f"""
        # Variables
        $Global:azcopyExePath = ""
        $azcopyUrl = "{AZCOPY_DOWNLOAD_URL}"
        $azcopyZipPath = "$env:USERPROFILE\\Downloads\\azcopy.zip"
        $azcopyExtractBasePath = "$env:USERPROFILE\\azcopy"
        $localPath = "{local_path}"  # Chemin local fourni par l'utilisateur
        $remotePath = "{sas_url}"    # Lien SAS vers Azure Blob Storage
        $logFile = "$env:USERPROFILE\\Downloads\\azcopy_log.txt"
        $azcopyLog = "$env:USERPROFILE\\Downloads\\azcopy_detailed_log.txt"

        Write-Output "Début du script PowerShell."

        # Fonction : Installer AzCopy si nécessaire
        function Install-AzCopy {{
            if (!(Test-Path $azcopyExtractBasePath)) {{
                New-Item -ItemType Directory -Path $azcopyExtractBasePath | Out-Null
            }}
            if (!(Get-Command azcopy.exe -ErrorAction SilentlyContinue)) {{
                Write-Output "Téléchargement d'AzCopy..."
                Invoke-WebRequest -Uri $azcopyUrl -OutFile $azcopyZipPath -UseBasicParsing
                Write-Output "Extraction d'AzCopy..."
                Expand-Archive -Path $azcopyZipPath -DestinationPath $azcopyExtractBasePath -Force
                Remove-Item $azcopyZipPath -Force
            }}
            $Global:azcopyExePath = Get-ChildItem -Path $azcopyExtractBasePath -Recurse -Filter "azcopy.exe" | Select-Object -ExpandProperty FullName -First 1
            if (-not $Global:azcopyExePath) {{
                Write-Output "Erreur : Impossible de trouver l'exécutable AzCopy après extraction."
                Pause
                exit 1
            }}
            Write-Output "Exécutable AzCopy trouvé : $Global:azcopyExePath"
        }}

        # Fonction : Synchronisation locale vers Azure
        function Sync-ToAzure {{
            Write-Output "Synchronisation des fichiers locaux vers Azure..."
            if (-not $Global:azcopyExePath) {{
                Write-Output "Erreur : AzCopy n'a pas été correctement initialisé."
                return
            }}
            try {{
                $command = "& `"$Global:azcopyExePath`" sync `"$localPath`" `"$remotePath`" --log-level=INFO --include-directory-stub"
                Write-Output "Exécution de la commande : $command"
                Invoke-Expression $command 2>&1 | Tee-Object -FilePath $logFile
                Write-Output "Synchronisation locale vers Azure terminée."
            }} catch {{
                Write-Output "Erreur lors de la synchronisation locale vers Azure : $($_.Exception.Message)"
            }}
        }}

        # Fonction : Synchronisation Azure vers local
        function Sync-ToLocal {{
            Write-Output "Synchronisation des fichiers Azure vers le dossier local..."
            if (-not $Global:azcopyExePath) {{
                Write-Output "Erreur : AzCopy n'a pas été correctement initialisé."
                return
            }}
            try {{
                $command = "& `"$Global:azcopyExePath`" sync `"$remotePath`" `"$localPath`" --log-level=INFO --include-directory-stub"
                Write-Output "Exécution de la commande : $command"
                Invoke-Expression $command 2>&1 | Tee-Object -FilePath $logFile
                Write-Output "Synchronisation Azure vers local terminée."
            }} catch {{
                Write-Output "Erreur lors de la synchronisation Azure vers local : $($_.Exception.Message)"
            }}
        }}

        # Fonction : Surveillance des changements locaux
        function Start-Watcher {{
            Write-Output "Activation de la surveillance des changements locaux..."
            $watcher = New-Object System.IO.FileSystemWatcher
            $watcher.Path = $localPath
            $watcher.IncludeSubdirectories = $true
            $watcher.EnableRaisingEvents = $true
            $watcher.NotifyFilter = [System.IO.NotifyFilters]::FileName, [System.IO.NotifyFilters]::LastWrite

            Register-ObjectEvent -InputObject $watcher -EventName "Changed" -Action {{
                Write-Output "Changement détecté dans le dossier local."
                Sync-ToAzure
            }}
            Register-ObjectEvent -InputObject $watcher -EventName "Created" -Action {{
                Write-Output "Fichier créé dans le dossier local."
                Sync-ToAzure
            }}
            Register-ObjectEvent -InputObject $watcher -EventName "Deleted" -Action {{
                Write-Output "Fichier supprimé dans le dossier local."
                Sync-ToAzure
            }}
            Write-Output "Surveillance du dossier local activée."
        }}

        # Fonction : Synchronisation périodique Azure → Local
        function Periodic-Sync-ToLocal {{
            while ($true) {{
                try {{
                    Write-Output "Synchronisation périodique Azure vers local..."
                    Sync-ToLocal
                    Write-Output "Synchronisation périodique terminée."
                }} catch {{
                    Write-Output "Erreur lors de la synchronisation périodique Azure vers local : $($_.Exception.Message)"
                }}
                Start-Sleep -Seconds 300  # Répéter toutes les 5 minutes
            }}
        }}

        # Étape 1 : Installer AzCopy
        Install-AzCopy

        # Vérifiez l'exécutable global
        Write-Output "Chemin AzCopy global après installation : $Global:azcopyExePath"

        # Étape 2 : Synchronisation initiale
        Sync-ToAzure
        Sync-ToLocal

        # Étape 3 : Activer la surveillance des changements locaux
        Start-Watcher

        # Étape 4 : Lancer la synchronisation périodique Azure → Local
        Write-Output "Lancement de la synchronisation permanente. Appuyez sur Ctrl+C pour arrêter."
        Periodic-Sync-ToLocal
    """


    # Créer un fichier temporaire pour le script en forçant l'encodage UTF-8
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ps1", delete=False, encoding="utf-8") as script_file:
            script_file.write(script_content)
            script_path = script_file.name
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la création du fichier script : {str(e)}"}), 500

    # Retourner le fichier PowerShell au client
    return send_file(script_path, as_attachment=True, download_name="sync_script.ps1")

