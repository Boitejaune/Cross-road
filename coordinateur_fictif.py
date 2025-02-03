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

    # Simuler l'envoi de voitures (origine, destination, priorité)
    send_to_display("0,1,False")  # Nord vers Est, voiture normale
    send_to_display("1,2,True")   # Est vers Sud, voiture prioritaire
    send_to_display("2,3,False")  # Sud vers Ouest, voiture normale
    send_to_display("3,0,True")   # Ouest vers Nord, voiture prioritaire

    # Simuler un changement des feux
    time.sleep(3)
    send_to_display("4,1,0,1,0")  # Nord et Sud passent au vert, Est et Ouest au rouge
