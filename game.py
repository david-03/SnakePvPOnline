import pygame
import random

# Length in pixels of each square
BOX = 32
# Colors used
RED = (255, 0, 0)
BLUE = (0, 100, 255)
GREEN = (0, 160, 0)
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


# General function for drawing a solid square based on column and row alone (no need to calculate pixels every time)
def square(win, color, col, row, width=0):
    # Get window size
    w, h = win.get_size()
    # Get upper left corner
    x = w / 2 - game_w / 2
    y = (h - 75) / 2 - game_h / 2
    # Important to put int(x) and int(y) to round them to the nearest integer (pixel number)
    square1 = pygame.Rect((int(x) + col * BOX, int(y) + row * BOX), (BOX, BOX))
    # Draw pygame rectangle
    pygame.draw.rect(win, color, square1, width)


# Snake object
class Snake:
    # Declare the attributes that each snake has
    def __init__(self, start_col, start_row, color):
        # Snake body is a list that contains the position of each body part as tuples (column, row)
        self.body = [(start_col, start_row), (start_col - 1, start_row), (start_col - 2, start_row)]
        # Dictionary that stores the position at which each body part has to turn and the turn itself
        # (column, row) = (right, left, up or down)
        self.turns = {}
        # Each body part has a speed on the x axis and on the y axis
        # Index of speeds is the same as index of body parts
        self.speed_x = [1, 1, 1]
        self.speed_y = [0, 0, 0]
        # Snakes have different colors
        self.color = color
        # Temporary variable that stores the turn at one precise moment
        self.dir = 0
        # Store the number of moves made by the snake in order to synchronize the two players
        self.moves = 0

    # Moving the snake by one box
    def move(self):
        self.moves += 1
        # For each body part on the snake
        for i in range(len(self.body)):
            # Reverse the order to move tail first, in order to remove turns that are not in body anymore
            ind = -i - 1
            (col, row) = self.body[ind]
            # Check if the body part position corresponds to a turn
            if (col, row) in self.turns.keys():
                # Get the turn and change speed accordingly
                self.dir = self.turns.get((col, row))
                if self.dir == 'r':
                    self.speed_x[ind] = 1
                    self.speed_y[ind] = 0
                if self.dir == 'l':
                    self.speed_x[ind] = -1
                    self.speed_y[ind] = 0
                if self.dir == 'u':
                    self.speed_x[ind] = 0
                    self.speed_y[ind] = -1
                if self.dir == 'd':
                    self.speed_x[ind] = 0
                    self.speed_y[ind] = 1

            # Change position of body part based on speed
            col += self.speed_x[ind]
            row += self.speed_y[ind]
            self.body[ind] = (col, row)

            # Delete turns that are gone (turns that are outside of the snake body)
            for (col, row) in list(self.turns):
                if (col, row) not in self.body:
                    self.turns.pop((col, row))


