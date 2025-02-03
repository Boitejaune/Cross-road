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
    print(f"PID : {PID_FEUX}")
    key = 128
    # Création des files de messages pour chaque direction
    Mqueue_0 = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREX)
    Mqueue_1 = sysv_ipc.MessageQueue(key+1, sysv_ipc.IPC_CREX)
    Mqueue_2 = sysv_ipc.MessageQueue(key+2, sysv_ipc.IPC_CREX)
    Mqueue_3 = sysv_ipc.MessageQueue(key+3, sysv_ipc.IPC_CREX)

    while True:
        # Réception des messages de chaque file
        queues = [
            json.loads(Mqueue_0.receive()[0].decode('utf-8')),
            json.loads(Mqueue_1.receive()[0].decode('utf-8')),
            json.loads(Mqueue_2.receive()[0].decode('utf-8')),
            json.loads(Mqueue_3.receive()[0].decode('utf-8'))
        ]
        print(f"Voitures avant feux : {queues}")
        
        # Logique de traitement des véhicules en fonction des feux
        for queue_index, queue_data in enumerate(queues):
            if queue_data:  # Si la file n'est pas vide
                # Vérification de la priorité
                if queue_index in priority_queue.get():
                    # Signaux pour changer les feux selon la priorité
                    signal_map = {
                        0: signal.SIGUSR1,
                        1: signal.SIGUSR2,
                        2: signal.SIGTERM,  # Corrigé de SIGUSRTERM
                        3: signal.SIGINT    # Corrigé de SIGUSRINT
                    }
                    os.kill(PID_FEUX, signal_map.get(queue_index, signal.SIGINT))
                else:
                    # Vérifier si le feu est vert pour cette direction
                    if light_array[queue_index] == 1:  # 1 représente le vert
                        # Autoriser le passage
                        pass
                    else:
                        # Bloquer le passage
                        continue
        
        time.sleep(0.1)  # Petit délai pour éviter la surcharge CPU
        print(f"Voitures après feux : {queues}")