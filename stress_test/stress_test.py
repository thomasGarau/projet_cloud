import threading
import time
import os
import psutil

def stress_cpu(cpu_percentage=70):
    """
    Simule une charge CPU à un certain pourcentage.
    """
    num_cores = psutil.cpu_count(logical=True)
    active_cores = max(1, int((cpu_percentage / 100) * num_cores))

    def cpu_task():
        while True:
            pass  # Boucle infinie pour consommer les cycles CPU

    print(f"[INFO] Stress CPU : utilisation prévue de {cpu_percentage}% ({active_cores} threads actifs sur {num_cores} cœurs)...")
    threads = []
    for _ in range(active_cores):
        t = threading.Thread(target=cpu_task, daemon=True)
        t.start()
        threads.append(t)
    return threads

def stress_memory(percentage=70, duration=60):
    """
    Simule une charge mémoire en allouant un pourcentage de la RAM totale pendant une durée donnée.
    """
    total_memory = psutil.virtual_memory().total
    allocate_memory = int((percentage / 100) * total_memory)  # Calcul des octets à allouer

    print(f"[INFO] Stress mémoire : allocation prévue de {allocate_memory // (1024 * 1024)} MB ({percentage}% de la RAM)...")
    try:
        memory_hog = bytearray(allocate_memory)  # Alloue un grand bloc de mémoire
        time.sleep(duration)  # Maintient la mémoire allouée pendant la durée
        return memory_hog
    except MemoryError:
        print("[ERROR] Impossible d'allouer plus de mémoire.")
        return None

def stress_disk(write_size_mb=100, duration=30):
    """
    Simule une charge disque en écrivant et supprimant des fichiers de manière répétée.
    """
    print(f"[INFO] Stress disque : écriture de {write_size_mb} MB en boucle pendant {duration} secondes...")
    stop_time = time.time() + duration
    try:
        while time.time() < stop_time:
            with open("stress_test_temp_file.bin", "wb") as f:
                f.write(os.urandom(write_size_mb * 1024 * 1024))  # Écrit des données aléatoires
            os.remove("stress_test_temp_file.bin")  # Supprime immédiatement le fichier
            time.sleep(0.5)  # Pause entre les cycles pour éviter la saturation
    except Exception as e:
        print(f"[ERROR] Erreur lors du stress disque : {e}")

def main():
    print("[INFO] Démarrage du stress test adapté à 70 % des ressources...")

    try:
        # CPU : Utilise environ 70 % des cœurs logiques
        cpu_threads = stress_cpu(cpu_percentage=70)

        # Mémoire : Alloue environ 70 % de la RAM totale
        memory_hog = stress_memory(percentage=70, duration=60)

        # Disque : Écrit des fichiers de 100 MB pendant 30 secondes
        stress_disk(write_size_mb=100, duration=30)

        print("[INFO] Stress test en cours... Appuyez sur Ctrl+C pour arrêter.")
        for t in cpu_threads:
            t.join()

    except KeyboardInterrupt:
        print("[INFO] Stress test interrompu par l'utilisateur.")
    finally:
        if memory_hog:
            del memory_hog  # Libère la mémoire

if __name__ == "__main__":
    main()