# Game object
class Game:
    def __init__(self, id_num):
        # Players' state
        self.p1_ready = False
        self.p2_ready = False
        # Create two snake objects
        self.players = [Snake(4, num_row // 2 - 1, BLUE), Snake(4, num_row // 2 + 1, GREEN)]
        # Game state
        self.ready = False
        # Game ID
        self.id = id_num
        # Number of wins per player
        self.wins = [0, 0]
        # List to store any losers
        self.losers = []
        # Initial apple position
        self.apple_pos = (3 * num_col // 4, num_row // 2)
        # Temporary variable to tell server if player has eaten
        self.ate = False
        # Temporary variable to tell client which player they are
        self.current_player = 0

    # Function used to draw a snake
    def draw(self, win, player):
        for (col, row) in self.players[player].body:
            square(win, self.players[player].color, col, row)

    # Check if game is ready (two players connected)
    def connected(self):
        return self.ready

    # Check if both players are ready to start playing
    def both_ready(self):
        return self.p1_ready and self.p2_ready

    # Check if a snake dies
    def lose(self, player_num):
        # Snake head
        (col, row) = self.players[player_num].body[0]
        # Check if snake head is inside its own body
        if (col, row) in self.players[player_num].body[1:]:
            return True
        # Check if snake head is inside the other snake's body
        if player_num == 0:
            if (col, row) in self.players[1].body:
                return True
        elif player_num == 1:
            if (col, row) in self.players[0].body:
                return True
        # Check if snake head is outside of game grid
        if col < 0 or row < 0 or col >= num_col or row >= num_row:
            return True
        # If none of the conditions are met, snake did not die
        return False

    # Check collision between snake head and apple (boolean function)
    def check_eat(self, win, player_num):
        (applec, appler) = self.apple_pos
        # Get window dimensions
        w, h = win.get_size()
        # Pixel position of upper left corner
        x = w / 2 - game_w / 2
        y = (h - 75) / 2 - game_h / 2
        # Get snake head position
        (col, row) = self.players[player_num].body[0]
        # Get rectangles that represent the snake head and the apple
        head = pygame.Rect((int(x) + col * BOX, int(y) + row * BOX), (BOX, BOX))
        apple1 = pygame.Rect((int(x) + applec * BOX, int(y) + appler * BOX), (BOX, BOX))
        # If the two rectangles overlap, there is collision
        if head.colliderect(apple1):
            # Add one body part to the tail depending on the tail's current speed
            (col, row) = self.players[player_num].body[-1]
            # Add new tail one square behind current tail
            self.players[player_num].body.append((col - self.players[player_num].speed_x[-1],
                                                  row - self.players[player_num].speed_y[-1]))
            # Add the current tail speed at the end of the speed list for the new tail
            self.players[player_num].speed_x.append(self.players[player_num].speed_x[-1])
            self.players[player_num].speed_y.append(self.players[player_num].speed_y[-1])
            return True
        # If no collision, function returns False
        return False

    # Create new apple
    def apple(self, win):
        while True:
            # Change the apple position globally, not just locally
            applec = random.randint(0, num_col - 1)
            appler = random.randint(0, num_row - 1)
            # Get a position that is not already in a snake
            if (applec, appler) not in self.players[0].body and (applec, appler) not in self.players[1].body:
                break
        # Update apple position
        self.apple_pos = (applec, appler)

    # Check if game is over
    def game_over(self, win, FONT_50):
        # If one or both players lose
        if len(self.losers) != 0:
            w, h = win.get_size()
            # Check for tie
            if len(self.losers) == 2:
                (head_x, head_y) = self.players[0].body[0]
                (head2_x, head2_y) = self.players[1].body[0]
                # Draw turquoise square on both heads if they collided with each other
                if (head_x, head_y) == (head2_x, head2_y):
                    square(win, (0, 200, 150), head_x, head_y)
                # Display text box, dimensions depend on window size
                text_box = pygame.Rect((w // 2 - 50, (h - 100) // 2 - 15), (80, 60))
                pygame.draw.rect(win, YELLOW, text_box)
                text = FONT_50.render('TIE', True, RED)
                win.blit(text, (w // 2 - 40, (h - 100) // 2))
            # If no tie
            else:
                # Check who lost, increase score of opponent and display text box
                if self.losers[0] == 0:
                    text_box = pygame.Rect((w // 2 - 115, (h - 100) // 2 - 15), (255, 60))
                    pygame.draw.rect(win, YELLOW, text_box)
                    text = FONT_50.render('GREEN WINS', True, GREEN)
                    win.blit(text, (w // 2 - 100, (h - 100) // 2))
                    self.wins[1] += 1
                elif self.losers[0] == 1:
                    text_box = pygame.Rect((w // 2 - 115, (h - 100) // 2 - 15), (225, 60))
                    pygame.draw.rect(win, YELLOW, text_box)
                    text = FONT_50.render('BLUE WINS', True, BLUE)
                    win.blit(text, (w // 2 - 100, (h - 100) // 2))
                    self.wins[0] += 1
            pygame.display.flip()
            # Wait 3 seconds
            pygame.time.delay(2500)
            # Reset players' state
            self.p1_ready = False
            self.p2_ready = False
            # Reset players
            self.players = [Snake(4, num_row // 2 - 1, BLUE), Snake(4, num_row // 2 + 1, GREEN)]
            # Reset losers list
            self.losers = []
            # Reset apple position
            self.apple_pos = (3 * num_col // 4, num_row // 2)
            return True
        # If no players lost
        return False
