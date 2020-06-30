import socket
import pickle


# Network object
class Network:
    def __init__(self):
        # Create socket
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # IP address
        self.server = "10.0.0.248"
        self.port = 5555
        self.addr = (self.server, self.port)
        # Current game
        self.game = self.connect()

    def get_game(self):
        return self.game

    # Connect with server and receive the game sent by server
    def connect(self):
        try:
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(2048 * 2))
        except Exception as general_error:
            print(general_error)

    # Function used to send current game to server and receive game sent by server
    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048 * 2))
        except Exception as error:
            print(error)
