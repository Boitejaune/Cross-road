import lights 
import coordinateur
import normal_traffic
import display
import priority_traffic
import multiprocessing



if __name__ == "__main__":
    # Création des queues pour la communication entre les processus
    car_queue = multiprocessing.Queue()  # Queue des véhicules normaux
    NS_queue = multiprocessing.Queue()
    WE_queue = multiprocessing.Queue()
    
    priority_queue = multiprocessing.Queue()  # Queue des véhicules prioritaires (désactivé)
    light_queue = multiprocessing.Queue()  # Queue des feux de circulation
    
    light_queue.put("GREEN")  # Initialiser les feux
    
    # Démarrer les processus
    p_lights = multiprocessing.Process(target=lights.lights_process, args=(light_queue,))
    p_normal_traffic = multiprocessing.Process(target=normal_traffic.normal_traffic_gen, args=(car_queue,))
    # p_priority_traffic = multiprocessing.Process(target=priority_traffic_gen, args=(priority_queue,))  # Désactivé
    p_coordinator = multiprocessing.Process(target=coordinateur.coordinator, args=(car_queue, priority_queue, light_queue))
    
    p_lights.start()
    p_normal_traffic.start()
    # p_priority_traffic.start()  # Désactivé
    p_coordinator.start()
    
    # Lancer l'interface graphique
    display.run_gui(priority_queue)
    
    # Terminer les processus à la fin
    p_lights.terminate()
    p_normal_traffic.terminate()
    # p_priority_traffic.terminate()  # Désactivé
    p_coordinator.terminate()