import time
import signal
import functools
import sysv_ipc
import json

# Fonction pour réinitialiser le cycle des feux
def reset_light_cycle(light, lock):
    with lock:
        # Réinitialiser l'alternance des feux à leur état normal
        if light[0] == "GREEN":
            light[0] = "GREEN"
            light[1] = "RED"
            light[2] = "GREEN"
            light[3] = "RED"
        else:
            light[0] = "RED"
            light[1] = "GREEN"
            light[2] = "RED"
            light[3] = "GREEN"
    print("Les feux ont été réinitialisés à leur cycle normal.")

# Handler pour SIGUSR1
def handler_sigusr1(signum, frame, light, queue_0, priority_queue, lock):
    print("Signal SIGUSR1 reçu")
    
    with lock:  # Verrouiller l'accès au dictionnaire light
        light[0] = "GREEN"
        light[1], light[2], light[3] = "RED", "RED", "RED"

    while True:
        try:
            msg, _ = queue_0.receive(block=False)
            vehicle_data = json.loads(msg.decode('utf-8'))
            print(f"Message reçu : {vehicle_data}")
            if vehicle_data.get("priority"):
                print("Véhicule prioritaire détecté !")
                # Si véhicule prioritaire, traiter et enlever de la file d'attente
                priority_queue.get()
            else:
                print(f"Véhicule non prioritaire détecté : {vehicle_data}")
            break
        except sysv_ipc.BusyError:
            time.sleep(0.1)

    # Une fois le véhicule prioritaire passé, rétablir l'alternance
    reset_light_cycle(light, lock)

# Handler pour SIGUSR2
def handler_sigusr2(signum, frame, light, queue_1, priority_queue, lock):
    print("Signal SIGUSR2 reçu")
    
    with lock:
        light[1] = "GREEN"
        light[0], light[2], light[3] = "RED", "RED", "RED"

    while True:
        try:
            msg, _ = queue_1.receive(block=False)
            vehicle_data = json.loads(msg.decode('utf-8'))
            print(f"Message reçu : {vehicle_data}")
            if vehicle_data.get("priority"):
                print("Véhicule prioritaire détecté !")
                # Si véhicule prioritaire, traiter et enlever de la file d'attente
                priority_queue.get()
            else:
                print(f"Véhicule non prioritaire détecté : {vehicle_data}")
            break
        except sysv_ipc.BusyError:
            time.sleep(0.1)

    # Une fois le véhicule prioritaire passé, rétablir l'alternance
    reset_light_cycle(light, lock)

# Handler pour SIGTERM
def handler_sigterm(signum, frame, light, queue_2, priority_queue, lock):
    print("Signal SIGTERM reçu")
    
    with lock:
        light[2] = "GREEN"
        light[1], light[0], light[3] = "RED", "RED", "RED"

    while True:
        try:
            msg, _ = queue_2.receive(block=False)
            vehicle_data = json.loads(msg.decode('utf-8'))
            print(f"Message reçu : {vehicle_data}")
            if vehicle_data.get("priority"):
                print("Véhicule prioritaire détecté !")
                # Si véhicule prioritaire, traiter et enlever de la file d'attente
                priority_queue.get()
            else:
                print(f"Véhicule non prioritaire détecté : {vehicle_data}")
            break
        except sysv_ipc.BusyError:
            time.sleep(0.1)

    # Une fois le véhicule prioritaire passé, rétablir l'alternance
    reset_light_cycle(light, lock)

# Handler pour SIGINT
def handler_sigint(signum, frame, light, queue_3, priority_queue, lock):
    print("Signal SIGINT reçu")
    
    with lock:
        light[3] = "GREEN"
        light[1], light[2], light[0] = "RED", "RED", "RED"

    while True:
        try:
            msg, _ = queue_3.receive(block=False)
            vehicle_data = json.loads(msg.decode('utf-8'))
            print(f"Message reçu : {vehicle_data}")
            if vehicle_data.get("priority"):
                print("Véhicule prioritaire détecté !")
                # Si véhicule prioritaire, traiter et enlever de la file d'attente
                priority_queue.get()
            else:
                print(f"Véhicule non prioritaire détecté : {vehicle_data}")
            break
        except sysv_ipc.BusyError:
            time.sleep(0.1)

    # Une fois le véhicule prioritaire passé, rétablir l'alternance
    reset_light_cycle(light, lock)

# Fonction principale pour la gestion des feux
def lights_process(light, priority_queue, mqueues, lock):
    while True:
        # Assignation des gestionnaires de signaux
        signal.signal(signal.SIGUSR1, functools.partial(handler_sigusr1, light=light, queue_0=mqueues[0], priority_queue=priority_queue, lock=lock))
        signal.signal(signal.SIGUSR2, functools.partial(handler_sigusr2, light=light, queue_1=mqueues[1], priority_queue=priority_queue, lock=lock))
        signal.signal(signal.SIGTERM, functools.partial(handler_sigterm, light=light, queue_2=mqueues[2], priority_queue=priority_queue, lock=lock))
        signal.signal(signal.SIGINT, functools.partial(handler_sigint, light=light, queue_3=mqueues[3], priority_queue=priority_queue, lock=lock))

        time.sleep(5)

        with lock:  # Verrouiller l'accès à light ici
            # Alterner les feux entre les directions
            if light[0] == "RED":
                light[0] = "GREEN"
                light[2] = "GREEN"
                light[1] = "RED"
                light[3] = "RED"
            else:
                light[0] = "RED"
                light[2] = "RED"
                light[1] = "GREEN"
                light[3] = "GREEN"

        print("État des feux :", light)
