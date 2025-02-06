import random
import time
import sysv_ipc
import json  # Pour convertir le dictionnaire en bytes

def normal_traffic_gen():
    
    key = 128

    queue_0 = sysv_ipc.MessageQueue(key)
    queue_1 = sysv_ipc.MessageQueue(key+1)
    queue_2 = sysv_ipc.MessageQueue(key+2)
    queue_3 = sysv_ipc.MessageQueue(key+3)

    dico_queues = {0: queue_0, 1: queue_1, 2: queue_2, 3: queue_3}
    
    while True:
        # Génère des voitures à des intervalles aléatoires
        time.sleep(1)
        #time.sleep(random.uniform(1, 5))  

        # Choix source 
        source = random.choice([0, 1, 2, 3])

        # Création des caractéristiques direction, priorité des voitures 
        possible_directions = [d for d in [0, 1, 2, 3] if d != source]
        direction = random.choice(possible_directions)  # Avec direction != source

        car = {"direction": direction, "priority": False}
        print(f"Nouvelle voiture : {car} (de {source})")

        # Convertir en JSON et envoyer dans la file de messages
        car_bytes = json.dumps(car).encode('utf-8')  # Convertir en bytes
        dico_queues[source].send(car_bytes)  # Envoyer dans la MessageQueue

        # Afficher la taille des queues
        for i in range(len(dico_queues)):
            print(f"Queue {i} size: {dico_queues[i].current_messages}")
