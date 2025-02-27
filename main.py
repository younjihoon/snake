import pygame
import random
import sys

# ----- Constants -----
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 30
WINDOW_WIDTH = CELL_SIZE * GRID_WIDTH
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS = 10  # Adjust speed as needed

# Colors
BLACK  = (0, 0, 0)
RED    = (255, 0, 0)
BLUE   = (0, 0, 255)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)

# Directions
UP    = (0, -1)
DOWN  = (0, 1)
LEFT  = (-1, 0)
RIGHT = (1, 0)

# ----- Snake Class -----
class Snake:
    def __init__(self, color):
        self.color = color
        # Start at a random position away from edges
        self.positions = [(random.randint(5, GRID_WIDTH-6), random.randint(5, GRID_HEIGHT-6))]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.alive = True

    def get_head(self):
        return self.positions[0]

    def move(self, grow=False):
        if not self.alive:
            return
        head = self.get_head()
        # Using modulo to wrap around the screen
        new_head = ((head[0] + self.direction[0]) % GRID_WIDTH,
                    (head[1] + self.direction[1]) % GRID_HEIGHT)
        self.positions.insert(0, new_head)
        if not grow:
            self.positions.pop()

    def set_direction(self, new_direction):
        # Prevent the snake from reversing on itself
        if (new_direction[0] * -1, new_direction[1] * -1) == self.direction:
            return
        self.direction = new_direction

    def draw(self, surface):
        for pos in self.positions:
            rect = pygame.Rect(pos[0] * CELL_SIZE, pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, self.color, rect)

    def decide_direction(self, food_position, all_snakes):
        """
        A very basic AI: move in the direction that brings the snake closer to the food.
        If the chosen direction would result in an imminent collision, try an alternate.
        """
        head = self.get_head()
        dx = food_position[0] - head[0]
        dy = food_position[1] - head[1]
        possible_directions = []

        if dx > 0:
            possible_directions.append(RIGHT)
        elif dx < 0:
            possible_directions.append(LEFT)
        if dy > 0:
            possible_directions.append(DOWN)
        elif dy < 0:
            possible_directions.append(UP)

        # Choose one of the preferred directions at random, if available.
        chosen = random.choice(possible_directions) if possible_directions else self.direction

        # Check if the move would cause a collision
        new_head = ((head[0] + chosen[0]) % GRID_WIDTH, (head[1] + chosen[1]) % GRID_HEIGHT)
        if self.is_collision(new_head, all_snakes):
            # Try an alternate safe direction
            alternatives = [UP, DOWN, LEFT, RIGHT]
            random.shuffle(alternatives)
            for alt in alternatives:
                new_head_alt = ((head[0] + alt[0]) % GRID_WIDTH, (head[1] + alt[1]) % GRID_HEIGHT)
                if not self.is_collision(new_head_alt, all_snakes):
                    chosen = alt
                    break
        self.set_direction(chosen)

    def is_collision(self, pos, all_snakes):
        # Check self-collision
        if pos in self.positions:
            return True
        # Check collision with any other snake’s segments
        for snake in all_snakes:
            if snake is not self and pos in snake.positions:
                return True
        return False

# ----- Food Class -----
class Food:
    def __init__(self):
        self.position = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))

    def draw(self, surface):
        rect = pygame.Rect(self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, YELLOW, rect)

    def respawn(self, snakes):
        """Ensure food doesn't spawn on any snake."""
        while True:
            pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
            if not any(pos in snake.positions for snake in snakes):
                self.position = pos
                break

# ----- Main Game Loop -----
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    # Create multiple snakes with distinct colors
    snakes = [Snake(RED), Snake(BLUE), Snake(PURPLE)]
    food = Food()

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Each snake makes its decision and moves
        for snake in snakes:
            if snake.alive:
                snake.decide_direction(food.position, snakes)
                # Determine if the snake is about to eat food
                head = snake.get_head()
                new_head = ((head[0] + snake.direction[0]) % GRID_WIDTH,
                            (head[1] + snake.direction[1]) % GRID_HEIGHT)
                grow = (new_head == food.position)
                snake.move(grow)
                if grow:
                    food.respawn(snakes)

        # Check for collisions: if a snake's head touches any body segment (its own or another's), it dies
        for snake in snakes:
            if not snake.alive:
                continue
            head = snake.get_head()
            for other in snakes:
                segments = other.positions if other != snake else other.positions[1:]
                if head in segments:
                    snake.alive = False
                    break

        # End the game when all snakes are dead
        if not any(snake.alive for snake in snakes):
            running = False

        # Drawing
        screen.fill(BLACK)
        food.draw(screen)
        for snake in snakes:
            if snake.alive:
                snake.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
