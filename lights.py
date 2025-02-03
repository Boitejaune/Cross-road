import time
import os
import signal
import functools

# Définition des différents handlers pour chaque signal
def handler_sigusr1(signum, frame, dico_feux,car,light_queue):
    print("Signal SIGUSR1 reçu")
    while(car['Priority'] == True):
        dico_feux[0] = "GREEN"
        dico_feux[1], dico_feux[2], dico_feux[3] = "RED"
        light_queue.put(dico_feux[0])
        light_queue.put(dico_feux[1])
        light_queue.put(dico_feux[2])
        light_queue.put(dico_feux[3])

def handler_sigusr2(signum, frame, dico_feux,car,light_queue):
    print("Signal SIGUSR2 reçu")
    prio = True
    while(prio == True):
        dico_feux[1] = "GREEN"
        dico_feux[0], dico_feux[2], dico_feux[3] = "RED"
        if car['Priority'] == False:
            prio == False
        light_queue.put(dico_feux[0])
        light_queue.put(dico_feux[1])
        light_queue.put(dico_feux[2])
        light_queue.put(dico_feux[3])

def handler_sigterm(signum, frame, dico_feux,car,light_queue):
    print("Signal SIGTERM reçu")
    prio = True
    while(prio == True):
        dico_feux[2] = "GREEN"
        dico_feux[1], dico_feux[0], dico_feux[3] = "RED"
        if car['Priority'] == False:
            prio == False
        light_queue.put(dico_feux[0])
        light_queue.put(dico_feux[1])
        light_queue.put(dico_feux[2])
        light_queue.put(dico_feux[3])

def handler_sigint(signum, frame, dico_feux,car,light_queue):
    print("Signal SIGINT reçu")
    prio = True
    while(prio == True):
        dico_feux[2] = "GREEN"
        dico_feux[1], dico_feux[2], dico_feux[0] = "RED"
        if car['Priority'] == False:
            prio == False
        light_queue.put(dico_feux[0])
        light_queue.put(dico_feux[1])
        light_queue.put(dico_feux[2])
        light_queue.put(dico_feux[3])


"""

"""
# Processus de gestion des feux avec alternance simple
# Gérer les feux de circulation avec alternance toutes les 5 secondes, met à jour les états dans la queue (light_queue
def lights_process(light_queue):
    dico_feux = {0 : "RED",
                1 : "GREEN",
                2 : "RED",
                3 : "GREEN"}

    while True:
        time.sleep(5)  # Intervalle de 5 secondes pour changer les feux
            # Alternance des feux
        
        # Enregistrement des handlers pour différents signaux
        signal.signal(signal.SIGUSR1, functools.partial(handler_sigusr1, dico_feux,car,light_queue))
        signal.signal(signal.SIGUSR2, functools.partial(handler_sigusr2, dico_feux,car,light_queue))
        signal.signal(signal.SIGTERM, functools.partial(handler_sigterm, dico_feux,car,light_queue))
        signal.signal(signal.SIGINT, handler_sigint)

        if dico_feux[0] == "RED":
            dico_feux[0], dico_feux[2] = "GREEN"
            dico_feux[1], dico_feux[3] = "RED"
        else:
            dico_feux[0], dico_feux[2] = "RED"
            dico_feux[1], dico_feux[3] = "GREEN"
        # Mettre à jour les feux dans la queue
        print(dico_feux)
        light_queue.put(dico_feux[0])
        light_queue.put(dico_feux[1])
        light_queue.put(dico_feux[2])
        light_queue.put(dico_feux[3])


