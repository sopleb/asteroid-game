import random

import pygame

from circleshape import CircleShape
from constants import LINE_WIDTH, ASTEROID_MIN_RADIUS
from logger import log_event


class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.vertices = self._generate_jagged_shape()

    def _generate_jagged_shape(self):
        # each asteroid gets a unique rocky outline by randomizing
        # the distance of each vertex from center
        num_vertices = random.randint(8, 12)
        vertices = []

        for i in range(num_vertices):
            angle = (360 / num_vertices) * i
            jitter = self.radius * random.uniform(0.7, 1.3)
            offset = pygame.Vector2(0, jitter).rotate(angle)
            vertices.append(offset)

        return vertices

    def draw(self, screen):
        points = [self.position + v for v in self.vertices]
        pygame.draw.polygon(screen, "white", points, LINE_WIDTH)

    def update(self, dt):
        self.position += self.velocity * dt
        super().update(dt)

    def split(self):
        self.kill()

        # smallest asteroids just die
        if self.radius <= ASTEROID_MIN_RADIUS:
            return

        log_event("asteroid_split")

        # break into two smaller rocks flying off at random angles
        angle = random.uniform(20, 50)
        v1 = self.velocity.rotate(angle)
        v2 = self.velocity.rotate(-angle)

        new_radius = self.radius - ASTEROID_MIN_RADIUS

        # nudge them apart so they don't instantly collide with each other
        nudge = new_radius * 0.8
        offset1 = pygame.Vector2(0, nudge).rotate(angle)
        offset2 = pygame.Vector2(0, nudge).rotate(-angle)

        a1 = Asteroid(self.position.x + offset1.x, self.position.y + offset1.y, new_radius)
        a1.velocity = v1 * 1.2

        a2 = Asteroid(self.position.x + offset2.x, self.position.y + offset2.y, new_radius)
        a2.velocity = v2 * 1.2
