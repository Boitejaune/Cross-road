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




if __name__ == "__main__":
    # Création des queues pour la communication entre les processus
    queue_0 = multiprocessing.Queue()
    queue_1 = multiprocessing.Queue()
    queue_2 = multiprocessing.Queue()
    queue_3 = multiprocessing.Queue()
    priority_queue = multiprocessing.Queue()
    
    # def la shared memory array lights
    dico_feu = {0 : "RED",
                1 : "GREEN",
                2 : "RED",
                3 : "GREEN"}
    light_array = multiprocessing.Array(dico_feu)
    
    # Démarrer les processus
    p_lights = multiprocessing.Process(target=lights.lights_process, args=(queue_0, queue_1, queue_2, queue_3, light_array,priority_queue))
    p_normal_traffic = multiprocessing.Process(target=normal_traffic.normal_traffic_gen, args=(queue_0, queue_1, queue_2, queue_3))
    p_priority_traffic = multiprocessing.Process(target=priority_traffic.priority_traffic_gen, args=(queue_0, queue_1, queue_2, queue_3,priority_queue))

    p_lights.start()
    p_normal_traffic.start()
    PID_FEUX = p_lights.pid
    p_priority_traffic.start()


    p_coordinator = multiprocessing.Process(target=coordinator.coordinator, args=(queue_0, queue_1, queue_2, queue_3, priority_queue, light_array, PID_FEUX))
    p_coordinator.start()
    p_coordinator.join()

    # Lancer l'interface graphique
    display.run_gui()
    
    # Terminer les processus à la fin
    p_lights.terminate()
    p_normal_traffic.terminate()
    # p_priority_traffic.terminate()  # Désactivé
    p_coordinator.terminate()