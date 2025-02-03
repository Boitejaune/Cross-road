import time
<<<<<<< HEAD
import multiprocessing
import socket
=======
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
            if (direction == 0 and light_queue.get() == "GREEN") or \
               (direction == 1 and light_queue.get() == "GREEN"):
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
"""

def coordinator(ns_queue, we_queue, shared_mem):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 5000))  # Envoi des voitures à display

    while True:
        time.sleep(0.1)  # Vérification rapide
        
        # Récupérer l'état des feux depuis la shared memory
        lights_status = ''.join(shared_mem).strip().split()  # Nettoyage de l'espace mémoire
        ns_light, we_light = lights_status[0], lights_status[1]

        # Envoyer uniquement les voitures qui peuvent avancer
        if ns_light == "GREEN" and not ns_queue.empty():
            car = ns_queue.get()
            sock.sendall(f"{car}\n".encode())

        if we_light == "GREEN" and not we_queue.empty():
            car = we_queue.get()
            sock.sendall(f"{car}\n".encode())
"""