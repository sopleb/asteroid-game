import pygame

import constants
from circleshape import CircleShape
from constants import LINE_WIDTH, SHOT_RADIUS


class Shot(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, SHOT_RADIUS)

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            "white",
            (int(self.position.x), int(self.position.y)),
            int(self.radius),
            LINE_WIDTH,
        )

    def update(self, dt):
        self.position += self.velocity * dt

        # shots don't wrap -- just remove them once they leave the screen
        if (self.position.x < -self.radius
                or self.position.x > constants.SCREEN_WIDTH + self.radius
                or self.position.y < -self.radius
                or self.position.y > constants.SCREEN_HEIGHT + self.radius):
            self.kill()
