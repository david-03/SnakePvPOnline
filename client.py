import pygame
from network import Network

# Initialize pygame
pygame.init()
# Create fonts
FONT = pygame.font.SysFont('comicsans', 30)
FONT_50 = pygame.font.SysFont('comicsans', 50)

# Length in pixels of each square
BOX = 32
# Colors used
RED = (255, 0, 0)
BLUE = (0, 100, 255)
GREEN = (0, 160, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

# Default grid dimensions
num_col = 17
num_row = 15
# Width and Height of the game grid in pixels
game_w = num_col * BOX
game_h = num_row * BOX
# Width and Height of the window in pixels (changes depending on window mode)
win_width = game_w
win_height = game_h + 75

# Create pygame window
win = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("SnakePvP")
icon = pygame.image.load('data\\snake.png')
pygame.display.set_icon(icon)


# General function to draw a pygame square at any column, row position
def square(window, color, col, row, width=0):
    w, h = window.get_size()
    # Upper left corner pixel position
    x = w / 2 - game_w / 2
    y = (h - 75) / 2 - game_h / 2
    # Important to put int(x) and int(y) to round them to the nearest integer (pixel number)
    square1 = pygame.Rect((int(x) + col * BOX, int(y) + row * BOX), (BOX, BOX))
    pygame.draw.rect(window, color, square1, width)


def draw_window(window, game, player_num, start):
    window.fill(BLACK)
    # Grid dimensions depend on window size
    w, h = window.get_size()
    x = w / 2 - game_w / 2
    y = (h - 75) / 2 - game_h / 2
    # Draw a rectangle which is the outline of the entire game grid
    r1 = pygame.Rect((int(x), int(y)), (game_w, game_h))
    pygame.draw.rect(window, WHITE, r1, 1)
    # Draw a rectangle for every two columns (one rectangle = two lines = two columns drawn)
    for n in range(1, num_col // 2 + 1):
        r_x = x + (2 * n - 1) * BOX
        r_n = pygame.Rect((int(r_x), int(y)), (BOX, game_h))
        pygame.draw.rect(window, WHITE, r_n, 1)
    # Draw a rectangle for every two rows (one rectangle = two lines = two rows drawn)
    for n in range(1, num_row // 2 + 1):
        r_y = y + (2 * n - 1) * BOX
        r_n = pygame.Rect((int(x), int(r_y)), (game_w, BOX))
        pygame.draw.rect(window, WHITE, r_n, 1)

    # Check if there's only one player connected to current game
    if not game.connected():
        text = FONT_50.render("Waiting for player...", True, RED)
        window.blit(text, (game_w // 2 - text.get_width() // 2, game_h // 2 - text.get_height() // 2))

    else:
        # Draw apple
        (applec, appler) = game.apple_pos
        square(window, RED, applec, appler)
        # Draw snakes
        for player in range(2):
            game.draw(window, player)

        # Print the score based on window size
        score_y = y + game_h + 20
        score1_x = x + 20
        score1_text = FONT_50.render("BLUE : " + str(game.wins[0]), True, BLUE)
        score2_x = x + (num_col - 6) * BOX
        score2_text = FONT_50.render("GREEN : " + str(game.wins[1]), True, GREEN)
        window.blit(score2_text, (int(score2_x), int(score_y)))
        window.blit(score1_text, (int(score1_x), int(score_y)))

        # If the player is still in the start menu
        if start:
            # Draw transparent rectangle if a player is ready
            if game.p1_ready:
                s = pygame.Surface((game_w, game_h // 2))
                s.set_alpha(128)
                s.fill(BLUE)
                window.blit(s, (w // 2 - game_w // 2, (h - 75) // 2 - game_h // 2))
            # If current player not ready, display text box
            elif player_num == 0:
                start_msg = FONT.render("YOU ARE BLUE. WHEN READY, PRESS 'R'", True, game.players[player_num].color)
                # Centered, a quarter of the way down the screen
                text_x_pos = game_w // 2 - start_msg.get_width() // 2
                text_y_pos = game_h // 4 - start_msg.get_height() // 2
                text_box = pygame.Rect((text_x_pos - 10, text_y_pos - 5),
                                       (start_msg.get_width() + 20, start_msg.get_height() + 10))
                pygame.draw.rect(window, YELLOW, text_box)
                window.blit(start_msg, (text_x_pos, text_y_pos))
            # Idem
            if game.p2_ready:
                s = pygame.Surface((game_w, game_h // 2))
                s.set_alpha(128)
                s.fill(GREEN)
                window.blit(s, (w // 2 - game_w // 2, (h - 75) // 2))
            elif player_num == 1:
                start_msg = FONT.render("YOU ARE GREEN. WHEN READY, PRESS 'R'", True, game.players[player_num].color)
                text_x_pos = game_w // 2 - start_msg.get_width() // 2
                text_y_pos = game_h // 4 - start_msg.get_height() // 2
                text_box = pygame.Rect((text_x_pos - 10, text_y_pos - 5),
                                       (start_msg.get_width() + 20, start_msg.get_height() + 10))
                pygame.draw.rect(window, YELLOW, text_box)
                window.blit(start_msg, (text_x_pos, text_y_pos))

    # Update display
    pygame.display.flip()


def main():
    # Create a network object for the client to communicate with server
    n = Network()
    # Get game from server via network
    game = n.get_game()
    # Save player number in variable
    player_num = game.current_player
    # Create clock to regulate FPS
    clock = pygame.time.Clock()

    # Game loop
    playing = True
    while playing:

        start = True
        run = True
        # Start menu
        while start:
            try:
                # Try to send game to and receive game from server
                game = n.send(game)
            except Exception as general_error:
                print(general_error)
                print("Couldn't get game")
                playing = False
                # Client code will keep trying to connect to server until it receives game from server
                break
            # 10 FPS
            clock.tick(10)

            # Check if player quit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

                # Check if player is ready
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    if player_num == 0:
                        game.p1_ready = True
                    elif player_num == 1:
                        game.p2_ready = True

            # If both players are ready to start
            if game.both_ready():
                # Send and receive current game
                game = n.send(game)
                # Draw window
                draw_window(win, game, player_num, start)

                # Countdown
                for i in range(3):
                    w, h = win.get_size()
                    count = FONT_50.render(str(3 - i), True, WHITE)
                    win.blit(count, (w // 2 - 10, (h - 175 + i * 75) // 2))
                    pygame.display.flip()
                    pygame.time.delay(750)

                # Stop loop
                start = False

            # Draw window
            draw_window(win, game, player_num, start)

        # Run loop (main game)
        while run:
            # 5 FPS
            clock.tick(5)

            # Scan events
            for event in pygame.event.get():
                # If client quits
                if event.type == pygame.QUIT:
                    playing = False
                    run = False
                    pygame.quit()

                if event.type == pygame.KEYDOWN:
                    # Check if player turns (keys u l d r) and record the turn in player turns dictionary
                    if game.players[player_num].speed_x[0] == 0:
                        if event.key == pygame.K_RIGHT:
                            (col, row) = game.players[player_num].body[0]
                            game.players[player_num].turns[(col, row)] = 'r'
                        elif event.key == pygame.K_LEFT:
                            (col, row) = game.players[player_num].body[0]
                            game.players[player_num].turns[(col, row)] = 'l'
                    elif game.players[player_num].speed_y[0] == 0:
                        if event.key == pygame.K_UP:
                            (col, row) = game.players[player_num].body[0]
                            game.players[player_num].turns[(col, row)] = 'u'
                        elif event.key == pygame.K_DOWN:
                            (col, row) = game.players[player_num].body[0]
                            game.players[player_num].turns[(col, row)] = 'd'

            try:
                # Receive updated game from server
                data = n.send(game)
                # Keep current player properties on the client's side
                player = game.players[player_num]
                # Overwrite current player in game received from server
                data.players[player_num] = player
                # Replace everything else in local game by game received from server
                game = data
                # Store second player properties in local variable
                if player_num == 0:
                    player2 = data.players[1]
                else:
                    player2 = data.players[0]

            # If client doesn't receive anything from server
            except Exception as general_error:
                print(general_error)
                print("Couldn't get game")
                playing = False
                # Client code will keep trying to connect to server until it receives game from server
                break

            # Move only if current player's number of moves is smaller or equal to player two's
            if game.players[player_num].moves <= player2.moves:
                # Code to execute only if both players' number of moves is the same
                # (avoid one player being ahead of the other)
                if game.players[player_num].moves == player2.moves:
                    # Check if snake ate apple
                    if game.check_eat(win, player_num):
                        # Tell server that the snake ate
                        game.ate = True
                        # Generate new apple position
                        game.apple(win)
                    # Draw window and both snakes
                    draw_window(win, game, player_num, start)
                    # Check both snakes to see if one or both lost
                    for p in range(2):
                        if game.lose(p):
                            # Update losers list
                            game.losers.append(p)
                    # Check if game is over
                    if game.game_over(win, FONT_50):
                        # Reset players' state
                        game.p1_ready = False
                        game.p2_ready = False
                        # Tell server to update apple position
                        game.ate = True
                        # Send the game
                        _ = n.send(game)
                        # Start new playing loop
                        break

                # Move player
                game.players[player_num].move()

                # Repeat same steps as before in case current player was ahead of or behind player two
                try:
                    # Receive updated game from server
                    data = n.send(game)
                    # Keep current player properties on the client's side
                    player = game.players[player_num]
                    # Overwrite current player in game received from server
                    data.players[player_num] = player
                    # Replace everything else in local game by game received from server
                    game = data
                    # Store second player properties in local variable
                    if player_num == 0:
                        player2 = data.players[1]
                    else:
                        player2 = data.players[0]
                # If client doesn't receive anything from server
                except Exception as general_error:
                    print(general_error)
                    print("Couldn't get game")
                    playing = False
                    # Client code will keep trying to connect to server until it receives game from server
                    break

                # If the updated players have the same number of moves
                if game.players[player_num].moves == player2.moves:
                    # Check if snake ate apple
                    if game.check_eat(win, player_num):
                        # Tell server that the snake ate
                        game.ate = True
                        # Generate new apple position
                        game.apple(win)
                    # Draw window and both snakes
                    draw_window(win, game, player_num, start)
                    # Check both snakes to see if one or both lost
                    for p in range(2):
                        if game.lose(p):
                            # Update losers list
                            game.losers.append(p)
                    # Check if game is over
                    if game.game_over(win, FONT_50):
                        # Reset players' state
                        game.p1_ready = False
                        game.p2_ready = False
                        # Tell server to update apple position
                        game.ate = True
                        # Send the game
                        _ = n.send(game)
                        # Start new playing loop
                        break


if __name__ == '__main__':
    # Loop until user quits
    while True:
        try:

            # If the other player quits, the current one will disconnect and reconnect to server
            try:
                main()
            except pygame.error:
                break

        # If client can't receive game from user, try again instead of terminating client
        except AttributeError:
            pass
