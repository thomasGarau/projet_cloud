import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env au moment de l'import du package
load_dotenv()

# Expose des constantes ou des configurations globales si nécessaire
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_QUEUE_NAME = os.getenv("AZURE_QUEUE_NAME")
AZURE_STORAGE_CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
