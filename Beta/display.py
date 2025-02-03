"""
import multiprocessing
import tkinter as tk
import random

# Dimensions
WINDOW_SIZE = 500
ROAD_WIDTH = 100
CAR_SIZE = 20

# Couleurs des feux
COLORS = {"RED": "red", "GREEN": "green"}

# Positions des routes
ROADS = {
    0: [(WINDOW_SIZE//2 - ROAD_WIDTH//2, 0, WINDOW_SIZE//2 + ROAD_WIDTH//2, WINDOW_SIZE)],
    1: [(0, WINDOW_SIZE//2 - ROAD_WIDTH//2, WINDOW_SIZE, WINDOW_SIZE//2 + ROAD_WIDTH//2)]
}

class CrossroadSimulation:
    def __init__(self, root, priority_queue):
        self.root = root
        self.canvas = tk.Canvas(root, width=WINDOW_SIZE, height=WINDOW_SIZE, bg="white")
        self.canvas.pack()
        
        # Dessiner les routes
        for road in ROADS[0] + ROADS[1]:
            self.canvas.create_rectangle(road, fill="gray")
        
        # Feux de circulation pour chaque route
        self.lights = {
            0 : "RED",  # Feu pour la route Nord-Sud
            1 : "GREEN"  # Feu pour la route Ouest-Est
        }
        
        self.light_circles = {
            0: self.canvas.create_oval(220, 10, 280, 50, fill=COLORS[self.lights[0]]),
            1: self.canvas.create_oval(10, 220, 50, 280, fill=COLORS[self.lights[1]])
        }
        
        self.cars = []  # Liste des voitures normales
        # self.priority_cars = []  # Liste des véhicules prioritaires (désactivé temporairement)
        self.priority_queue = priority_queue  # Passer la queue de priorité
        
        # Lancer la mise à jour
        self.update_simulation()

    def update_simulation(self):
        # Mettre à jour les feux de circulation
        self.canvas.itemconfig(self.light_circles[0], fill=COLORS[self.lights[0]])
        self.canvas.itemconfig(self.light_circles[1], fill=COLORS[self.lights[1]])
        
        
        # Ajouter une nouvelle voiture normale
        if random.random() < 0.3:
            direction = random.choice([0, 1])
            if direction == 0:
                x, y = WINDOW_SIZE//2 - 10, 0
                dx, dy = 0, 5
            else:
                x, y = 0, WINDOW_SIZE//2 - 10
                dx, dy = 5, 0
                
            # Déterminer si la voiture est prioritaire (exemple: 10% des voitures)
            # is_priority = random.random() < 0.1  # Désactivé momentanément
            is_priority = False  # Tous les véhicules sont non prioritaires pour l'instant
            car = self.canvas.create_rectangle(x, y, x + CAR_SIZE, y + CAR_SIZE, fill="blue")
            
            # Ajout des coordonnées dx, dy au dictionnaire
            car_info = {"car": car, "direction": direction, "priority": is_priority, "dx": dx, "dy": dy}
            # if is_priority:
            #     self.priority_cars.append(car_info)
            #     self.priority_queue.put(car_info)  # Ajouter à la queue des priorités
            # else:
            self.cars.append(car_info)
        
        # Déplacer les voitures
        for car_info in self.cars:  # Plus besoin de gérer les priorités ici
            car = car_info["car"]
            direction = car_info["direction"]
            dx, dy = car_info["dx"], car_info["dy"]
            
            # Si la direction est rouge, la voiture ne peut pas avancer
            if direction == 0 and self.lights[0] == "RED":
                continue
            if direction == 1 and self.lights[1] == "RED":
                continue
                
            # Déplacer la voiture
            self.canvas.move(car, dx, dy)
            
            # Supprimer les voitures qui sortent de l'écran
            x1, y1, x2, y2 = self.canvas.coords(car)
            if x1 > WINDOW_SIZE or y1 > WINDOW_SIZE:
                self.canvas.delete(car)
                self.cars = [c for c in self.cars if c["car"] != car]  # Nettoyer la liste
        
        # Mettre à jour la simulation toutes les 100ms
        self.root.after(100, self.update_simulation)

# Lancer l'interface graphique
def run_gui(priority_queue):
    root = tk.Tk()
    app = CrossroadSimulation(root, priority_queue)
    root.mainloop()

"""
import tkinter as tk
import socket
import threading

WINDOW_SIZE = 500
ROAD_WIDTH = 100
CAR_SIZE = 20
COLORS = {"RED": "red", "GREEN": "green"}

class CrossroadSimulation:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=WINDOW_SIZE, height=WINDOW_SIZE, bg="white")
        self.canvas.pack()

        self.lights = {0: "RED", 1: "GREEN"}  # États initiaux
        self.cars = []

        # Serveurs sockets
        self.car_server = threading.Thread(target=self.receive_cars)
        self.car_server.start()

        self.lights_server = threading.Thread(target=self.receive_lights)
        self.lights_server.start()

        self.update_simulation()

    def receive_cars(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("localhost", 5000))
        sock.listen()

        while True:
            conn, _ = sock.accept()
            data = conn.recv(1024).decode().strip()
            if data:
                car_info = eval(data)
                self.add_car(car_info)

    def receive_lights(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("localhost", 5001))
        sock.listen()

        while True:
            conn, _ = sock.accept()
            data = conn.recv(1024).decode().strip()
            if data:
                ns, we = data.split()
                self.lights["NS"], self.lights["WE"] = ns, we

    def add_car(self, car_info):
        direction = car_info["direction"]
        x, y = (WINDOW_SIZE // 2 - 10, 0) if direction == "NS" else (0, WINDOW_SIZE // 2 - 10)
        dx, dy = (0, 5) if direction == "NS" else (5, 0)
        
        car = self.canvas.create_rectangle(x, y, x + CAR_SIZE, y + CAR_SIZE, fill="blue")
        self.cars.append({"car": car, "dx": dx, "dy": dy})

    def update_simulation(self):
        for car_info in self.cars:
            car = car_info["car"]
            dx, dy = car_info["dx"], car_info["dy"]
            self.canvas.move(car, dx, dy)

            # Supprimer les voitures hors écran
            x1, y1, x2, y2 = self.canvas.coords(car)
            if x1 > WINDOW_SIZE or y1 > WINDOW_SIZE:
                self.canvas.delete(car)
                self.cars.remove(car_info)

        self.root.after(50, self.update_simulation)  # Mise à jour rapide

def run_gui():
    root = tk.Tk()
    app = CrossroadSimulation(root)
    root.mainloop()

