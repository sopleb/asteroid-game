import pygame

from constants import PLAYER_RADIUS, LINE_WIDTH, PLAYER_TURN_SPEED, PLAYER_MOVE_SPEED
from circleshape import CircleShape


class Player(CircleShape):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0

    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def draw(self, screen):
        pygame.draw.polygon(screen, "white", self.triangle(), LINE_WIDTH)

    def rotate(self, direction: float, dt: float):
        self.rotation += direction * PLAYER_TURN_SPEED * dt

    def move(self, dt: float):
        movement = pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_MOVE_SPEED * dt
        self.position += movement

    def update(self, dt: float):
        keys = pygame.key.get_pressed()

        turn = 0.0
        if keys[pygame.K_a]:
            turn -= 1.0
        if keys[pygame.K_d]:
            turn += 1.0
        if turn != 0.0:
            self.rotate(turn, dt)

        if keys[pygame.K_w]:
            self.move(dt)
        elif keys[pygame.K_s]:
            self.move(-dt)