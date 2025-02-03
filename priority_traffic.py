import random
import time

# Génération de trafic priorirtaire
# Générer des voitures à intervalles aléatoires et les ajouter à une queue (car_queue)
def normal_traffic_gen(car_queue):
    while True:
<<<<<<< HEAD
        time.sleep(random.uniform(0.5, 2))  # Génère des voitures à des intervalles aléatoires
        direction = random.choice([0, 1])
=======
        time.sleep(random.uniform(0.5, 20))  # Génère des voitures à des intervalles aléatoires
        direction = random.choice(["NS", "WE"])
>>>>>>> 8336a699d65685c4249c005e296f42a735862e9c
        car = {"direction": direction, "priority": True}
        car_queue.put(car)