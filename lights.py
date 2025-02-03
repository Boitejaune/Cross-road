import time
import os
import signal


# Créer les signaux, un pour chaque route
# toutes les 5 secondes, le main màj les feux. Si signal du prioritaire, tant que le véhicule pas passé, laisse vert à la source du véhicule
# un dico pour état actuel des feux transmis à coordinateur via shared memory, puis lui à display via sockets
# pour véhicule prio : FIFO de la queue, on attend le prochain véhicule pour dire qu'il est parti

# Définition des différents handlers pour chaque signal
def handler_sigusr1(signum, frame):
    print("Signal SIGUSR1 reçu")
    # Ajoutez ici le code pour gérer le signal SIGUSR1

def handler_sigusr2(signum, frame):
    print("Signal SIGUSR2 reçu")
    # Ajoutez ici le code pour gérer le signal SIGUSR2

def handler_sigterm(signum, frame):
    print("Signal SIGTERM reçu")
    # Ajoutez ici le code pour gérer le signal SIGTERM

def handler_sigint(signum, frame):
    print("Signal SIGINT reçu")
    # Ajoutez ici le code pour gérer le signal SIGINT


"""

"""
# Processus de gestion des feux avec alternance simple
# Gérer les feux de circulation avec alternance toutes les 5 secondes, met à jour les états dans la queue (light_queue
def lights_process(light_queue):
    current_ns = "RED"
    current_we = "GREEN"
    dico_feu = {0 : "RED",
                1 : "GREEN",
                2 : "RED",
                3 : "GREEN"}

    while True:
        time.sleep(5)  # Intervalle de 5 secondes pour changer les feux
            # Alternance des feux
        
        # Enregistrement des handlers pour différents signaux
        signal.signal(signal.SIGUSR1, handler_sigusr1)
        signal.signal(signal.SIGUSR2, handler_sigusr2)
        signal.signal(signal.SIGTERM, handler_sigterm)
        signal.signal(signal.SIGINT, handler_sigint)

        if current_ns == "RED":
            current_ns = "GREEN"
            current_we = "RED"
        else:
            current_ns = "RED"
            current_we = "GREEN"
        # Mettre à jour les feux dans la queue
        print(current_ns,current_we)
        light_queue.put(current_ns)
        light_queue.put(current_we)


