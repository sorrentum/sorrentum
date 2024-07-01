import zmq
import asyncio
from zmq.asyncio import Context, Poller

async def server():
    try:
        context = Context.instance()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:5555")
        
        poller = Poller()
        poller.register(socket, zmq.POLLIN)

        while True:
            events = await poller.poll(timeout=1000)  # Poll for 1 second
            
            if socket in dict(events):
                try:
                    # Receive request from client
                    message = await socket.recv_multipart()
                    
                    # Check if the message has the correct format
                    if len(message) != 2:
                        print("Received invalid message from client")
                        await socket.send_multipart([address ,b"Invalid message"])
                        continue  # Skip processing invalid messages

                    address, req = message
                    print("Received request:", req.decode())

                    # Send response to client
                    await socket.send_multipart([address, b"Server response"])
                except zmq.error.ZMQError as e:
                    print(f"ZMQ error: {e}")

            else:
                print("Timeout occurred while waiting for request from client")

    except zmq.error.ZMQError as e:
        print(f"ZMQ error during initialization: {e}")

if __name__ == "__main__":
    asyncio.run(server())

