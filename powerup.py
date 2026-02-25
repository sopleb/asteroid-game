import math
import random

import pygame

from circleshape import CircleShape
from constants import POWERUP_RADIUS, POWERUP_LIFETIME, POWERUP_BLINK_TIME


class PowerupType:
    EXTRA_LIFE = "extra_life"
    SHIELD = "shield"
    SPEED_BOOST = "speed_boost"
    RAPID_FIRE = "rapid_fire"


# each type gets a distinct color so the player can tell them apart at a glance
POWERUP_COLORS = {
    PowerupType.EXTRA_LIFE: (0, 220, 80),     # green
    PowerupType.SHIELD: (60, 140, 255),        # blue
    PowerupType.SPEED_BOOST: (255, 220, 40),   # yellow
    PowerupType.RAPID_FIRE: (255, 60, 60),     # red
}


class Powerup(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, POWERUP_RADIUS)
        self.powerup_type = random.choice([
            PowerupType.EXTRA_LIFE,
            PowerupType.SHIELD,
            PowerupType.SPEED_BOOST,
            PowerupType.RAPID_FIRE,
        ])
        self.color = POWERUP_COLORS[self.powerup_type]
        self.age = 0.0

        # give it a slow random drift so it's not just sitting there
        angle = random.uniform(0, 360)
        speed = random.uniform(15, 35)
        self.velocity = pygame.Vector2(0, 1).rotate(angle) * speed

    def draw(self, screen):
        remaining = POWERUP_LIFETIME - self.age

        # blink on/off in the last couple seconds as a warning
        if remaining < POWERUP_BLINK_TIME:
            freq = 8 + (POWERUP_BLINK_TIME - remaining) * 6
            if math.sin(self.age * freq) < 0:
                return

        # gentle breathing effect
        pulse = 1.0 + 0.15 * math.sin(self.age * 4)
        r = int(self.radius * pulse)
        cx, cy = int(self.position.x), int(self.position.y)

        # timer arc around the outside -- sweeps from full circle down to nothing
        fraction = remaining / POWERUP_LIFETIME
        if fraction > 0:
            arc_r = r + 6
            start = math.pi / 2
            rect = pygame.Rect(cx - arc_r, cy - arc_r, arc_r * 2, arc_r * 2)
            dim = tuple(c // 2 for c in self.color)
            pygame.draw.arc(screen, dim, rect, start, start + fraction * 2 * math.pi, 2)

        # thin outer glow
        pygame.draw.circle(screen, self.color, (cx, cy), r + 3, 1)

        # now draw the actual icon depending on type
        if self.powerup_type == PowerupType.EXTRA_LIFE:
            # plus sign
            pygame.draw.circle(screen, self.color, (cx, cy), r, 2)
            h = r // 2
            pygame.draw.line(screen, self.color, (cx - h, cy), (cx + h, cy), 2)
            pygame.draw.line(screen, self.color, (cx, cy - h), (cx, cy + h), 2)

        elif self.powerup_type == PowerupType.SHIELD:
            # two concentric rings
            pygame.draw.circle(screen, self.color, (cx, cy), r, 2)
            pygame.draw.circle(screen, self.color, (cx, cy), r - 4, 2)

        elif self.powerup_type == PowerupType.SPEED_BOOST:
            # double chevron pointing up
            pygame.draw.circle(screen, self.color, (cx, cy), r, 2)
            h = r // 2
            pygame.draw.lines(screen, self.color, False, [
                (cx - h, cy + 2), (cx, cy - h), (cx + h, cy + 2),
            ], 2)
            pygame.draw.lines(screen, self.color, False, [
                (cx - h, cy + h), (cx, cy), (cx + h, cy + h),
            ], 2)

        elif self.powerup_type == PowerupType.RAPID_FIRE:
            # crosshair
            pygame.draw.circle(screen, self.color, (cx, cy), r, 2)
            h = r - 2
            pygame.draw.line(screen, self.color, (cx - h, cy), (cx + h, cy), 2)
            pygame.draw.line(screen, self.color, (cx, cy - h), (cx, cy + h), 2)
            pygame.draw.circle(screen, self.color, (cx, cy), h // 2, 1)

    def update(self, dt):
        self.position += self.velocity * dt
        self.age += dt

        # despawn after the lifetime runs out
        if self.age >= POWERUP_LIFETIME:
            self.kill()
            return

        super().update(dt)

    @staticmethod
    def maybe_spawn(x, y, chance):
        # roll the dice -- only some asteroid kills drop a powerup
        if random.random() < chance:
            Powerup(x, y)
