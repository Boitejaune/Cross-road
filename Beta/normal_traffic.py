import random
import time
import multiprocessing

# Génération de trafic normal
# Générer des voitures à intervalles aléatoires et les ajouter à une queue (car_queue)
def normal_traffic_gen(NS_queue, WE_queue):

    dico_queues = {0 : NS_queue,
                   1 : WE_queue} # refaire correctement après
    
    while True:
        time.sleep(random.uniform(1, 5))  # Génère des voitures à des intervalles aléatoires
        direction = random.choice([0,1])
        car = {"direction": dico_queues[direction], "priority": False}
        print(f"New car created: {car}")
        dico_queues[direction].put(car)
        print(dico_queues)

if __name__ == "__main__":
    car_queue = multiprocessing.Queue()
    normal_traffic_gen(car_queue)
