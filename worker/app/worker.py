import json
import io
import logging
import os
import time
from azure.storage.queue import QueueClient
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError, AzureError
from app.utils import compresse_file

# Réduire les logs des bibliothèques Azure
logging.getLogger("azure").setLevel(logging.WARNING)
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)

def start_worker():
    # Configuration du logger
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("Worker")

    # Connexion aux services Azure
    queue_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    queue_name = os.getenv("AZURE_QUEUE_NAME", "compression-queue")
    blob_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

    # Connexion aux services Azure
    queue_client = QueueClient.from_connection_string(queue_connection_string, queue_name)
    blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    # Vérification ou création de la file d’attente
    try:
        queue_client.create_queue()
        logger.info(f"File d'attente '{queue_name}' créée avec succès.")
    except ResourceExistsError:
        logger.info(f"File d'attente '{queue_name}' déjà existante.")
    except AzureError as e:
        logger.error(f"Erreur lors de la vérification ou de la création de la file d'attente : {e}")
        return

    logger.info("Worker démarré. En attente de messages...")

    while True:
        try:
            messages = queue_client.receive_messages()
            if not messages:
                logger.info("Aucun message à traiter. En attente...")
                time.sleep(2)
                continue
        except AzureError as e:
            logger.error(f"Erreur lors de la réception des messages : {e}")
            time.sleep(5)  # Attendez 5 secondes avant de réessayer
            continue

        for message in messages:
            try:
                logger.info(f"Message reçu : {message.content}")
                message_content = json.loads(message.content)

                # Extraire les informations
                username = message_content.get("username")
                filename = message_content.get("filename")
                extension = message_content.get("extension")
                blob_name = message_content.get("blob_name")

                if not all([username, filename, extension, blob_name]):
                    raise ValueError(f"Données manquantes ou invalides dans le message : {message_content}")

                # Télécharger le fichier temporaire
                logger.info(f"Téléchargement du fichier : {blob_name}")
                blob_client = container_client.get_blob_client(blob_name)
                stream = io.BytesIO()
                blob_client.download_blob().readinto(stream)
                file_content = stream.getvalue()
                stream.close()

                # Compression du fichier
                logger.info(f"Compression du fichier : {filename}{extension}")
                compressed_content = compresse_file(file_content, extension)

                # Sauvegarder le fichier compressé
                compressed_blob_name = f"{username}/{filename}_compressed.bin"
                compressed_blob_client = container_client.get_blob_client(compressed_blob_name)
                compressed_blob_client.upload_blob(compressed_content, overwrite=True)
                logger.info(f"Fichier compressé sauvegardé sous : {compressed_blob_name}")

                # Supprimer le fichier temporaire
                blob_client.delete_blob()
                logger.info(f"Fichier temporaire supprimé : {blob_name}")

                # Supprimer le message de la file d’attente
                queue_client.delete_message(message)
                logger.info(f"Message traité et supprimé de la file d'attente.")

            except json.JSONDecodeError as e:
                logger.error(f"Erreur de décodage JSON pour le message : {e}")
                queue_client.delete_message(message)  # Supprimez les messages corrompus
            except ValueError as e:
                logger.error(f"Erreur dans les données du message : {e}")
                queue_client.delete_message(message)  # Supprimez les messages invalides
            except AzureError as e:
                logger.error(f"Erreur Azure pendant le traitement : {e}")
            except Exception as e:
                logger.error(f"Erreur inattendue lors du traitement du message : {e}")
