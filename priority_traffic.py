import random
import time

# Génération de trafic priorirtaire
# Générer des voitures à intervalles aléatoires et les ajouter à une queue (car_queue)
def normal_traffic_gen(car_queue):
    while True:
        time.sleep(random.uniform(0.5, 2))  # Génère des voitures à des intervalles aléatoires
        direction = random.choice([0, 1])
        car = {"direction": direction, "priority": True}
        car_queue.put(car)