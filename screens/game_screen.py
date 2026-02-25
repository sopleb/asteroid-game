import math
import pygame

import constants
from constants import (
    LINE_WIDTH,
    PLAYER_LIVES,
    ASTEROID_MIN_RADIUS,
    SCORE_SMALL_ASTEROID,
    SCORE_MEDIUM_ASTEROID,
    SCORE_LARGE_ASTEROID,
    POWERUP_SPAWN_CHANCE,
    SHIELD_DURATION,
    SPEED_BOOST_DURATION,
    SPEED_BOOST_MULTIPLIER,
    RAPID_FIRE_DURATION,
    RAPID_FIRE_MULTIPLIER,
)
from logger import log_state, log_event
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
from powerup import Powerup, PowerupType


class GameScreen:
    def __init__(self, app):
        self.app = app

        self.score = 0
        self.lives = PLAYER_LIVES
        self.respawn_countdown = 0
        self.player_invulnerable = False

        # powerup timers -- 0 means not active
        self.shield_timer = 0.0
        self.speed_boost_timer = 0.0
        self.rapid_fire_timer = 0.0

        self.font = pygame.font.Font(None, 36)
        self.countdown_font = pygame.font.Font(None, 72)

        self._load_sounds()
        self._init_sprites()

    def _load_sounds(self):
        sfx_vol = self.app.settings["sfx_volume"]
        self.bang_sound = self._load_sound("sounds/bangSmall.mp3", sfx_vol)
        self.shoot_sound = self._load_sound("sounds/fire.mp3", sfx_vol * 0.67)

    def _load_sound(self, path, volume):
        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(volume)
            return sound
        except Exception:
            print(f"Warning: Could not load {path}")
            return None

    def _init_sprites(self):
        self.updatable = pygame.sprite.Group()
        self.drawable = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.shots = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()

        # wire up containers so new instances auto-register into the right groups
        Player.containers = (self.updatable, self.drawable)
        Asteroid.containers = (self.asteroids, self.updatable, self.drawable)
        Shot.containers = (self.shots, self.updatable, self.drawable)
        AsteroidField.containers = (self.updatable,)
        Powerup.containers = (self.powerups, self.updatable, self.drawable)

        self.player = Player(constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT // 2)
        self.player.shoot_sound = self.shoot_sound
        AsteroidField()

    def handle_event(self, event):
        return None

    def update(self, dt):
        log_state()
        self._game_over = False
        self._update_timers(dt)
        self._check_collisions()
        if self._game_over:
            return ("switch", "game_over", {"score": self.score})
        return None

    def _update_timers(self, dt):
        # while respawning, freeze everything but keep counting down
        if self.respawn_countdown > 0:
            self.respawn_countdown -= dt
            if self.respawn_countdown <= 0:
                self.player.visible = True
                # don't strip invuln if the player has a shield going
                if self.shield_timer <= 0:
                    self.player_invulnerable = False
        else:
            self.updatable.update(dt)

        # tick down active powerup effects
        if self.shield_timer > 0:
            self.shield_timer -= dt
            if self.shield_timer <= 0:
                self.shield_timer = 0
                # careful not to remove invuln mid-respawn
                if self.respawn_countdown <= 0:
                    self.player_invulnerable = False

        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= dt
            if self.speed_boost_timer <= 0:
                self.speed_boost_timer = 0
                self.player.speed_multiplier = 1.0

        if self.rapid_fire_timer > 0:
            self.rapid_fire_timer -= dt
            if self.rapid_fire_timer <= 0:
                self.rapid_fire_timer = 0
                self.player.shoot_cooldown_multiplier = 1.0

    def _check_collisions(self):
        # only check player-asteroid hits when they're actually vulnerable
        if self.respawn_countdown <= 0 and not self.player_invulnerable:
            self._check_player_hit()
        if self.respawn_countdown <= 0:
            self._check_powerup_pickup()
        self._check_shot_hits()
        self._check_asteroid_bounces()

    def _check_player_hit(self):
        for asteroid in self.asteroids:
            if self.player.collides_with(asteroid):
                log_event("player_hit")
                self.lives -= 1

                if self.lives <= 0:
                    self._game_over = True
                    return

                # wipe the board clean for respawn
                for a in list(self.asteroids):
                    a.kill()
                for s in list(self.shots):
                    s.kill()
                for p in list(self.powerups):
                    p.kill()

                # kill any active powerup effects
                self.shield_timer = 0.0
                self.speed_boost_timer = 0.0
                self.rapid_fire_timer = 0.0
                self.player.speed_multiplier = 1.0
                self.player.shoot_cooldown_multiplier = 1.0

                # reset player to center and start the countdown
                self.player.position = pygame.Vector2(
                    constants.SCREEN_WIDTH / 2, constants.SCREEN_HEIGHT / 2
                )
                self.player.velocity = pygame.Vector2(0, 0)
                self.player.visible = False
                self.respawn_countdown = 3.0
                self.player_invulnerable = True
                break

    def _check_powerup_pickup(self):
        for powerup in list(self.powerups):
            if self.player.collides_with(powerup):
                self._apply_powerup(powerup)
                powerup.kill()

    def _apply_powerup(self, powerup):
        log_event("powerup_collected", kind=powerup.powerup_type)

        if powerup.powerup_type == PowerupType.EXTRA_LIFE:
            self.lives += 1
        elif powerup.powerup_type == PowerupType.SHIELD:
            self.shield_timer = SHIELD_DURATION
            self.player_invulnerable = True
        elif powerup.powerup_type == PowerupType.SPEED_BOOST:
            self.speed_boost_timer = SPEED_BOOST_DURATION
            self.player.speed_multiplier = SPEED_BOOST_MULTIPLIER
        elif powerup.powerup_type == PowerupType.RAPID_FIRE:
            self.rapid_fire_timer = RAPID_FIRE_DURATION
            self.player.shoot_cooldown_multiplier = RAPID_FIRE_MULTIPLIER

    def _check_shot_hits(self):
        for asteroid in self.asteroids:
            for shot in self.shots:
                if asteroid.collides_with(shot):
                    log_event("asteroid_shot")

                    # smaller rocks are harder to hit so they're worth more
                    if asteroid.radius <= ASTEROID_MIN_RADIUS:
                        self.score += SCORE_SMALL_ASTEROID
                    elif asteroid.radius <= ASTEROID_MIN_RADIUS * 2:
                        self.score += SCORE_MEDIUM_ASTEROID
                    else:
                        self.score += SCORE_LARGE_ASTEROID

                    spawn_x, spawn_y = asteroid.position.x, asteroid.position.y
                    asteroid.split()
                    shot.kill()

                    # stop then replay so rapid kills retrigger cleanly
                    if self.bang_sound:
                        self.bang_sound.stop()
                        self.bang_sound.play()

                    Powerup.maybe_spawn(spawn_x, spawn_y, POWERUP_SPAWN_CHANCE)
                    break

    def _check_asteroid_bounces(self):
        # asteroids bounce off each other by swapping velocities
        asteroid_list = list(self.asteroids)
        for i, a1 in enumerate(asteroid_list):
            for a2 in asteroid_list[i + 1:]:
                if a1.collides_with(a2):
                    a1.velocity, a2.velocity = a2.velocity, a1.velocity

    # --- drawing ---

    def _draw_lives(self, surface):
        # little ship icons in the top-left
        icon_r = 10
        spacing = 30
        base_x = 20
        base_y = 55
        fwd = pygame.Vector2(0, -1)
        right = pygame.Vector2(1, 0) * icon_r / 1.5

        for i in range(self.lives):
            center = pygame.Vector2(base_x + i * spacing, base_y)
            a = center + fwd * icon_r
            b = center - fwd * icon_r - right
            c = center - fwd * icon_r + right
            pygame.draw.polygon(surface, "white", [a, b, c], LINE_WIDTH)

    def _draw_shield_effect(self, surface):
        if self.shield_timer <= 0 or not self.player.visible:
            return
        cx, cy = int(self.player.position.x), int(self.player.position.y)
        pulse = 1.0 + 0.1 * math.sin(self.shield_timer * 6)
        r = int(self.player.radius * 1.8 * pulse)
        color = (60, 140, 255)

        # solid inner ring so the shield is always visible
        pygame.draw.circle(surface, color, (cx, cy), r, 2)

        # outer arc drains down as the shield runs out
        frac = self.shield_timer / SHIELD_DURATION
        arc_r = r + 4
        start = math.pi / 2
        rect = pygame.Rect(cx - arc_r, cy - arc_r, arc_r * 2, arc_r * 2)
        pygame.draw.arc(surface, color, rect, start, start + frac * 2 * math.pi, 2)

    def _draw_speed_effect(self, surface):
        if self.speed_boost_timer <= 0 or not self.player.visible:
            return
        cx, cy = int(self.player.position.x), int(self.player.position.y)
        color = (255, 220, 40)

        # little exhaust lines flickering behind the ship
        fwd = pygame.Vector2(0, 1).rotate(self.player.rotation)
        right = pygame.Vector2(0, 1).rotate(self.player.rotation + 90)
        for off in (-0.5, 0, 0.5):
            base = self.player.position - fwd * self.player.radius * 1.2 + right * off * self.player.radius
            wobble = 1.0 + 0.3 * math.sin(self.speed_boost_timer * 8 + off * 3)
            end = base - fwd * self.player.radius * wobble
            pygame.draw.line(surface, color, (int(base.x), int(base.y)), (int(end.x), int(end.y)), 2)

        # timer arc
        frac = self.speed_boost_timer / SPEED_BOOST_DURATION
        arc_r = int(self.player.radius * 1.5)
        start = math.pi / 2
        rect = pygame.Rect(cx - arc_r, cy - arc_r, arc_r * 2, arc_r * 2)
        pygame.draw.arc(surface, color, rect, start, start + frac * 2 * math.pi, 2)

    def _draw_rapid_fire_effect(self, surface):
        if self.rapid_fire_timer <= 0 or not self.player.visible:
            return
        cx, cy = int(self.player.position.x), int(self.player.position.y)
        color = (255, 60, 60)

        # just a draining arc -- keeps it clean and readable
        frac = self.rapid_fire_timer / RAPID_FIRE_DURATION
        arc_r = int(self.player.radius * 1.3)
        start = math.pi / 2
        rect = pygame.Rect(cx - arc_r, cy - arc_r, arc_r * 2, arc_r * 2)
        pygame.draw.arc(surface, color, rect, start, start + frac * 2 * math.pi, 2)

    def draw(self, surface):
        surface.fill("black")

        for obj in self.drawable:
            obj.draw(surface)

        # powerup effects draw on top of the player sprite
        self._draw_shield_effect(surface)
        self._draw_speed_effect(surface)
        self._draw_rapid_fire_effect(surface)

        score_text = self.font.render(f"Score: {self.score}", True, "white")
        surface.blit(score_text, (10, 10))
        self._draw_lives(surface)

        # big countdown number while waiting to respawn
        if self.respawn_countdown > 0:
            num = int(self.respawn_countdown) + 1
            text = self.countdown_font.render(str(num), True, "white")
            rect = text.get_rect(center=(constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT // 2))
            surface.blit(text, rect)

        return None
