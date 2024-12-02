import json
import io
import logging
import os
import time
import psutil
from azure.storage.queue import QueueClient
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError, AzureError
from app.utils import compresse_file


# Réduire les logs des bibliothèques Azure
logging.getLogger("azure").setLevel(logging.WARNING)
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)

def start_worker():
    logger = setup_logger()
    queue_client, container_client = setup_azure_connections(logger)

    if not queue_client or not container_client:
        logger.error("Erreur lors de la configuration des connexions Azure. Arrêt du worker.")
        return

    print("Worker démarré. En attente de messages...")

    batch_size = 5  # Taille initiale des lots

    while True:
        # Calculer le score hybride
        availability_score = calculate_hybrid_availability_score()
        print(f"Score de disponibilité hybride : {availability_score:.2f}")

        # Ajuster la taille des lots en fonction du score hybride
        batch_size = adjust_batch_size_based_on_score(availability_score, batch_size)
        print(f"Taille du lot ajustée : {batch_size}")

        process_queue_messages(queue_client, container_client, logger, batch_size)



def setup_logger():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("Worker")
    return logger


def setup_azure_connections(logger):
    try:
        queue_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        queue_name = os.getenv("AZURE_QUEUE_NAME", "compression-queue")
        blob_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

        queue_client = QueueClient.from_connection_string(queue_connection_string, queue_name)
        blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        # Vérification ou création de la file d’attente
        try:
            queue_client.create_queue()
            print(f"File d'attente '{queue_name}' créée avec succès.")
        except ResourceExistsError:
            print(f"File d'attente '{queue_name}' déjà existante.")

        return queue_client, container_client
    except AzureError as e:
        logger.error(f"Erreur lors de la configuration des services Azure : {e}")
        return None, None


def process_queue_messages(queue_client, container_client, logger, batch_size):
    """
    Traite les messages en fonction de la taille des lots.
    """
    try:
        messages = queue_client.receive_messages(messages_per_page=batch_size)
        if not messages:
            print("Aucun message à traiter. En attente...")
            time.sleep(2)
            return

        for message in messages:
            process_message(message, container_client, queue_client, logger)
    except AzureError as e:
        logger.error(f"Erreur lors de la réception des messages : {e}")
        time.sleep(5)


def process_message(message, container_client, queue_client, logger):
    try:
        print(f"Message reçu : {message.content}")
        message_content = json.loads(message.content)

        # Extraire les informations
        username, filename, extension, blob_name = extract_message_data(message_content)

        # Télécharger et compresser le fichier
        compressed_blob_name = process_blob(
            username, filename, extension, blob_name, container_client, logger
        )

        # Supprimer le fichier temporaire
        container_client.get_blob_client(blob_name).delete_blob()
        print(f"Fichier temporaire supprimé : {blob_name}")

        # Supprimer le message de la file d’attente
        queue_client.delete_message(message)
        print(f"Message traité et supprimé de la file d'attente.")
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


def extract_message_data(message_content):
    username = message_content.get("username")
    filename = message_content.get("filename")
    extension = message_content.get("extension")
    blob_name = message_content.get("blob_name")

    if not all([username, filename, extension, blob_name]):
        raise ValueError(f"Données manquantes ou invalides dans le message : {message_content}")

    return username, filename, extension, blob_name


def process_blob(username, filename, extension, blob_name, container_client, logger):
    # Télécharger le fichier
    print(f"Téléchargement du fichier : {blob_name}")
    blob_client = container_client.get_blob_client(blob_name)
    stream = io.BytesIO()
    blob_client.download_blob().readinto(stream)
    file_content = stream.getvalue()
    stream.close()

    # Compression du fichier
    print(f"Compression du fichier : {filename}{extension}")
    compressed_content = compresse_file(file_content, extension)

    # Sauvegarder le fichier compressé
    compressed_blob_name = f"{username}/{filename}_compressed.bin"
    compressed_blob_client = container_client.get_blob_client(compressed_blob_name)
    compressed_blob_client.upload_blob(compressed_content, overwrite=True)
    print(f"Fichier compressé sauvegardé sous : {compressed_blob_name}")

    return compressed_blob_name


