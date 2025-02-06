import lights
import coordinator
import normal_traffic
import display
import priority_traffic
import multiprocessing
import sysv_ipc
import threading
import time

# Fonction pour nettoyer la file de messages existante
def cleanup_message_queue(key):
    try:
        queue = sysv_ipc.MessageQueue(key)
        print(f"Suppression de la file de messages avec la clé {key}")
        queue.remove()
    except sysv_ipc.ExistentialError:
        pass  # La file n'existe pas, rien à faire

# Fonction pour démarrer les processus
def start_processes(manager):
    light_lock = multiprocessing.Lock()
    locks = [multiprocessing.Lock() for _ in range(4)]  # Verrous pour les 4 queues

    # Création des queues pour la communication entre les processus
    priority_queue = multiprocessing.Queue()

    # Dictionnaire partagé pour les feux de circulation
    light_dict = manager.dict({0: "RED", 1: "GREEN", 2: "RED", 3: "GREEN"})

    key = 128

    # Nettoyage des files existantes
    for i in range(4):
        cleanup_message_queue(key + i)

    mqueues = [sysv_ipc.MessageQueue(key + i, sysv_ipc.IPC_CREX) for i in range(4)]

    # Démarrer les processus
    p_lights = multiprocessing.Process(target=lights.lights_process, args=(light_dict, priority_queue, mqueues, light_lock))
    p_normal_traffic = multiprocessing.Process(target=normal_traffic.normal_traffic_gen, args=())
    p_priority_traffic = multiprocessing.Process(target=priority_traffic.priority_traffic_gen, args=(priority_queue,))

    p_lights.start()
    p_normal_traffic.start()
    p_priority_traffic.start()
    PID_FEUX = p_lights.pid

    p_coordinator = multiprocessing.Process(target=coordinator.coordinator, args=(priority_queue, light_dict, mqueues, PID_FEUX, locks))
    p_coordinator.start()

    return p_lights, p_normal_traffic, p_priority_traffic, p_coordinator, mqueues

if __name__ == "__main__":
    # Créer un Manager pour les objets partagés
    with multiprocessing.Manager() as manager:
        # Démarrer l'interface graphique dans un thread avant les autres processus
        gui_thread = threading.Thread(target=display.run_gui)
        gui_thread.start()

        # Petite pause pour s'assurer que le display est bien lancé avant d'envoyer des messages
        time.sleep(1)

        # Démarrer les processus
        p_lights, p_normal_traffic, p_priority_traffic, p_coordinator, mqueues = start_processes(manager)

        try:
            # Attendre la fin de l'exécution du coordinateur
            p_coordinator.join()
        except KeyboardInterrupt:
            print("\n[INFO] Interruption reçue, arrêt des processus...")
        finally:
            # Arrêter proprement les processus
            p_lights.terminate()
            p_normal_traffic.terminate()
            p_priority_traffic.terminate()
            p_coordinator.terminate()

            # Attendre qu'ils se ferment proprement
            p_lights.join()
            p_normal_traffic.join()
            p_priority_traffic.join()
            p_coordinator.join()

        print("[INFO] Tous les processus ont été arrêtés proprement.")
