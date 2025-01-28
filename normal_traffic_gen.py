import threading
from queue import Queue
import random

def worker(queue, data_ready):
    print("Starting thread:", threading.current_thread().name)    
    data_ready.wait()
    value = queue.get()
    data[0] = random.uniform[0,4]
    data[1] = random.uniform[0,4]
    print("Ending thread:", threading.current_thread().name)

if __name__ == "__main__":   
    print("Starting thread:", threading.current_thread().name)

    queue = Queue()
    data_ready = threading.Event()

    thread = threading.Thread(target=worker, args=(queue, data_ready))
    thread.start()

    data = [0,0,0]

    queue.put(data)
    data_ready.set()

    thread.join()

    print("Ending thread:", threading.current_thread().name)


    