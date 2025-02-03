import time
import random
import multiprocessing
import tkinter as tk
import socket
import threading

# ======================= TRAFIC NORMAL ======================= #
def normal_traffic_gen(NS_queue, WE_queue):
    """ Génère des voitures normales à intervalles aléatoires. """
    while True:
        time.sleep(random.uniform(1, 5))
        direction = random.choice([0, 1])  # 0 = NS, 1 = WE
        queue = NS_queue if direction == 0 else WE_queue
        direction_str = "NS" if direction == 0 else "WE"

        car = {"source": direction_str, "priority": False, "movement": random.choice(["straight", "left", "right"])}
        queue.put(car)
        print(f"🚗 Voiture ajoutée : {car}")

# ======================= TRAFIC PRIORITAIRE ======================= #
def priority_traffic_gen(NS_queue, WE_queue, priority_signal):
    """ Génère des véhicules prioritaires (ambulance, police). """
    while True:
        time.sleep(random.uniform(10, 30))
        direction = random.choice([0, 1])
        queue = NS_queue if direction == 0 else WE_queue
        direction_str = "NS" if direction == 0 else "WE"

        car = {"source": direction_str, "priority": True, "movement": random.choice(["straight", "left", "right"])}
        queue.put(car)
        priority_signal.value = 1 if direction == 0 else 2  # 1 = priorité NS, 2 = priorité WE
        print(f"🚑 Véhicule prioritaire détecté : {car}")

# ======================= GESTION DES FEUX ======================= #
def lights_process(light_status, priority_signal):
    """ Change les feux et donne priorité aux véhicules prioritaires. """
    while True:
        time.sleep(5)
        if priority_signal.value:
            light_status.value = "GREEN RED" if priority_signal.value == 1 else "RED GREEN"
            time.sleep(3)
            priority_signal.value = 0
        else:
            if ''.join(light_status).strip() == "GREEN RED":
                light_status[:] = "RED GREEN".ljust(10)
            else:
                light_status[:] = "GREEN RED".ljust(10)


# ======================= COORDINATEUR ======================= #
def coordinator(NS_queue, WE_queue, light_status):
    """ Gère l'écoulement du trafic en fonction des feux. """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 5000))

    while True:
        time.sleep(0.1)
        ns_light, we_light = light_status.value.split()
        
        if ns_light == "GREEN" and not NS_queue.empty():
            car = NS_queue.get()
            sock.sendall(f"{car}\n".encode())

        if we_light == "GREEN" and not WE_queue.empty():
            car = WE_queue.get()
            sock.sendall(f"{car}\n".encode())

# ======================= AFFICHAGE ======================= #
WINDOW_SIZE = 500
CAR_SIZE = 20

class CrossroadSimulation:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=WINDOW_SIZE, height=WINDOW_SIZE, bg="white")
        self.canvas.pack()
        self.lights = {"NS": "RED", "WE": "GREEN"}
        self.cars = []
        
        threading.Thread(target=self.receive_cars, daemon=True).start()
        threading.Thread(target=self.receive_lights, daemon=True).start()
        
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
        direction = car_info["source"]
        x, y = (WINDOW_SIZE // 2 - 10, 0) if direction == "NS" else (0, WINDOW_SIZE // 2 - 10)
        dx, dy = (0, 5) if direction == "NS" else (5, 0)
        
        car = self.canvas.create_rectangle(x, y, x + CAR_SIZE, y + CAR_SIZE, fill="blue")
        self.cars.append({"car": car, "dx": dx, "dy": dy})

    def update_simulation(self):
        for car_info in self.cars:
            car = car_info["car"]
            dx, dy = car_info["dx"], car_info["dy"]
            self.canvas.move(car, dx, dy)

        self.root.after(50, self.update_simulation)

def run_gui():
    root = tk.Tk()
    CrossroadSimulation(root)
    root.mainloop()

# ======================= MAIN ======================= #
if __name__ == "__main__":
    NS_queue = multiprocessing.Queue()
    WE_queue = multiprocessing.Queue()
    light_status = multiprocessing.Array("u", "GREEN RED".ljust(10))

    priority_signal = multiprocessing.Value("i", 0)

    multiprocessing.Process(target=lights_process, args=(light_status, priority_signal)).start()
    multiprocessing.Process(target=coordinator, args=(NS_queue, WE_queue, light_status)).start()
    multiprocessing.Process(target=normal_traffic_gen, args=(NS_queue, WE_queue)).start()
    multiprocessing.Process(target=priority_traffic_gen, args=(NS_queue, WE_queue, priority_signal)).start()

    run_gui()
