import pygame

import constants


class CircleShape(pygame.sprite.Sprite):
    """Base class for anything that moves around the screen."""

    def __init__(self, x, y, radius):
        # auto-add to sprite groups if the subclass set them up
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()

        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius

    def _wrap_position(self):
        # teleport to the opposite edge when we go off-screen
        # uses radius as buffer so we don't pop in/out visibly
        if self.position.x < -self.radius:
            self.position.x = constants.SCREEN_WIDTH + self.radius
        elif self.position.x > constants.SCREEN_WIDTH + self.radius:
            self.position.x = -self.radius

        if self.position.y < -self.radius:
            self.position.y = constants.SCREEN_HEIGHT + self.radius
        elif self.position.y > constants.SCREEN_HEIGHT + self.radius:
            self.position.y = -self.radius

    def collides_with(self, other) -> bool:
        # simple circle-circle overlap check
        distance = self.position.distance_to(other.position)
        return distance <= (self.radius + other.radius)

    def draw(self, screen):
        pass

    def update(self, dt):
        self._wrap_position()
