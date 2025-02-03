import time
import signal
import functools
import multiprocessing
# Définition des différents handlers pour chaque signal
def handler_sigusr1(signum, frame, light,queue_0,priority_queue):
    print("Signal SIGUSR1 reçu")
    light[0] = "GREEN"
    light[1], light[2], light[3] = "RED"
    while (queue_0 and queue_0[0] == False):
        time.sleep(0.1)
    priority_queue.pop(0)

def handler_sigusr2(signum, frame, light,queue_1,priority_queue):
    print("Signal SIGUSR2 reçu")
    light[1] = "GREEN"
    light[0], light[2], light[3] = "RED"
    while (queue_1 and queue_1[0] == False):
        time.sleep(0.1)
    priority_queue.pop(0)

def handler_sigterm(signum, frame, light,queue_2,priority_queue):
    print("Signal SIGTERM reçu")
    light[2] = "GREEN"
    light[1], light[0], light[3] = "RED"
    while (queue_2 and queue_2[0] == False):
        time.sleep(0.1)
    priority_queue.pop(0)

def handler_sigint(signum, frame, light,queue_3,priority_queue):
    print("Signal SIGINT reçu")
    light[3] = "GREEN"
    light[1], light[2], light[0] = "RED"
    while (queue_3 and queue_3[0] == False):
        time.sleep(0.1)
    priority_queue.pop(0)



# Processus de gestion des feux avec alternance simple
# Gérer les feux de circulation avec alternance toutes les 5 secondes, met à jour les états dans la queue (light_queue
def lights_process(queue_0, queue_1, queue_2, queue_3,light,priority_queue):
    while True:

        # Enregistrement des handlers pour différents signaux
        signal.signal(signal.SIGUSR1, functools.partial(handler_sigusr1, light,queue_0))
        signal.signal(signal.SIGUSR2, functools.partial(handler_sigusr2, light,queue_1))
        signal.signal(signal.SIGTERM, functools.partial(handler_sigterm, light,queue_2))
        signal.signal(signal.SIGINT, handler_sigint, light,queue_3)

        time.sleep(5)  # Intervalle de 5 secondes pour changer les feux
            # Alternance des feux

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
        # Mettre à jour les feux dans la queue
        print(light)
