import time
import sysv_ipc
import os

# Processus de gestion des feux avec alternance simple
# Gérer les feux de circulation avec alternance toutes les 5 secondes, met à jour les états dans la queue (light_queue
def lights_process(light_queue):
    current_ns = "RED"
    current_we = "GREEN"
    PID_FEUX = os.getpid()
    print(f" lights {PID_FEUX}")

    key = 666
    mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
    mq.send(PID_FEUX)
    
    while True:
        time.sleep(5)  # Intervalle de 5 secondes pour changer les feux
            # Alternance des feux
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
