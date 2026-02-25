import math

import pygame

from constants import (
    PLAYER_RADIUS,
    LINE_WIDTH,
    PLAYER_TURN_SPEED,
    PLAYER_MOVE_SPEED,
    PLAYER_SHOOT_SPEED,
    PLAYER_SHOOT_COOLDOWN_SECONDS,
)
from circleshape import CircleShape
from shot import Shot


class Player(CircleShape):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shoot_timer = 0.0
        self.visible = True

        # powerup modifiers -- these get reset when effects expire
        self.speed_multiplier = 1.0
        self.shoot_cooldown_multiplier = 1.0

    def triangle(self):
        # build the three vertices of the ship relative to its position/rotation
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def draw(self, screen):
        if not self.visible:
            return
        pygame.draw.polygon(screen, "white", self.triangle(), LINE_WIDTH)

    # --- collision: triangle vs circle ---
    # the base class does circle-circle, but our ship is a triangle so we
    # need a proper check. test if the other circle's center is inside our
    # triangle OR if it's close enough to any of the three edges.

    def collides_with(self, other) -> bool:
        tri = self.triangle()
        center = other.position
        r = other.radius

        if self._point_in_triangle(center, tri[0], tri[1], tri[2]):
            return True

        for i in range(3):
            if self._point_segment_distance(center, tri[i], tri[(i + 1) % 3]) <= r:
                return True

        return False

    @staticmethod
    def _point_in_triangle(p, a, b, c) -> bool:
        # uses the cross product sign trick -- if the point is on the same
        # side of all three edges, it's inside the triangle
        def cross(o, v1, v2):
            return (v1.x - o.x) * (v2.y - o.y) - (v1.y - o.y) * (v2.x - o.x)

        d1 = cross(p, a, b)
        d2 = cross(p, b, c)
        d3 = cross(p, c, a)

        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
        return not (has_neg and has_pos)

    @staticmethod
    def _point_segment_distance(p, a, b) -> float:
        # project p onto the line segment ab, clamp to [0,1], measure distance
        ab = b - a
        ap = p - a
        len_sq = ab.x * ab.x + ab.y * ab.y
        if len_sq == 0:
            return p.distance_to(a)
        t = max(0, min(1, (ap.x * ab.x + ap.y * ab.y) / len_sq))
        proj = a + ab * t
        return p.distance_to(proj)

    def rotate(self, direction: float, dt: float):
        self.rotation += direction * PLAYER_TURN_SPEED * dt

    def move(self, dt: float):
        speed = PLAYER_MOVE_SPEED * self.speed_multiplier
        movement = pygame.Vector2(0, 1).rotate(self.rotation) * speed * dt
        self.position += movement

    def shoot(self):
        if self.shoot_timer > 0:
            return

        self.shoot_timer = PLAYER_SHOOT_COOLDOWN_SECONDS * self.shoot_cooldown_multiplier
        shot = Shot(self.position.x, self.position.y)
        shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOOT_SPEED

        if hasattr(self, 'shoot_sound') and self.shoot_sound:
            self.shoot_sound.play()

    def update(self, dt: float):
        self.shoot_timer = max(0.0, self.shoot_timer - dt)

        keys = pygame.key.get_pressed()

        # turning -- A/D or Left/Right
        turn = 0.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            turn -= 1.0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            turn += 1.0
        if turn != 0.0:
            self.rotate(turn, dt)

        # thrust -- W/S or Up/Down
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.move(dt)
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.move(-dt)

        if keys[pygame.K_SPACE]:
            self.shoot()

        super().update(dt)
