import socket
import time

def send_to_display(message):
    """Envoie un message à display via socket."""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("localhost", 12345))
        client.send(message.encode())
        client.close()
    except ConnectionRefusedError:
        print("[ERREUR] Impossible de contacter Display")

if __name__ == "__main__":
    time.sleep(2)  # Attendre que display soit lancé

    # Phase 1 : Nord et Sud passent au vert
    send_to_display("4,1,0,1,0")  # Feux : Nord & Sud verts, Est & Ouest rouges
    time.sleep(1)
    send_to_display("0,1,False")  # Nord vers Est
    send_to_display("2,3,True")   # Sud vers Ouest, Prioritaire
    time.sleep(1)
    send_to_display("0,3,False")  # Nord vers Ouest
    send_to_display("2,1,False")  # Sud vers Est
    time.sleep(3)

    # Phase 2 : Est et Ouest passent au vert
    send_to_display("4,0,1,0,1")  # Feux : Est & Ouest verts, Nord & Sud rouges
    time.sleep(1)
    send_to_display("1,2,False")  # Est vers Sud
    send_to_display("3,0,True")   # Ouest vers Nord, Prioritaire
    time.sleep(1)
    send_to_display("1,0,False")  # Est vers Nord
    send_to_display("3,2,False")  # Ouest vers Sud
    time.sleep(3)

    # Phase 3 : Tous les feux au rouge (pause de sécurité)
    send_to_display("4,0,0,0,0")
    time.sleep(2)

    # Phase 4 : Alternance rapide pour urgence
    for i in range(3):
        send_to_display("4,1,0,1,0")  # Nord et Sud verts
        send_to_display("0,1,True")   # Nord vers Est, Prioritaire
        time.sleep(0.5)
        send_to_display("4,0,1,0,1")  # Est et Ouest verts
        send_to_display("1,2,True")   # Est vers Sud, Prioritaire
        time.sleep(0.5)

    # Phase 5 : Mélange de direction
    send_to_display("4,1,1,1,1")  # Tous les feux verts
    send_to_display("0,2,False")  # Nord vers Sud
    send_to_display("1,3,False")  # Est vers Ouest
    send_to_display("2,0,False")  # Sud vers Nord
    send_to_display("3,1,False")  # Ouest vers Est
    time.sleep(3)

    # Retour à la normale
    send_to_display("4,1,0,1,0")  # Nord & Sud verts
    send_to_display("0,1,False")  # Nord vers Est
    send_to_display("2,3,False")  # Sud vers Ouest
    time.sleep(3)

    send_to_display("4,0,1,0,1")  # Est & Ouest verts
    send_to_display("1,0,False")  # Est vers Nord
    send_to_display("3,2,False")  # Ouest vers Sud
    time.sleep(3)


