# queues : une par route : {((destination, prioritaire)), (), ...}
# quand on appelle coordinateur et véhicule, penser à mettre en param chaque queue
# process des lights : thread
# Liste des process à garder pour PID

import lights 
import coordinator
import normal_traffic
import display
import priority_traffic
import multiprocessing
import sysv_ipc

# Fonction pour nettoyer la file de messages existante
def cleanup_message_queue(key):
    try:
        # Essayer d'ouvrir la file de messages
        queue = sysv_ipc.MessageQueue(key)
        print(f"Suppression de la file de messages avec la clé {key}")
        queue.remove()  # Supprimer la file de messages existante
    except sysv_ipc.ExistentialError:
        pass  # Si la file n'existe pas, rien à faire

    
if __name__ == "__main__":
    # Initialiser les verrous pour chaque ressource partagée
    light_lock = multiprocessing.Lock()  # Verrou pour la variable light
    locks = [multiprocessing.Lock() for _ in range(4)]  # Verrous pour les 4 queues (mqueues)
    
    # Création des queues pour la communication entre les processus
    priority_queue = multiprocessing.Queue()
    
    # def la shared memory array lights
    dico_feu = {0 : "RED",
                1 : "GREEN",
                2 : "RED",
                3 : "GREEN"}
    light_dict = multiprocessing.Manager().dict(dico_feu)

    key = 128
    
    # Nettoyer les files existantes avant de créer de nouvelles files
    for i in range(4):
        cleanup_message_queue(key + i)

    mqueues = [sysv_ipc.MessageQueue(key + i, sysv_ipc.IPC_CREX) for i in range(4)]
    
    # Démarrer les processus
    p_lights = multiprocessing.Process(target=lights.lights_process, args=(light_dict,priority_queue, mqueues, light_lock))
    p_normal_traffic = multiprocessing.Process(target=normal_traffic.normal_traffic_gen, args=())
    p_priority_traffic = multiprocessing.Process(target=priority_traffic.priority_traffic_gen, args=(priority_queue,))

    p_lights.start()
    p_normal_traffic.start()
    PID_FEUX = p_lights.pid
    p_priority_traffic.start()


    p_coordinator = multiprocessing.Process(target=coordinator.coordinator, args=(priority_queue, light_dict, mqueues, PID_FEUX, locks))
    p_coordinator.start()
    p_coordinator.join()

    # Lancer l'interface graphique
    display.run_gui()
    
    # Terminer les processus à la fin
    p_lights.terminate()
    p_normal_traffic.terminate()
    # p_priority_traffic.terminate()  # Désactivé
    p_coordinator.terminate()