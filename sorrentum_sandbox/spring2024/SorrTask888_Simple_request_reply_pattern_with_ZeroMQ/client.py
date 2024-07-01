import zmq


def client():
    try:
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://server:5555")

        # Set timeout for socket operations (in milliseconds)
        socket.setsockopt(zmq.RCVTIMEO, 5000)  # 5 seconds

        for request_num in range(10):
            try:
                # Send request to server
                print("Sending request:", request_num)
                
                # Intentionally send a malformed request on the third request
                if request_num == 2:
                    socket.send_multipart([b"Client request"])  # Missing empty address
                else:
                    socket.send_multipart([b"", b"Client request"])
                
                # Receive response from server
                message = socket.recv_multipart()
                address, response = message
                print("Received response:", response.decode())

            except zmq.error.ZMQError as e:
                if e.errno == zmq.ETERM:
                    print("Socket closed during operation.")
                elif e.errno == zmq.EAGAIN:
                    print("Timeout occurred while waiting for response.")
                else:
                    print(f"Error occurred during message exchange: {e}")

    except zmq.error.ZMQError as e:
        print(f"Error occurred during initialization: {e}")

if __name__ == "__main__":
    client()

