import socket
import json

class Network:

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = '127.0.0.1'
        self.port = 50006
        self.addr = (self.server, self.port)
        self.player = self.connect()
        print(f'player: {self.player}\n')

    def connect(self):
        try:
            self.client.connect(self.addr)
            print('connected')
            return json.loads(self.client.recv(2048).decode())
        except (Exception, socket.error) as error:
            print(f'not connected \nerror: {error}')

    def send(self, data):
        try:
            self.client.send(str.encode(json.dumps(data)))
            print(json.loads(self.client.recv(2048 * 2)))
        except (Exception, socket.error) as error:
            print(f'error: {error}')

    def get_player_pos(self):
        return (self.player['x'], self.player['y'])

    def get_player_id(self):
        return self.player['id']