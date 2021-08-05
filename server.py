import socket
from _thread import *
import json


class Player:

    def __init__(self, id):
        self.temp_id = id
        self.x = (id + 1) * 100
        self.y = (id + 1) * 100

        self.weapon_0 = 'fist'
        self.weapon_1 = 'fist'
        self.dead = False
        self.angle = 0 

        self.online = False

    def get_data(self):
        data = {
            'x': self.x,
            'y': self.y,
            'weapon_0': self.weapon_0,
            'weapon_1': self.weapon_1,
            'dead': self.dead,
            'angle': self.angle,
            'id': self.temp_id,
            'online': self.online,
        }
        return data

    def update_data(self, data):
        self.x = data['x']
        self.y = data['y']
        self.angle = data['angle']

class Server:

    def __init__(self):
        # server = '161.35.65.19'
        self.server  = ''
        self.port = 50006
        self.players = []
        self.players_number = 0
        self.temp_id = 0

        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.my_socket.settimeout(5.0)
        try:
            self.my_socket.bind((self.server, self.port))
        except (Exception, socket.error) as error:
            print(error)

        self.my_socket.listen(2)
        print('Waiting for connection, server started')

    def threaded_client(self, addr, cliend_id):
        
        self.temp_id += 1
        data = json.dumps(self.players[cliend_id].get_data())
        print(f'all players: ')
        for count, player in enumerate(self.players):
            print(f'{count}. pos: ({player.x}, {player.y}), id: {player.temp_id}')
        conn.send(str.encode(data))
        
        reply = {'test': 'test message'}

        while True:
            try:
                data = json.loads(conn.recv(2048 * 2))
                print(f'received data from player{data["id"]}')
                # print(f'data from player{data["temp_id"]}:\n{data}')
                # self.players[cliend_id].update_data(data)

                if not data:
                    print('Disconnected')
                    break
                else:
                    conn.sendall(str.encode(json.dumps(reply)))
            except Exception:
                break

        print(f'Lost connection')
        # self.players.remove(self.players[cliend_id])
        self.players_number -= 1
        conn.close()


if __name__ == '__main__':
    server = Server()
    while True:
        conn, addr = server.my_socket.accept()
        print(f'connected to: {addr}')

        new_player = Player(server.temp_id)
        server.players.append(new_player)
        server.players_number += 1
        start_new_thread(server.threaded_client, (addr, server.temp_id))
