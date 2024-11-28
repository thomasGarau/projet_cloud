from dotenv import load_dotenv
from app.worker import start_worker

# Charger les variables d'environnement depuis .env
load_dotenv()

if __name__ == "__main__":
    # Lancer le worker
    start_worker()
