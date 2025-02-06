# récupère chaque queue de route, PID feux pour les signaux, shared memory array lights
# pour chaque queue, vérif si il y a des véhicules
    # oui : véhicule prio ?
        # oui : envoie un signal à lights
        # non : si feux vert de la shared memory, de la source = n° queue, alors passe
                # sinon bloque


import os
import signal
import time
import sysv_ipc
import json
import socket
import sys

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



def send_to_display(message):
    """Envoie un message à display via socket."""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("localhost", 12346))
        client.send(message.encode())
        client.close()
    except ConnectionRefusedError:
        print("[ERREUR] Impossible de contacter Display")

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

                # Envoie de l'état des feux de circulation à l'affichage
                a_envoyer_display_feux = "4," + str(light_array[0]) + "," + str(light_array[1]) + "," + str(light_array[2]) + "," + str(light_array[3])
                send_to_display(a_envoyer_display_feux)
                print(f"Etat des feux : {a_envoyer_display_feux}")


                for queue_index, queue_data in enumerate(queues):
                    if queue_data:
                        # Vérifier si le véhicule est prioritaire
                        # print(f"queue_data.get priority : {queue_data['priority']}")
                        if str(queue_data['priority']) == "True":
                            # Si le véhicule est prioritaire, envoyer un signal
                            signal_map = {0: signal.SIGUSR1, 1: signal.SIGUSR2,
                                          2: signal.SIGTERM, 3: signal.SIGINT}
                            os.kill(PID_FEUX, signal_map.get(queue_index, signal.SIGINT))
                            # Envoie une voiture à l'affichage (format: origine, direction, priorité)
                            # Affichage des données du véhicule avec l'indice de la queue
                            # print(f"queue index : {queue_index}, queue direction : {queue_data.get('direction')}, prio : {queue_data.get('priority')}")
                            a_envoyer_display = str(queue_index) + "," + str(queue_data['direction']) + "," + str(queue_data['priority'])
                            send_to_display(a_envoyer_display)
                            # Vider la queue du véhicule prioritaire
                            while mqueues[queue_index].current_messages > 0:
                                mqueues[queue_index].receive()

                        else:
                            # Si le véhicule n'est pas prioritaire, vérifier les feux
                            with locks[queue_index]:  # Verrouiller l'accès à light_array
                                if str(light_array[queue_index]) == "GREEN":
                                    # Si le feu est vert, laisser passer
                                    print(f"Véhicule de la queue {queue_index} passe (feu vert)")
                                    
                                    # Affichage des données du véhicule avec l'indice de la queue
                                    # print(f"queue index : {queue_index}, queue direction : {queue_data.get('direction')}, prio : {queue_data.get('priority')}")
                                    a_envoyer_display = str(queue_index) + "," + str(queue_data['direction']) + "," + str(queue_data['priority'])
                                    send_to_display(a_envoyer_display)
                                    while mqueues[queue_index].current_messages > 0:
                                        mqueues[queue_index].receive()  # Laisser passer les véhicules
                                else:
                                    # Si le feu est rouge, bloquer
                                    print(f"Véhicule de la queue {queue_index} bloqué (feu rouge)")
                                    # Le véhicule reste dans la queue

                #print("État actuel des feux :", light_array)

                time.sleep(0.1)

            except (KeyboardInterrupt, SystemExit):
                cleanup_queues()
                break

    except sysv_ipc.Error as e:
        print(f"Erreur IPC: {e}")
        cleanup_queues()
