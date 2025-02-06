import tkinter as tk
import threading
import time
import random
import socket
from tkinter import PhotoImage

WINDOW_SIZE = 500
ROAD_WIDTH = 100
CAR_SIZE = 20
COLORS = {"RED": "red", "GREEN" : "green", "NORMAL": "blue"}

# Positions des routes
ROUTES = {
    "NordSud": [(WINDOW_SIZE//2 - ROAD_WIDTH//2, 0, WINDOW_SIZE//2 + ROAD_WIDTH//2, WINDOW_SIZE)],
    "EstOuest": [(0, WINDOW_SIZE//2 - ROAD_WIDTH//2, WINDOW_SIZE, WINDOW_SIZE//2 + ROAD_WIDTH//2)]
}

# Positions des feux de circulation
FEUX = {
    "Nord": (205, 180, 225, 200),  
    "Est": (305, 205, 325, 225),  
    "Sud": (275, 300, 295, 320),  
    "Ouest": (180, 275, 200, 295)   
}

# Positions initiales des voitures (bord droit de chaque tronçon)
START_POSITIONS = {
    0: (205, 50, 225, 70),   # Nord -> Sud
    1: (450, 205, 470, 225), # Est -> Ouest
    2: (275, 450, 295, 470), # Sud -> Nord
    3: (50, 275, 70, 295)    # Ouest -> Est
}

class CrossroadSimulation:
    def __init__(self, root):#, queue_0, queue_1, queue_2, queue_3):
        self.root = root

        

        self.canvas = tk.Canvas(root, width=WINDOW_SIZE, height=WINDOW_SIZE, bg="white")
        self.canvas.pack()

        """
        # Charger arrière-plan
        image = PhotoImage(file='fond.png', master=root)
        self.canvas.create_image(0, 0, image=image, anchor="nw")
        """
        
        # Dessiner les routes
        for road in ROUTES.values():
            for coords in road:
                self.canvas.create_rectangle(coords, fill="gray")

        # Dessiner les feux de circulation
        self.lights = {}
        for position, coords in FEUX.items():
            color = "RED" if position in ["Nord", "Sud"] else "GREEN"
            self.lights[position] = self.canvas.create_oval(coords, fill=COLORS[color])

        # Stockage des voitures affichées
        self.voitures = {}

        # Queues des voitures
        #self.queues = {0: queue_0, 1: queue_1, 2: queue_2, 3: queue_3}

        # Démarrer le serveur socket pour écouter Coordinator
        self.running = True
        self.server_thread = threading.Thread(target=self.start_socket_server)
        self.server_thread.start()

        self.root.after(100, self.move_voitures)


    def start_socket_server(self):
        """Démarre un serveur socket pour recevoir les données de Coordinator."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("localhost", 12346))  # Écoute sur le port 12345
        server.listen(5)
        print("[INFO] Serveur Display en écoute...")

        while self.running:
            client, addr = server.accept()
            print(f"[INFO] Connexion reçue de {addr}")
            client_thread = threading.Thread(target=self.handle_client, args=(client,))
            client_thread.start()

    def handle_client(self, client):
        """Gère la connexion socket avec Coordinator et traite les messages."""
        while self.running:
            try:
                data = client.recv(1024).decode()
                if not data:
                    break
                
                message = data.split(",")  # Ex : "0,1,False"
                header = int(message[0])

                if header in [0, 1, 2, 3]:  # Ajout d'une voiture
                    origin = header
                    destination = int(message[1])
                    is_priority = message[2] == "True"
                    self.root.after(0, self.add_voiture, origin, destination, is_priority)
                    print(f"[DEBUG] Ajout voiture : Origine={origin}, Destination={destination}, Prioritaire={is_priority}")


                elif header == 4:  # Mise à jour des feux
                    feu_nord = "GREEN" if message[1] == "GREEN" else "RED"
                    feu_est = "GREEN" if message[2] == "GREEN" else "RED"
                    feu_sud = "GREEN" if message[3] == "GREEN" else "RED"
                    feu_ouest = "GREEN" if message[4] == "GREEN" else "RED"

                    self.root.after(0, self.update_lights, feu_nord, feu_est, feu_sud, feu_ouest)

            except Exception as e:
                print(f"[ERREUR] Problème avec le client socket : {e}")
                break

        client.close()

    def update_lights(self, nord, est, sud, ouest):
        """Met à jour les feux de circulation sur le canevas."""
        self.canvas.itemconfig(self.lights["Nord"], fill=COLORS[nord])
        self.canvas.itemconfig(self.lights["Est"], fill=COLORS[est])
        self.canvas.itemconfig(self.lights["Sud"], fill=COLORS[sud])
        self.canvas.itemconfig(self.lights["Ouest"], fill=COLORS[ouest])

    def move_voitures(self):
        """Déplace les voitures et gère les virages correctement."""
        voitures_a_supprimer = []

        for car, (origin, destination) in list(self.voitures.items()):
            x1, y1, x2, y2 = self.canvas.coords(car)

            # Feux et positions de l'intersection
            feu_position = {0: 180, 1: 305, 2: 320, 3: 200}
            intersection_x, intersection_y = WINDOW_SIZE//2, WINDOW_SIZE//2

            # Vérifier la couleur du feu
            feu_ok = (
                (origin == 0 and self.canvas.itemcget(self.lights["Nord"], "fill") == COLORS["GREEN"]) or
                (origin == 1 and self.canvas.itemcget(self.lights["Est"], "fill") == COLORS["GREEN"]) or
                (origin == 2 and self.canvas.itemcget(self.lights["Sud"], "fill") == COLORS["GREEN"]) or
                (origin == 3 and self.canvas.itemcget(self.lights["Ouest"], "fill") == COLORS["GREEN"])
            )

            # Vérifier si la voiture a dépassé son feu (elle continue après l'intersection)
            passed_light = (
                (origin == 0 and y1 > feu_position[0]) or  # Nord → Sud
                (origin == 1 and x1 < feu_position[1]) or  # Est → Ouest
                (origin == 2 and y2 < feu_position[2]) or  # Sud → Nord
                (origin == 3 and x2 > feu_position[3])     # Ouest → Est
            )

            # Debugging
            print(f"Voiture {car} de {origin} vers {destination} | Feu OK: {feu_ok} | Dépassé: {passed_light}")

            # Si la voiture peut avancer
            if feu_ok or passed_light:
                dx, dy = 0, 0

                # Si la voiture n'est pas encore au centre, elle avance droit
                if (
                    (origin == 0 and y1 < intersection_y) or
                    (origin == 1 and x1 > intersection_x) or
                    (origin == 2 and y2 > intersection_y) or
                    (origin == 3 and x2 < intersection_x)
                ):
                    dx, dy = {0: (0, 5), 1: (-5, 0), 2: (0, -5), 3: (5, 0)}[origin]

                else:  # Elle est au centre et peut tourner si nécessaire
                    if (origin == 0 and destination == 1):  # Nord → Est (droite)
                        dx, dy = (5, 0)
                    elif (origin == 0 and destination == 3):  # Nord → Ouest (gauche)
                        dx, dy = (-5, 0)
                    elif (origin == 1 and destination == 2):  # Est → Sud (droite)
                        dx, dy = (0, 5)
                    elif (origin == 1 and destination == 0):  # Est → Nord (gauche)
                        dx, dy = (0, -5)
                    elif (origin == 2 and destination == 3):  # Sud → Ouest (droite)
                        dx, dy = (-5, 0)
                    elif (origin == 2 and destination == 1):  # Sud → Est (gauche)
                        dx, dy = (5, 0)
                    elif (origin == 3 and destination == 0):  # Ouest → Nord (droite)
                        dx, dy = (0, -5)
                    elif (origin == 3 and destination == 2):  # Ouest → Sud (gauche)
                        dx, dy = (0, 5)
                    else:  # Si elle va tout droit
                        dx, dy = {0: (0, 5), 1: (-5, 0), 2: (0, -5), 3: (5, 0)}[origin]

                # Déplacer la voiture
                self.canvas.move(car, dx, dy)

                # Supprimer la voiture si elle sort de l'écran
                if x1 < 0 or x2 > WINDOW_SIZE or y1 < 0 or y2 > WINDOW_SIZE:
                    voitures_a_supprimer.append(car)

        # Supprimer les voitures qui quittent l'écran
        for car in voitures_a_supprimer:
            self.canvas.delete(car)
            del self.voitures[car]

        # Planifier le prochain déplacement
        self.root.after(100, self.move_voitures)






    """
    def listen_for_updates(self):
        #Simule la réception des données des sockets et met à jour les voitures.
        while self.running:
            for route, queue in self.queues.items():
                if not queue.empty():
                    data = queue.get()  # Récupérer les infos sous forme (destination, priorité)
                    self.add_voiture(route, data[0], data[1])
            time.sleep(0.5)  # Met à jour toutes les 500ms
    """

    def add_voiture(self, origin, destination, is_priority):
        """Ajoute une voiture sur l'écran avec la couleur correspondante."""
        color = "RED" if is_priority else "NORMAL"
        if origin in START_POSITIONS:
            x1, y1, x2, y2 = START_POSITIONS[origin]
            car = self.canvas.create_rectangle(x1, y1, x2, y2, fill=COLORS[color])
            self.voitures[car] = (origin, destination)  # Sauvegarde de la destination pour futur mouvement

    def stop(self):
        """Arrête le thread proprement."""
        self.running = False
        self.update_thread.join()

def run_gui():
    root = tk.Tk()
    app = CrossroadSimulation(root)
    root.protocol("WM_DELETE_WINDOW", app.stop)
    root.mainloop()


"""
def run_gui(queue_0, queue_1, queue_2, queue_3):
    root = tk.Tk()
    app = CrossroadSimulation(root, queue_0, queue_1, queue_2, queue_3)
    root.protocol("WM_DELETE_WINDOW", app.stop)  # Assurer la fermeture propre
    root.mainloop()



if __name__ == "__main__":
    import multiprocessing
    import time

    # Création des queues pour tester
    queue_0 = multiprocessing.Queue()
    queue_1 = multiprocessing.Queue()
    queue_2 = multiprocessing.Queue()
    queue_3 = multiprocessing.Queue()

    # Lancer l'interface graphique dans un processus séparé
    p_display = multiprocessing.Process(target=run_gui, args=(queue_0, queue_1, queue_2, queue_3))
    p_display.start()

    # Simuler l'arrivée de voitures
    time.sleep(2)  # Attendre que la fenêtre s'affiche

    # Ajouter quelques voitures test (origin, destination, priorité)
    queue_0.put((1, False))  # Une voiture normale venant du Nord vers l'Est
    queue_1.put((2, False))   # Une voiture prioritaire venant de l'Est vers le Sud
    queue_2.put((3, False))  # Une voiture normale venant du Sud vers l'Ouest
    queue_3.put((0, True))   # Une voiture prioritaire venant de l'Ouest vers le Nord

    # Laisser tourner quelques secondes pour voir l'affichage
    time.sleep(100)

    # Fermer proprement
    p_display.terminate()
"""

if __name__ == "__main__":
    run_gui()
