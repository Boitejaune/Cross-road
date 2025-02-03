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
    0: [(WINDOW_SIZE//2 - ROAD_WIDTH//2, 0, WINDOW_SIZE//2 + ROAD_WIDTH//2, WINDOW_SIZE)],
    1: [(0, WINDOW_SIZE//2 - ROAD_WIDTH//2, WINDOW_SIZE, WINDOW_SIZE//2 + ROAD_WIDTH//2)]
}

# Shared resources
def init_shared_resources():
    manager = multiprocessing.Manager()
    light_state = manager.dict({0: "RED", 1: "GREEN"})  # Feu initial (NS -> RED, WE -> GREEN)
    
    # Liste des voitures sur chaque route
    cars_ns = manager.list()  # Voitures sur la route Nord-Sud
    cars_we = manager.list()  # Voitures sur la route Ouest-Est
    return light_state, cars_ns, cars_we

# Définir une voiture avec sa direction et son mouvement
def create_car(direction, priority=False):
    # Position initiale
    x, y = 0, 0
    if direction == 0:
        x = random.randint(WINDOW_SIZE//4, 3*WINDOW_SIZE//4)
        y = -CAR_SIZE  # Arriver depuis le haut
    elif direction == 1:
        x = -CAR_SIZE  # Arriver depuis la gauche
        y = random.randint(WINDOW_SIZE//4, 3*WINDOW_SIZE//4)
    
    # Créer la voiture sous forme d'un dictionnaire
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
    def __init__(self, root, light_state, cars_ns, cars_we, car_queue, stop_event):
        self.root = root
        self.canvas = tk.Canvas(root, width=WINDOW_SIZE, height=WINDOW_SIZE, bg="white")
        self.canvas.pack()
        
        # Dessiner les routes
        for road in ROADS[0] + ROADS[1]:
            self.canvas.create_rectangle(road, fill="gray")
        
        # Feux de circulation pour chaque route
        self.light_circles = {
            0: self.canvas.create_oval(220, 10, 280, 50, fill=COLORS[light_state[0]]),
            1: self.canvas.create_oval(10, 220, 50, 280, fill=COLORS[light_state[1]])
        }
        
        self.light_state = light_state
        self.cars_ns = cars_ns  # Liste des voitures sur la route NS
        self.cars_we = cars_we  # Liste des voitures sur la route WE
        self.car_queue = car_queue  # Queue pour recevoir les nouvelles voitures
        self.stop_event = stop_event  # Event pour arrêter la simulation
        
        self.update_simulation()

    def update_simulation(self):
        if self.stop_event.is_set():
            self.root.quit()  # Quitter la boucle principale si l'événement est activé
        
        # Mettre à jour les feux de circulation
        self.canvas.itemconfig(self.light_circles[0], fill=COLORS[self.light_state[0]])
        self.canvas.itemconfig(self.light_circles[1], fill=COLORS[self.light_state[1]])
        
        # Récupérer les nouvelles voitures depuis la queue
        while not self.car_queue.empty():
            new_car = self.car_queue.get()
            print(f"New car created: {new_car}")  # Vérification de la création de la voiture
            if new_car["direction"] == "0":
                self.cars_ns.append(new_car)
            else:
                self.cars_we.append(new_car)
            
            # Créer l'objet graphique pour la voiture
            new_car["car"] = self.canvas.create_rectangle(
                new_car["position"][0], new_car["position"][1], 
                new_car["position"][0] + CAR_SIZE, new_car["position"][1] + CAR_SIZE, 
                fill="blue"
            )
        
        # Déplacer les voitures
        for car_info in list(self.cars_ns) + list(self.cars_we):  # Convertir en liste classique
            direction = car_info["direction"]
            
            # Si le feu est rouge, la voiture ne peut pas avancer
            if direction == 0 and self.light_state[0] == "RED":
                continue
            if direction == 1 and self.light_state[1] == "RED":
                continue
            
            # Déplacer la voiture
            x, y = car_info["position"]
            if car_info["movement"] == "straight":
                if direction == 0:
                    car_info["position"] = (x, y + 5)  # Déplacer vers le bas
                elif direction == 1:
                    car_info["position"] = (x + 5, y)  # Déplacer vers la droite
                
            # Mettre à jour l'affichage de la voiture
            print(f"Moving car: {car_info}")  # Vérification du mouvement des voitures
            self.canvas.coords(car_info["car"], x, y, x + CAR_SIZE, y + CAR_SIZE)
        
        # Mettre à jour la simulation toutes les 100ms
        self.root.after(100, self.update_simulation)

# Génération de trafic normal
def normal_traffic_gen(car_queue, stop_event):
    while not stop_event.is_set():
        time.sleep(random.uniform(0.5, 2))  # Génère des voitures à des intervalles aléatoires
        direction = random.choice([0, 1])
        car = create_car(direction)
        # Ajouter la voiture à la queue
        print(f"Car added to queue: {car}")  # Vérification avant ajout à la queue
        car_queue.put(car)

# Processus de gestion des feux avec alternance simple
def lights_process(light_state, stop_event):
    while not stop_event.is_set():
        time.sleep(5)  # Intervalle pour alterner les feux
        # Alterner les feux
        if light_state[0] == "RED":
            light_state[0] = "GREEN"
            light_state[1] = "RED"
        else:
            light_state[0] = "RED"
            light_state[1] = "GREEN"
        print(f"Lights changed: {light_state}")

def main():
    # Initialisation des ressources partagées
    light_state, cars_ns, cars_we = init_shared_resources()
    car_queue = multiprocessing.Queue()
    stop_event = multiprocessing.Event()
    
    # Création des processus
    light_process = multiprocessing.Process(target=lights_process, args=(light_state, stop_event))
    traffic_process = multiprocessing.Process(target=normal_traffic_gen, args=(car_queue, stop_event))
    
    # Démarrer les processus
    light_process.start()
    traffic_process.start()
    
    # Création de la fenêtre principale tkinter
    root = tk.Tk()
    root.title("Simulation de Croisement")
    
    # Lancer la simulation
    gui = CrossroadSimulation(root, light_state, cars_ns, cars_we, car_queue, stop_event)
    
    # Lancer l'interface graphique tkinter
    root.mainloop()
    
    # Arrêter les processus lorsque la fenêtre se ferme
    stop_event.set()
    light_process.join()
    traffic_process.join()

if __name__ == "__main__":
    main()




# une queue pour car par tronçon
# virer trucs bizarres dans display
# les sockets envoient les communications des queues au display