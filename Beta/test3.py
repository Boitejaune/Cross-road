import tkinter as tk
import random
import time
import multiprocessing
import sysv_ipc
import socket



# Dimensions
WINDOW_SIZE = 500
ROAD_WIDTH = 100
CAR_SIZE = 20

# Couleurs des feux
COLORS = {"RED": "red", "GREEN": "green"}

# Positions des routes
ROADS = {
    "NS": [(WINDOW_SIZE//2 - ROAD_WIDTH//2, 0, WINDOW_SIZE//2 + ROAD_WIDTH//2, WINDOW_SIZE)],
    "WE": [(0, WINDOW_SIZE//2 - ROAD_WIDTH//2, WINDOW_SIZE, WINDOW_SIZE//2 + ROAD_WIDTH//2)]
}

class CrossroadSimulation:
    def __init__(self, root, priority_queue):
        self.root = root
        self.canvas = tk.Canvas(root, width=WINDOW_SIZE, height=WINDOW_SIZE, bg="white")
        self.canvas.pack()
        
        # Dessiner les routes
        for road in ROADS["NS"] + ROADS["WE"]:
            self.canvas.create_rectangle(road, fill="gray")
        
        # Feux de circulation pour chaque route
        self.lights = {
            "NS": "RED",  # Feu pour la route Nord-Sud
            "WE": "GREEN"  # Feu pour la route Ouest-Est
        }
        
        self.light_circles = {
            "NS": self.canvas.create_oval(220, 10, 280, 50, fill=COLORS[self.lights["NS"]]),
            "WE": self.canvas.create_oval(10, 220, 50, 280, fill=COLORS[self.lights["WE"]])
        }
        
        self.cars = []  # Liste des voitures normales
        # self.priority_cars = []  # Liste des véhicules prioritaires (désactivé temporairement)
        self.priority_queue = priority_queue  # Passer la queue de priorité
        
        # Lancer la mise à jour
        self.update_simulation()

    def update_simulation(self):
        # Mettre à jour les feux de circulation
        self.canvas.itemconfig(self.light_circles["NS"], fill=COLORS[self.lights["NS"]])
        self.canvas.itemconfig(self.light_circles["WE"], fill=COLORS[self.lights["WE"]])
        
        # Ajouter une nouvelle voiture normale
        if random.random() < 0.3:
            direction = random.choice(["NS", "WE"])
            if direction == "NS":
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
            if direction == "NS" and self.lights["NS"] == "RED":
                continue
            if direction == "WE" and self.lights["WE"] == "RED":
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

# Génération de trafic normal
# Générer des voitures à intervalles aléatoires et les ajouter à une queue (car_queue)
def normal_traffic_gen(car_queue):
    while True:
        time.sleep(random.uniform(0.5, 2))  # Génère des voitures à des intervalles aléatoires
        direction = random.choice(["NS", "WE"])
        car = {"direction": direction, "priority": False}
        car_queue.put(car)

# Processus de gestion des feux avec alternance simple
# Gérer les feux de circulation avec alternance toutes les 5 secondes, met à jour les états dans la queue (light_queue
def lights_process(light_queue):
    current_ns = "RED"
    current_we = "GREEN"
    
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
        light_queue.put(current_ns)
        light_queue.put(current_we)

# Processus de coordination des véhicules : Vérifie les feux avant de permettre aux voitures de circuler. Si le feu est vert pour la direction d'une voiture, elle peut avancer.
def coordinator(car_queue, priority_queue, light_queue):
    while True:
        time.sleep(0.1)
        
        # Gérer les véhicules en fonction des feux
        if not car_queue.empty():
            car_info = car_queue.get()
            direction = car_info["direction"]
            # Si le feu est vert pour la direction du véhicule, il peut passer
            if (direction == "NS" and light_queue.get() == "GREEN") or \
               (direction == "WE" and light_queue.get() == "GREEN"):
                # Logique pour faire avancer la voiture (ex. déplacer sur l'écran)
                pass  # On ajoutera la gestion de l'avancement plus tard

# Lancer l'interface graphique
def run_gui(priority_queue):
    root = tk.Tk()
    app = CrossroadSimulation(root, priority_queue)
    root.mainloop()

if __name__ == "__main__":
    # Création des queues pour la communication entre les processus
    car_queue = multiprocessing.Queue()  # Queue des véhicules normaux
    priority_queue = multiprocessing.Queue()  # Queue des véhicules prioritaires (désactivé)
    light_queue = multiprocessing.Queue()  # Queue des feux de circulation
    
    light_queue.put("GREEN")  # Initialiser les feux
    
    # Démarrer les processus
    p_lights = multiprocessing.Process(target=lights_process, args=(light_queue,))
    p_normal_traffic = multiprocessing.Process(target=normal_traffic_gen, args=(car_queue,))
    # p_priority_traffic = multiprocessing.Process(target=priority_traffic_gen, args=(priority_queue,))  # Désactivé
    p_coordinator = multiprocessing.Process(target=coordinator, args=(car_queue, priority_queue, light_queue))
    
    p_lights.start()
    p_normal_traffic.start()
    # p_priority_traffic.start()  # Désactivé
    p_coordinator.start()
    
    # Lancer l'interface graphique
    run_gui(priority_queue)
    
    # Terminer les processus à la fin
    p_lights.terminate()
    p_normal_traffic.terminate()
    # p_priority_traffic.terminate()  # Désactivé
    p_coordinator.terminate()


"""import tkinter as tk


WINDOW_SIZE = 500
ROAD_WIDTH = 100
CAR_SIZE = 20
COLORS = {"RED": "red", "GREEN": "green"}

# routes - msg queues et feuxù

class CrossroadSimulation:
    def __init__(self, root, queue0, queue1, queue2, queue3):
        self.root = root
        self.canvas = tk.Canvas(root, width=WINDOW_SIZE, height=WINDOW_SIZE, bg="white")
        self.canvas.pack()

        self.lights = {0: "RED", 1: "GREEN", 2: "RED", 3:"GREEN"}  # États initiaux
        self.cars = []

        self.lights_dessin_cercles = {
            0: self.canvas.create_oval(220, 10, 280, 50, fill=COLORS[self.lights["NS"]]),
            1: self.canvas.create_oval(220, 10, 280, 50, fill=COLORS[self.lights["NS"]]),
            2: self.canvas.create_oval(220, 10, 280, 50, fill=COLORS[self.lights["NS"]]),
            3: self.canvas.create_oval(220, 10, 280, 50, fill=COLORS[self.lights["NS"]])
        }

    
        # Serveurs sockets
        self.car_server = threading.Thread(target=self.receive_cars)
        self.car_server.start()

        self.lights_server = threading.Thread(target=self.receive_lights)
        self.lights_server.start()
        
        
        self.update_simulation()

    def reception_voitures(self):



    def update_simulation(self):
        # Mettre à jour les feux de circulation
        self.canvas.itemconfig(self.light_circles["N"], fill=COLORS[self.lights["NS"]])
        self.canvas.itemconfig(self.light_circles["W"], fill=COLORS[self.lights["WE"]])
        
            
        # Déplacer les voitures
        for car_info in self.cars:
            car = car_info["car"]
            direction = car_info["direction"]
            dx, dy = car_info["dx"], car_info["dy"]
            
            # Si la direction est rouge, la voiture ne peut pas avancer
            if direction == "NS" and self.lights["NS"] == "RED":
                continue
            if direction == "WE" and self.lights["WE"] == "RED":
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

        """