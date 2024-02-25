import threading
import socket
class ServerNetwork:
    def __init__(self)->None:
        '''
        creates a socket with IPV4 Address Family(AF_INET), having a random port 
        b/w 5000 to 65534 then binds to that socket object and starting listening to that socket
        Initializes list of clients and number of active clients
        '''
        self.clients = []
        self.lock = threading.Lock()
        self.active_clients = 0  # Instance attribute to track active clients
        

    def start_server(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = socket.gethostbyname(socket.gethostname())  # Get the local machine's IP address
        self.port = 55555
        self.server.bind((self.host, self.port))  
        self.server.listen()
        receive_thread = threading.Thread(target=self.receive_from_clients)
        receive_thread.start()
        print(f"hosting server @ {self.host}:{self.port}")

    def increment_active_clients(self)->None:
        """increments active clients count by 1"""
        self.active_clients += 1

    def decrement_active_clients(self)->None:
        """decrements active clients count by 1"""
        self.active_clients -= 1

    def broadcast(self, message:bool, sending_client=None)->None:
        '''
        by default broadcasts message recived as argumenst to the cleints present in self.clients[]
        if sending_client is provided as argument then message is broadcasted except for the sending 
        client
        '''
        with self.lock:
            for client in self.clients:
                if client != sending_client:
                    client.send(message)
                    
    def msg_frm_server_to_start(self)->None:
        '''
        uses self.broadcast method to broadcast message originated by the server
        '''
        self.broadcast(True)
        
    def msg_frm_server_to_stop(self)->None:
        '''
        uses self.broadcast method to broadcast message originated by the server
        '''
        self.broadcast(False)
        
    def handle_client(self, client):
        ''''
        continuously tries to recieve message and if any exception occurs 
        client is removed from self.clients[] list and connection with that client is closed
        '''
        while True:
            try:
                message = client.recv(1024)
                if message:
                    print(f"Received from {client.getpeername()}: {message.decode('ascii')}")
                    self.broadcast(message, client)
            except:
                '''
                 as many threads may try to remove cleints or decrement number of active clients 
                 here we have a scope race condtion so, lock object would acquire the lock while 
                 making changes to cleints list or decrementing clients and release the lock after
                 closing the client connection(acquiring and releasing of lock is done by with context manager)
                 '''
                with self.lock:
                    if client in self.clients:
                        self.clients.remove(client)
                        self.decrement_active_clients()  # Decrement active clients when a client leaves
                    client.close()
                break

    def receive_from_clients(self):
        """
        accepts incoming client request and creates a new thread for every new client
        """
        while True:
            client, address = self.server.accept()
            # accept() -> waits for a client connection
            print(f"Server: {address} connected.")
            
            '''
            Increment active clients when a new client connects
            we don't need thread synchronization while incrementing active clients count because
            there is no scope of race condition here
            '''
            self.increment_active_clients()  

            # adding client to self.clients[] 
            self.clients.append(client)

            '''
            creating new thread for the client
            new thread is created for every new client
            '''
            thread = threading.Thread(target=self.handle_client, args=(client,))
            thread.start()
            print(self.active_clients)

            self.broadcast(f"\nserver: {address} joined!".encode('ascii'))
