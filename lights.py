import multiprocessing

def update(proc_id, data):
    print("starting process:", multiprocessing.current_process().name)
    if proc_id % 2:
        data.value += 1
    else:
        data.value -= 1
    print("ending process:", multiprocessing.current_process().name)            
 
if __name__ == "__main__":
    
    data = multiprocessing.Value('d', 0, lock=False)
 
    process = multiprocessing.Process(target=worker, args=(i, data))
 
    process.start()
    process.join()
 
    print(f"Value of data needs to be 0, got {data.value}")