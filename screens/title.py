import random

import pygame

import constants
from constants import LINE_WIDTH, ASTEROID_MIN_RADIUS, ASTEROID_KINDS


class _BgAsteroid:
    """Dumb decorative asteroid -- no sprite groups, just drifts and wraps."""

    def __init__(self, w, h):
        self.radius = ASTEROID_MIN_RADIUS * random.randint(1, ASTEROID_KINDS)
        self.position = pygame.Vector2(random.uniform(0, w), random.uniform(0, h))
        angle = random.uniform(0, 360)
        speed = random.uniform(20, 60)
        self.velocity = pygame.Vector2(0, 1).rotate(angle) * speed
        self.rotation_speed = random.uniform(-30, 30)
        self.rotation = random.uniform(0, 360)

        # same jagged shape logic as the real Asteroid class
        num_verts = random.randint(8, 12)
        self.vertices = []
        for i in range(num_verts):
            a = (360 / num_verts) * i
            jitter = self.radius * random.uniform(0.7, 1.3)
            self.vertices.append(pygame.Vector2(0, jitter).rotate(a))

    def update(self, dt, w, h):
        self.position += self.velocity * dt
        self.rotation += self.rotation_speed * dt

        if self.position.x < -self.radius:
            self.position.x = w + self.radius
        elif self.position.x > w + self.radius:
            self.position.x = -self.radius
        if self.position.y < -self.radius:
            self.position.y = h + self.radius
        elif self.position.y > h + self.radius:
            self.position.y = -self.radius

    def draw(self, surface):
        # rotate vertices around center
        rot = pygame.Vector2(0, 1).rotate(self.rotation)
        cos, sin = rot.y, rot.x
        points = []
        for v in self.vertices:
            rx = v.x * cos - v.y * sin
            ry = v.x * sin + v.y * cos
            points.append((self.position.x + rx, self.position.y + ry))
        pygame.draw.polygon(surface, "white", points, LINE_WIDTH)


class TitleScreen:
    def __init__(self, app):
        self.app = app
        self.title_font = pygame.font.Font(None, 120)
        self.menu_font = pygame.font.Font(None, 48)
        self.items = ["Play", "Settings", "Quit"]
        self.selected = 0

        self._bg_asteroids = self._spawn_bg_asteroids()
        self._overlay = None

    def _spawn_bg_asteroids(self):
        w, h = constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT
        # more rocks at higher resolutions so it doesn't look empty
        count = max(8, (w * h) // 80000)
        return [_BgAsteroid(w, h) for _ in range(count)]

    def _get_overlay(self, w, h):
        # cached dark tint -- keeps the menu readable over the asteroids
        if self._overlay is None or self._overlay.get_size() != (w, h):
            self._overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            self._overlay.fill((0, 0, 0, 160))
        return self._overlay

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.items)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.items)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                choice = self.items[self.selected]
                if choice == "Play":
                    return ("switch", "playing")
                elif choice == "Settings":
                    return ("switch", "settings")
                elif choice == "Quit":
                    return ("quit",)
        return None

    def update(self, dt):
        w, h = constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT
        for a in self._bg_asteroids:
            a.update(dt, w, h)
        return None

    def draw(self, surface):
        surface.fill("black")
        w, h = surface.get_size()

        for a in self._bg_asteroids:
            a.draw(surface)

        # dark overlay so the text pops
        surface.blit(self._get_overlay(w, h), (0, 0))

        title = self.title_font.render("ASTEROIDS", True, "white")
        surface.blit(title, title.get_rect(center=(w // 2, h // 4)))

        start_y = h // 2
        for i, item in enumerate(self.items):
            color = (255, 255, 0) if i == self.selected else (255, 255, 255)
            text = self.menu_font.render(item, True, color)
            surface.blit(text, text.get_rect(center=(w // 2, start_y + i * 60)))
