# récupère chaque queue de route, PID feux pour les signaux, shared memory array lights
# pour chaque queue, vérif si il y a des véhicules
    # oui : véhicule prio ?
        # oui : envoie un signal à lights
        # non : si feux vert de la shared memory, de la source = n° queue, alors passe
                # sinon bloque
"""
import time
import sysv_ipc
import socket
import os
import signal
import json
import sys


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
"""

"""
def coordinator(priority_queue, light_array, PID_FEUX):
   key = 128
   mqueues = [sysv_ipc.MessageQueue(key + i, sysv_ipc.IPC_CREX) for i in range(4)]

   try:
       while True:
           # Reste du code inchangé...
           queues = []
           for mq in mqueues:
               try:
                   msg, _ = mq.receive(block=False) 
                   queues.append(json.loads(msg.decode('utf-8')))
               except sysv_ipc.BusyError:
                   queues.append(None)
                   
           for queue_index, queue_data in enumerate(queues):
               if queue_data:
                   if queue_index in priority_queue.get():
                       signal_map = {0: signal.SIGUSR1, 1: signal.SIGUSR2,
                                   2: signal.SIGTERM, 3: signal.SIGINT}
                       os.kill(PID_FEUX, signal_map.get(queue_index, signal.SIGINT))
                       while mqueues[queue_index].current_messages > 0:
                           mqueues[queue_index].receive()
                   elif light_array[queue_index] == 1:
                       while mqueues[queue_index].current_messages > 0:
                           mqueues[queue_index].receive()
                           
           time.sleep(0.1)

   except sysv_ipc.Error as e:
       print(f"Erreur IPC: {e}")
"""

import os
import signal
import time
import sysv_ipc
import json

def signal_handler(sig, frame):
    cleanup_queues()

def cleanup_queues():
    for i in range(4):
        try:
            queue = sysv_ipc.MessageQueue(128 + i)
            while queue.current_messages > 0:
                queue.receive()  # Récupère les messages dans l'ordre dans lequel ils ont été envoyés
            queue.remove()
        except:
            pass
    sys.exit(0)

def print_queue_state(mqueues):
    for i, mq in enumerate(mqueues):
        print(f"Queue {i}:")
        try:
            while mq.current_messages > 0:
                msg, _ = mq.receive(block=False)
                vehicle_data = msg.decode('utf-8')
                print(f"Queue state: {vehicle_data}")
        except sysv_ipc.BusyError:
            print(f"  (Queue {i} est vide)")

def coordinator(priority_queue, light_array, mqueues, PID_FEUX, locks):
    try:
        while True:
            try:
                queues = []
                for i, mq in enumerate(mqueues):
                    with locks[i]:  # Verrouiller l'accès à la queue
                        try:
                            msg, _ = mq.receive(block=False)
                            queues.append(json.loads(msg.decode('utf-8')))
                            print_queue_state(mqueues)
                        except sysv_ipc.BusyError:
                            queues.append(None)

                for queue_index, queue_data in enumerate(queues):
                    if queue_data:
                        # Vérifier si le véhicule est prioritaire
                        if queue_data.get('priority', False):
                            # Si le véhicule est prioritaire, envoyer un signal
                            signal_map = {0: signal.SIGUSR1, 1: signal.SIGUSR2,
                                          2: signal.SIGTERM, 3: signal.SIGINT}
                            os.kill(PID_FEUX, signal_map.get(queue_index, signal.SIGINT))
                            # Vider la queue du véhicule prioritaire
                            while mqueues[queue_index].current_messages > 0:
                                mqueues[queue_index].receive()
                        else:
                            # Si le véhicule n'est pas prioritaire, vérifier les feux
                            with locks[queue_index]:  # Verrouiller l'accès à light_array
                                if light_array[queue_index] == 1:
                                    # Si le feu est vert, laisser passer
                                    print(f"Véhicule de la queue {queue_index} passe (feu vert)")
                                    while mqueues[queue_index].current_messages > 0:
                                        mqueues[queue_index].receive()  # Laisser passer les véhicules
                                else:
                                    # Si le feu est rouge, bloquer
                                    print(f"Véhicule de la queue {queue_index} bloqué (feu rouge)")
                                    # Le véhicule reste dans la queue

                print("État actuel des feux :", light_array)
                time.sleep(0.1)

            except (KeyboardInterrupt, SystemExit):
                cleanup_queues()
                break

    except sysv_ipc.Error as e:
        print(f"Erreur IPC: {e}")
        cleanup_queues()
