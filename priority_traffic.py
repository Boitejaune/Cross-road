import random
import time
import multiprocessing

# Génération de trafic prioritaire
# Générer des voitures à intervalles aléatoires et les ajouter à une queue (car_queue)
def priority_traffic_gen(queue_0, queue_1, queue_2, queue_3,priority_queue):

    dico_queues = {0 : queue_0,
                   1 : queue_1,
                   2 : queue_2,
                   3 : queue_3}
    priority_queue = []
    
    while True:
        # Génère des voitures à des intervalles aléatoires
        time.sleep(random.uniform(4, 5))  

        # Choix source 
        source = random.choice([0, 1, 2, 3])
        priority_queue.append(source)

        # Création des caractéristiques direction, priorité des voitures 
        possible_directions = [d for d in [0, 1, 2, 3] if d != source]
        direction = random.choice(possible_directions) # Avec direction != source

        car = {"direction": direction, "priority": True}
        print(f"New car created: {car}")
        print(f"Vérification source : {source}")

        # ajout des voitures à la queue qu'il faut
        dico_queues[source].put(car)
        print(dico_queues)
        for i in range(len(dico_queues)):
            print(f"Queue {i} size: {dico_queues[i].qsize()}")
        print(dico_queues, priority_queue)


# Pour tester :
if __name__ == "__main__":
    # Création des queues
    queue_0 = multiprocessing.Queue()
    queue_1 = multiprocessing.Queue()
    queue_2 = multiprocessing.Queue()
    queue_3 = multiprocessing.Queue()
    priority_queue = multiprocessing.Queue()
    # Lancer la génération de trafic
    priority_traffic_gen(queue_0, queue_1, queue_2, queue_3,priority_queue)