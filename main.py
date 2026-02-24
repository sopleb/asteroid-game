import pygame

from constants import *
from logger import log_state
from player import Player

def main():
    pygame.init()
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen height: {SCREEN_HEIGHT}")
    print(f"Screen width: {SCREEN_WIDTH}")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    player = Player(int(SCREEN_WIDTH / 2), int(SCREEN_HEIGHT / 2))

    clock = pygame.time.Clock()
    dt = 0

    while True:
        log_state()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            pass

        screen.fill("black")
        player.draw(screen)
        pygame.display.flip()

        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()