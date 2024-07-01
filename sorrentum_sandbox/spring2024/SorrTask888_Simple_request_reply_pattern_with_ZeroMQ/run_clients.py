import subprocess
import multiprocessing

def run_client_instance():
    subprocess.run(["docker-compose", "up", "--build", "client"])

if __name__ == "__main__":
    # Define the number of client instances to run
    num_clients = 2
    
    # Create a list to hold references to the client processes
    client_processes = []

    # Start multiple client instances concurrently
    for _ in range(num_clients):
        client_process = multiprocessing.Process(target=run_client_instance)
        client_process.start()
        client_processes.append(client_process)

    # Wait for all client processes to finish
    for client_process in client_processes:
        client_process.join()
