import random
import time
import multiprocessing
import priority_traffic

# Génération de trafic normal
# Générer des voitures à intervalles aléatoires et les ajouter à une queue (car_queue)
def normal_traffic_gen(queue_0, queue_1, queue_2, queue_3):

    dico_queues = {0 : queue_0,
                   1 : queue_1,
                   2 : queue_2,
                   3 : queue_3}
    
    while True:
        # Génère des voitures à des intervalles aléatoires
        time.sleep(random.uniform(1, 5))  

        # Choix source 
        source = random.choice([0, 1, 2, 3])

        # Création des caractéristiques direction, priorité des voitures 
        possible_directions = [d for d in [0, 1, 2, 3] if d != source]
        direction = random.choice(possible_directions) # Avec direction != source

        car = {"direction": direction, "priority": False}
        print(f"New car created: {car}")
        print(f"Vérification source : {source}")

        # ajout des voitures à la queue qu'il faut
        dico_queues[source].put(car)
        print(dico_queues)
        for i in range(len(dico_queues)):
            print(f"Queue {i} size: {dico_queues[i].qsize()}")

"""
# Pour tester :
if __name__ == "__main__":
    # Création des queues
    queue_0 = multiprocessing.Queue()
    queue_1 = multiprocessing.Queue()
    queue_2 = multiprocessing.Queue()
    queue_3 = multiprocessing.Queue()

    # Lancer la génération de trafic
    # normal_traffic_gen(queue_0, queue_1, queue_2, queue_3)

    # Création des processus
    normal_process = multiprocessing.Process(target=normal_traffic_gen, args=(queue_0, queue_1, queue_2, queue_3))
    priority_process = multiprocessing.Process(target=priority_traffic.priority_traffic_gen, args=(queue_0, queue_1, queue_2, queue_3))

    # Lancer les processus
    normal_process.start()
    priority_process.start()

    # Attendre que les processus terminent (normalement, ils tournent en boucle infinie)
    normal_process.join()
    priority_process.join()
"""