def adjust_batch_size_based_on_score(score, current_batch_size, min_batch=0, max_batch=5):
    """
    Ajuste dynamiquement la taille des lots en fonction du score de disponibilité.

    :param score: Score de disponibilité
    :param current_batch_size: Taille actuelle des lots
    :param min_batch: Taille minimale des lots
    :param max_batch: Taille maximale des lots
    :return: Nouvelle taille des lots
    """
    if score >= 85 and current_batch_size == max_batch:
        # Maintenir la taille des lots si on est sous le seuil critique
        return current_batch_size
    elif score > 70:
        # Maximiser les lots progressivement si le score est suffisant
        return min(current_batch_size + 1, max_batch)
    elif score < 50:
        # Réduire les lots si le score est faible
        return max(current_batch_size - 1, min_batch)
    elif score < 20:
        # Forcer à 1 batch si la situation est critique
        return min_batch
    return current_batch_size



def should_compress(score, current_batch_size, threshold=85):
    """
    Détermine si le worker doit traiter un fichier en fonction du score de disponibilité
    et de la taille des lots.

    :param score: Score de disponibilité
    :param current_batch_size: Taille actuelle des lots
    :param threshold: Seuil critique de charge pour autoriser la compression
    :return: True si la compression est autorisée, False sinon
    """
    # Toujours compresser si on est sous le seuil critique et que des lots sont actifs
    if score >= threshold:
        return True
    # Empêche la compression uniquement si le score est critique
    return score > 50 and current_batch_size > 0


def calculate_hybrid_availability_score(cpu_threshold=80, memory_threshold=80, critical_threshold=90):
    """
    Calcule un score hybride basé sur CPU, mémoire et activité disque.
    """
    cpu_usage = psutil.cpu_percent(interval=0.5)
    memory_usage = psutil.virtual_memory().percent
    disk_activity_score = get_most_active_disk()

    # Log des ressources
    print(f"Utilisation CPU : {cpu_usage}%, Mémoire : {memory_usage}%, Activité disque : {disk_activity_score:.2f}%")

    # Calcul des scores individuels
    cpu_score = max(0, 100 - (cpu_usage / cpu_threshold) * 100)
    memory_score = max(0, 100 - (memory_usage / memory_threshold) * 100)
    disk_score = max(0, 100 - disk_activity_score)

    # Si l'un des éléments dépasse le seuil critique
    if cpu_usage > critical_threshold or memory_usage > critical_threshold or disk_activity_score > 90:
        return min(cpu_score, memory_score, disk_score)

    # Moyenne pondérée
    total_score = (cpu_score * 0.4) + (memory_score * 0.3) + (disk_score * 0.3)
    print(f"Scores individuels : CPU={cpu_score:.2f}, Mémoire={memory_score:.2f}, Disque={disk_score:.2f}")
    return total_score


def list_all_disks():
    partitions = psutil.disk_partitions()
    disks = [partition.device for partition in partitions]
    return disks


def get_most_active_disk():
    """
    Calcule un pourcentage d'utilisation basé sur l'activité du disque le plus actif.
    """
    DISK_CAPACITIES = {
        "PhysicalDrive0": {"read": 180_000_000, "write": 180_000_000},  # 180 Mo/s
        "PhysicalDrive1": {"read": 550_000_000, "write": 550_000_000},  # 550 Mo/s
        "PhysicalDrive2": {"read": 550_000_000, "write": 550_000_000},  # 550 Mo/s
    }

    disk_io_start = psutil.disk_io_counters(perdisk=True)
    time.sleep(1)  # Mesure sur une seconde
    disk_io_end = psutil.disk_io_counters(perdisk=True)

    max_read_percentage = 0
    max_write_percentage = 0

    print("Activité des disques :")
    for disk, counters in disk_io_start.items():
        read_diff = disk_io_end[disk].read_bytes - disk_io_start[disk].read_bytes
        write_diff = disk_io_end[disk].write_bytes - disk_io_start[disk].write_bytes

        # Obtenir les capacités maximales du disque
        disk_capacity = DISK_CAPACITIES.get(disk, {"read": 100_000_000, "write": 100_000_000})  # Valeurs par défaut
        read_threshold = disk_capacity["read"]
        write_threshold = disk_capacity["write"]

        # Calcul des pourcentages
        read_percentage = (read_diff / read_threshold) * 100 if read_threshold > 0 else 0
        write_percentage = (write_diff / write_threshold) * 100 if write_threshold > 0 else 0

        max_read_percentage = max(max_read_percentage, read_percentage)
        max_write_percentage = max(max_write_percentage, write_percentage)

    return max(max_read_percentage, max_write_percentage)

