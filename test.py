import tkinter as tk
import random
import time
import multiprocessing

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

# Shared resources
def init_shared_resources():
    manager = multiprocessing.Manager()
    light_state = manager.dict({"NS": "RED", "WE": "GREEN"})  # Feu initial (NS -> RED, WE -> GREEN)
    
    # Liste des voitures sur chaque route
    cars_ns = manager.list()  # Voitures sur la route Nord-Sud
    cars_we = manager.list()  # Voitures sur la route Ouest-Est
    
    return light_state, cars_ns, cars_we

# Définir une voiture avec sa direction et son mouvement
def create_car(direction, priority=False):
    # Position initiale
    x, y = 0, 0
    
    # Créer la voiture sous forme d'un rectangle
    car = {
        "direction": direction,
        "priority": priority,
        "position": (x, y),
        "movement": "straight",  # Mouvement par défaut
        "car": None  # Référence pour l'objet graphique
    }
    return car

# Classe pour l'application de simulation de croisement
class CrossroadSimulation:
    def __init__(self, root, light_state, cars_ns, cars_we):
        self.root = root
        self.canvas = tk.Canvas(root, width=WINDOW_SIZE, height=WINDOW_SIZE, bg="white")
        self.canvas.pack()
        
        # Dessiner les routes
        for road in ROADS["NS"] + ROADS["WE"]:
            self.canvas.create_rectangle(road, fill="gray")
        
        # Feux de circulation pour chaque route
        self.light_circles = {
            "NS": self.canvas.create_oval(220, 10, 280, 50, fill=COLORS[light_state["NS"]]),
            "WE": self.canvas.create_oval(10, 220, 50, 280, fill=COLORS[light_state["WE"]])
        }
        
        self.light_state = light_state
        self.cars_ns = cars_ns  # Liste des voitures sur la route NS
        self.cars_we = cars_we  # Liste des voitures sur la route WE
        
        # Créer des objets graphiques pour chaque voiture
        for car_info in self.cars_ns + self.cars_we:
            car_info["car"] = self.canvas.create_rectangle(
                car_info["position"][0], car_info["position"][1], 
                car_info["position"][0] + CAR_SIZE, car_info["position"][1] + CAR_SIZE, 
                fill="blue"
            )
        
        # Lancer la mise à jour
        self.update_simulation()

    def update_simulation(self):
        # Mettre à jour les feux de circulation
        self.canvas.itemconfig(self.light_circles["NS"], fill=COLORS[self.light_state["NS"]])
        self.canvas.itemconfig(self.light_circles["WE"], fill=COLORS[self.light_state["WE"]])
        
        # Déplacer les voitures
        for car_info in list(self.cars_ns) + list(self.cars_we):  # Convertir en liste classique
            direction = car_info["direction"]
            
            # Si le feu est rouge, la voiture ne peut pas avancer
            if direction == "NS" and self.light_state["NS"] == "RED":
                continue
            if direction == "WE" and self.light_state["WE"] == "RED":
                continue
            
            # Déplacer la voiture
            x, y = car_info["position"]
            if car_info["movement"] == "straight":
                car_info["position"] = (x + 5, y + 5)  # Exemple de déplacement simple
                
            # Mettre à jour l'affichage de la voiture
            self.canvas.coords(car_info["car"], x, y, x + CAR_SIZE, y + CAR_SIZE)
        
        # Mettre à jour la simulation toutes les 100ms
        self.root.after(100, self.update_simulation)



# Génération de trafic normal
def normal_traffic_gen(cars_ns, cars_we):
    while True:
        time.sleep(random.uniform(0.5, 2))  # Génère des voitures à des intervalles aléatoires
        direction = random.choice(["NS", "WE"])
        car = create_car(direction)
        
        # Ajouter la voiture à la liste appropriée
        if direction == "NS":
            cars_ns.append(car)
        else:
            cars_we.append(car)

# Processus de gestion des feux avec alternance simple
def lights_process(light_state):
    while True:
        time.sleep(5)  # Intervalle pour alterner les feux
        # Alterner les feux
        if light_state["NS"] == "RED":
            light_state["NS"] = "GREEN"
            light_state["WE"] = "RED"
        else:
            light_state["NS"] = "RED"
            light_state["WE"] = "GREEN"

# Processus de coordination des véhicules
def coordinator(cars_ns, cars_we, light_state):
    while True:
        time.sleep(0.1)  # Mise à jour à chaque intervalle de temps
        
        # Gérer les voitures sur les routes Nord-Sud et Ouest-Est
        for car in list(cars_ns) + list(cars_we):  # Convertir en liste classique
            direction = car["direction"]
            
            # Vérifier l'état du feu pour la direction de la voiture
            if direction == "NS" and light_state["NS"] == "RED":
                continue  # Si le feu est rouge, la voiture ne peut pas avancer
            if direction == "WE" and light_state["WE"] == "RED":
                continue  # Si le feu est rouge, la voiture ne peut pas avancer
            
            # Logique pour déplacer la voiture
            if car["movement"] == "straight":
                # Déplacement tout droit (simplement exemple)
                car["position"] = (car["position"][0] + 5, car["position"][1] + 5)  # Exemple de mouvement simple

# Lancer l'interface graphique
def run_gui(light_state, cars_ns, cars_we):
    root = tk.Tk()
    app = CrossroadSimulation(root, light_state, cars_ns, cars_we)
    root.mainloop()

if __name__ == "__main__":
    # Création des queues pour la communication entre les processus
    light_state, cars_ns, cars_we = init_shared_resources()

    # Démarrer les processus
    p_lights = multiprocessing.Process(target=lights_process, args=(light_state,))
    p_normal_traffic = multiprocessing.Process(target=normal_traffic_gen, args=(cars_ns, cars_we))
    p_coordinator = multiprocessing.Process(target=coordinator, args=(cars_ns, cars_we, light_state))
    
    p_lights.start()
    p_normal_traffic.start()
    p_coordinator.start()
    
    # Lancer l'interface graphique
    run_gui(light_state, cars_ns, cars_we)
    
    # Terminer les processus à la fin
    p_lights.terminate()
    p_normal_traffic.terminate()
    p_coordinator.terminate()
