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
        pass  # Si la file n'existe pas, rien à faire

# Fonction pour démarrer les processus
def start_processes():
    # Initialisation des verrous et queues
    light_lock = multiprocessing.Lock()
    locks = [multiprocessing.Lock() for _ in range(4)]
    priority_queue = multiprocessing.Queue()

    # Nettoyer les files existantes avant de créer de nouvelles files
    key = 128
    for i in range(4):
        cleanup_message_queue(key + i)

    mqueues = [sysv_ipc.MessageQueue(key + i, sysv_ipc.IPC_CREX) for i in range(4)]

    # ✅ Remplacement de Manager().dict par Array pour éviter les erreurs de connexion
    light_array = multiprocessing.Array('u', ["R", "G", "R", "G"])  # 'u' = Unicode (1 caractère par feu)

    # Événement pour signaler l'arrêt propre des processus
    stop_event = multiprocessing.Event()

    # 🔥 On s'assure que le display est lancé AVANT les autres processus
    gui_thread = threading.Thread(target=display.run_gui)
    gui_thread.start()
    time.sleep(1)  # ✅ Attente pour éviter les erreurs de connexion

    # Démarrer les processus avec les bons arguments
    p_lights = multiprocessing.Process(target=lights.lights_process, args=(light_array, priority_queue, mqueues, light_lock))
    p_normal_traffic = multiprocessing.Process(target=normal_traffic.normal_traffic_gen)
    p_priority_traffic = multiprocessing.Process(target=priority_traffic.priority_traffic_gen, args=(priority_queue,))
    p_coordinator = multiprocessing.Process(target=coordinator.coordinator, args=(priority_queue, light_array, mqueues, p_lights.pid, locks))

    p_lights.start()
    p_normal_traffic.start()
    p_priority_traffic.start()
    p_coordinator.start()

    return p_lights, p_normal_traffic, p_priority_traffic, p_coordinator, mqueues, stop_event

if __name__ == "__main__":
    # Démarrer les processus
    p_lights, p_normal_traffic, p_priority_traffic, p_coordinator, mqueues, stop_event = start_processes()

    try:
        p_coordinator.join()
    except KeyboardInterrupt:
        print("\nArrêt détecté, fermeture des processus...")

    # Signaler à tous les processus de s'arrêter proprement
    stop_event.set()

    p_lights.join()
    p_normal_traffic.join()
    p_priority_traffic.join()
    p_coordinator.join()

    print("Tous les processus ont été arrêtés proprement.")
