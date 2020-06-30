import socket
from _thread import *
import pickle
from game import Game

# Local IP address
server = "10.0.0.248"
port = 5555

# Create socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Bind socket to IP address
    s.bind((server, port))
except socket.error:
    pass

# Listen for client requesting connection
s.listen()
print("Waiting for a connection, server started.")

# Dictionary of games (key = game ID, item = game object)
games = {}


# Code to execute for each connected client
def threaded_client(connection, player_num, game_id_key):

    try:
        # Update current player number in current game
        games[game_id_key].current_player = player_num
        # Send game to client
        connection.send(pickle.dumps(games[game_id_key]))
    # If game is deleted, pass instead of ending server
    except KeyError:
        pass

    # Game loop for each client
    while True:
        try:
            # Retrieve data received from client
            data = pickle.loads(connection.recv(2048 * 2))
            # Check if game exists
            if game_id_key in games:
                # Check if client actually sent something
                if not data:
                    break

                # Update player state in game
                if player_num == 0:
                    games[game_id_key].p1_ready = data.p1_ready
                else:
                    games[game_id_key].p2_ready = data.p2_ready

                # Update number of wins
                games[game_id_key].wins[player_num] = data.wins[player_num]

                # Update player (Snake object)
                games[game_id_key].players[player_num] = data.players[player_num]

                # If player ate, update apple position
                if data.ate:
                    games[game_id_key].apple_pos = data.apple_pos

                # Send back updated game to player
                reply = games[game_id_key]
                connection.sendall(pickle.dumps(reply))

            # If game has been deleted
            else:
                break

        # If there is an error, pass instead of terminating server
        except Exception as error:
            print(error)
            break

    # Code to execute when client is disconnected
    print("Disconnected from client...")
    try:
        # Delete corresponding game
        del games[game_id_key]
        print("Closing Game " + str(game_id_key) + "\n")
    # If game is already deleted, pass instead of terminating server
    except Exception as general_error:
        print("Game already closed, game ID: " + str(general_error) + "\n")
    # Close connection
    connection.close()


# Server loop
while True:
    # Accept any connection from socket
    conn, addr = s.accept()
    print("Connected to: " + str(addr))

    # Set default player number as 0
    player = 0

    # Loop to find available games
    game_id = 0
    check = True
    # Check for created games with only one player
    for i in games.keys():
        if len(games) != 0 and not games[i].ready:
            try:
                game_id = i
                # Update game state
                games[game_id].ready = True
                print("Client connected to an existing game...")
                print("Game ID: " + str(game_id) + '\n')
            # If the game has been deleted, pass instead of terminating server
            except KeyError:
                pass
            # Set player number as 1 (player one is number 0 and player two is number 1)
            player = 1
            check = False
            break
    while check:
        # Game not created yet
        if game_id not in games.keys():
            # Create new game
            games[game_id] = Game(game_id)
            print("Creating a new game...")
            print("Game ID: " + str(game_id) + '\n')
            break
        # Game created, but two players already
        game_id += 1

    # Start client thread
    start_new_thread(threaded_client, (conn, player, game_id))
