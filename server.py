import threading
import socket

# Server Configuration
host = '127.0.0.1' # Localhost
port = 1234        # Port to listen on (must match client)

# Initialize Server Socket
# AF_INET refers to IPv4, SOCK_STREAM refers to TCP protocol
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# Dictionary to store connected clients: {socket_object: nickname}
clients = {}

def broadcast(message, sender=None):
    """Sends a message to all connected clients except the sender."""
    for client in clients:
        if client != sender:
            try:
                client.send(message)
            except Exception as e:
                print(f"Error broadcasting to {clients.get(client, 'Unknown')}: {e}")

def handle_client(client):
    """
    Main loop for each client thread. 
    Listens for incoming messages from a specific client.
    """
    while True:
        try:
            # Receive message and decode from bytes to string
            message = client.recv(1024).decode('ascii')
            
            # Private Messaging Logic: "private:target_name message_body"
            if message.startswith("private:"):
                # Remove the "private:" prefix and strip leading spaces
                remainder = message[len("private:"):].lstrip()
                
                # Split into target nickname and the actual message
                target, p_message = remainder.split(" ", 1)
                
                # Check if the target user is currently online
                if target in clients.values():
                    # Find the socket belonging to the target nickname
                    target_client = [sock for sock, name in clients.items() if name == target][0]
                    target_client.send(f"Private message from {clients[client]}: {p_message}".encode('ascii'))
                else:
                    client.send(f"User {target} not found.".encode('ascii'))
            
            # Global Messaging Logic: Send to everyone else
            else:
                broadcast(f"{message}".encode('ascii'), sender=client)
                
        except Exception as e:
            # Handle disconnection or errors
            print(f"Error with client {clients.get(client, 'Unknown')}: {e}")
            nickname = clients.pop(client, None) # Remove client from active dictionary
            broadcast(f'{nickname} has left the chat!'.encode('ascii'))
            client.close() # Close the socket connection
            break # Exit the thread loop

def receive_clients():
    """Accepts new connections and initiates the handshake protocol."""
    print('Server is listening...')
    while True:
        # Accept new connection (blocks until a client connects)
        client, address = server.accept()
        print(f"Client connected from {str(address)}")
        
        # Handshake: Ask client for their nickname
        client.send('NAME'.encode('ascii'))
        clientname = client.recv(1024).decode('ascii')
        
        # Register client in the dictionary
        clients[client] = clientname
        
        print(f'The client name is {clientname}')
        
        # Notify others and confirm connection to the client
        broadcast(f'{clientname} has joined the chat!'.encode('ascii'), sender=client)
        client.send('Connected to the chat'.encode('ascii'))
        
        # Start a new thread for this client to allow simultaneous communication
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

if __name__ == "__main__":
    receive_clients()