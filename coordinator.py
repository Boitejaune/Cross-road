# récupère chaque queue de route, PID feux pour les signaux, shared memory array lights
# pour chaque queue, vérif si il y a des véhicules
    # oui : véhicule prio ?
        # oui : envoie un signal à lights
        # non : si feux vert de la shared memory, de la source = n° queue, alors passe
                # sinon bloque

import time
import sysv_ipc
import socket
import os
import signal
import json


# Processus de coordination des véhicules : Vérifie les feux avant de permettre aux voitures de circuler. Si le feu est vert pour la direction d'une voiture, elle peut avancer.
def coordinator(priority_queue, light_array, PID_FEUX):
    print(PID_FEUX)

    key = 128

    Mqueue_0 = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREX)
    Mqueue_1 = sysv_ipc.MessageQueue(key+1, sysv_ipc.IPC_CREX)
    Mqueue_2 = sysv_ipc.MessageQueue(key+2, sysv_ipc.IPC_CREX)
    Mqueue_3 = sysv_ipc.MessageQueue(key+3, sysv_ipc.IPC_CREX)


    while True:
        Cqueue_0, _ = Mqueue_0.receive()  # Lire un message
        queue_0 = json.loads(Cqueue_0.decode('utf-8'))  # Convertir bytes -> dict
        print(f"🚦 Voiture reçue : {car}")


        time.sleep(0.1)
        
        # Gérer les véhicules en fonction des feux
        if queue_0 or queue_1 or queue_2 or queue_3:
            # Si le feu est vert pour la direction du véhicule, il peut passer
            if (direction == 0 and light_queue.get() == "GREEN") or \
               (direction == 1 and light_queue.get() == "GREEN"):
                
            if (len(priority_queue)>0):
                if (priority_queue[0] == 0):
                    os.kill(PID_FEUX,signal.SIGUSR1)
                if (priority_queue[0] == 1):
                    os.kill(PID_FEUX,signal.SIGUSR2)
                if (priority_queue[0] == 2):
                    os.kill(PID_FEUX,signal.SIGUSRTERM)
                else:
                    os.kill(PID_FEUX,signal.SIGUSRINT)
            if (direction == "NS" and light_queue.get() == "GREEN") or \
               (direction == "WE" and light_queue.get() == "GREEN"):

                # Logique pour faire avancer la voiture (ex. déplacer sur l'écran)
                pass  # On ajoutera la gestion de l'avancement plus tard
