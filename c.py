import threading
import socket
from kivy.clock import Clock

class ClientNetwork:
    msg = False 
        
    def connect(self, host, port)->None:
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        
    def receive_from_server(self):
        while True:
            try:
                message = self.client.recv(1024).decode('ascii')
                print(message)
                ClientNetwork.msg = message
                Clock.schedule_interval(self.check_state,1)
            except Exception as e:
                print("An error occurred while receiving from the server:", str(e))
                self.client.close()
                break
            
    def send_to_server_start(self):
            try:
                message = True
                self.client.send(message.encode('ascii'))
            except Exception as e:
                print("An error occurred while sending to the server:", str(e))

    def send_to_server_stop(self):
            try:
                message = False
                self.client.send(message.encode('ascii'))
            except Exception as e:
                print("An error occurred while sending to the server:", str(e))