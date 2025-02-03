import tkinter as tk

WINDOW_SIZE = 500
ROAD_WIDTH = 100
CAR_SIZE = 20
COLORS = {"RED": "red", "GREEN": "green"}

# Positions des routes
ROUTES = {
    "NordSud": [(WINDOW_SIZE//2 - ROAD_WIDTH//2, 0, WINDOW_SIZE//2 + ROAD_WIDTH//2, WINDOW_SIZE)],
    "EstOuest": [(0, WINDOW_SIZE//2 - ROAD_WIDTH//2, WINDOW_SIZE, WINDOW_SIZE//2 + ROAD_WIDTH//2)]
}

# Positions des feux de circulation
FEUX = {
    "Nord": (205, 180, 225, 200),  # Feu en haut à gauche
    "Est": (305, 205, 325, 225),  # Feu en haut à droite
    "Sud": (275, 300, 295, 320),  # Feu en bas à droite
    "Ouest": (180, 275, 200, 295)  # Feu en bas à gauche    
}

# Positions des voitures (bord droit de chaque tronçon)
VOITURES = {
    "NordSud_Haut": (205, 50, 225, 70),  # Voiture venant du Nord
    "NordSud_Bas": (275, 450, 295, 470),  # Voiture venant du Sud
    "EstOuest_Gauche": (50, 275, 70, 295),  # Voiture venant de l'Ouest
    "EstOuest_Droite": (450, 205, 470, 225)  # Voiture venant de l'Est
}


class CrossroadSimulation:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=WINDOW_SIZE, height=WINDOW_SIZE, bg="white")
        self.canvas.pack()
        
        # Dessiner les routes
        for road in ROUTES.values():
            for coords in road:
                self.canvas.create_rectangle(coords, fill="gray")
        
        # Dessiner les feux de circula  tion
        self.lights = {}
        for position, coords in FEUX.items():
            color = "RED" if position in ["Nord", "Sud"] else "GREEN"
            self.lights[position] = self.canvas.create_oval(coords, fill=COLORS[color])

        self.voitures = {}
        for position, coords in VOITURES.items():
            self.voitures[position] = self.canvas.create_rectangle(coords, fill="blue")

# Lancer l'interface graphique
if __name__ == "__main__":
    root = tk.Tk()
    app = CrossroadSimulation(root)
    root.mainloop()
