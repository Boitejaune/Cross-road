import tkinter as tk
import threading
import time
import random

WINDOW_SIZE = 500
ROAD_WIDTH = 100
CAR_SIZE = 20
COLORS = {"RED": "red", "GREEN": "green", "NORMAL": "blue"}

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
    def __init__(self, root, queue_0, queue_1, queue_2, queue_3):
        self.root = root
        self.canvas = tk.Canvas(root, width=WINDOW_SIZE, height=WINDOW_SIZE, bg="white")
        self.canvas.pack()

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
        self.queues = {0: queue_0, 1: queue_1, 2: queue_2, 3: queue_3}

        # Démarrer le thread d'écoute des données
        self.running = True
        self.update_thread = threading.Thread(target=self.listen_for_updates)
        self.update_thread.start()

    def listen_for_updates(self):
        """Simule la réception des données des sockets et met à jour les voitures."""
        while self.running:
            for route, queue in self.queues.items():
                if not queue.empty():
                    data = queue.get()  # Récupérer les infos sous forme (destination, priorité)
                    self.add_voiture(route, data[0], data[1])
            time.sleep(0.5)  # Met à jour toutes les 500ms

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
    time.sleep(10)

    # Fermer proprement
    p_display.terminate()
