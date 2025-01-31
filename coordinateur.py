import time
import os
import signal

# Processus de coordination des véhicules : Vérifie les feux avant de permettre aux voitures de circuler. Si le feu est vert pour la direction d'une voiture, elle peut avancer.
def coordinator(car_queue, priority_queue, light_queue,PID_FEUX):
    print(PID_FEUX)
    while True:
        time.sleep(0.1)
        
        # Gérer les véhicules en fonction des feux
        if not car_queue.empty():
            car_info = car_queue.get()
            direction = car_info["direction"]
            # Si le feu est vert pour la direction du véhicule, il peut passer
            if car_info["priority"] == True:
                if car_info["Direction"] == 0:
                    os.kill(PID_FEUX,signal.SIGUSR1)
                if car_info["Direction"] == 0:
                    os.kill(PID_FEUX,signal.SIGUSR2)
                if car_info["Direction"] == 0:
                    os.kill(PID_FEUX,signal.SIGUSRTERM)
                else:
                    os.kill(PID_FEUX,signal.SIGUSRINT)
            if (direction == "NS" and light_queue.get() == "GREEN") or \
               (direction == "WE" and light_queue.get() == "GREEN"):
                # Logique pour faire avancer la voiture (ex. déplacer sur l'écran)
                pass  # On ajoutera la gestion de l'avancement plus tard