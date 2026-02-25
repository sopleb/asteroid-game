import json
import os

import pygame

import constants
from screens.title import TitleScreen
from screens.settings_screen import SettingsScreen
from screens.game_screen import GameScreen
from screens.game_over import GameOverScreen

SETTINGS_FILE = "settings.json"

DEFAULTS = {
    "resolution": [1280, 720],
    "bg_track": "bg1",
    "sfx_volume": 0.3,
    "music_volume": 0.5,
}


class App:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.settings = self._load_settings()
        self._apply_resolution()

        self.screen = pygame.display.set_mode(
            (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
        )
        pygame.display.set_caption("Asteroids")
        self.clock = pygame.time.Clock()

        # title and settings stick around between screen switches,
        # game and game_over get recreated each time
        self._title = TitleScreen(self)
        self._settings = SettingsScreen(self)

        self.current_screen = self._title
        self._start_music()

    # --- settings ---

    def _load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE) as f:
                    saved = json.load(f)
                # layer saved on top of defaults so any new keys we add later
                # still have sane values
                return {**DEFAULTS, **saved}
            except Exception:
                pass
        return dict(DEFAULTS)

    def save_settings(self):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings, f, indent=2)

    # --- resolution ---

    def _apply_resolution(self):
        w, h = self.settings["resolution"]
        constants.SCREEN_WIDTH = w
        constants.SCREEN_HEIGHT = h

    def apply_resolution_live(self):
        self._apply_resolution()
        self.screen = pygame.display.set_mode(
            (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
        )

    # --- music ---

    def _start_music(self):
        track = self.settings["bg_track"]
        path = f"sounds/{track}.wav"
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.settings["music_volume"])
            pygame.mixer.music.play(-1)
        except Exception:
            print(f"Warning: Could not load {path}")

    def switch_music(self, track=None):
        if track:
            self.settings["bg_track"] = track
        self._start_music()

    # --- screens ---

    def switch_to(self, name, **kwargs):
        if name == "title":
            self.current_screen = self._title
        elif name == "settings":
            self.current_screen = self._settings
        elif name == "playing":
            self.current_screen = GameScreen(self)
        elif name == "game_over":
            self.current_screen = GameOverScreen(self, **kwargs)

    # --- main loop ---

    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

                result = self.current_screen.handle_event(event)
                if result and self._handle_transition(result):
                    return

            result = self.current_screen.update(dt)
            if result and self._handle_transition(result):
                return

            self.current_screen.draw(self.screen)
            pygame.display.flip()

    def _handle_transition(self, result):
        # returns True when the app should shut down
        action = result[0]
        if action == "quit":
            return True
        elif action == "switch":
            name = result[1]
            kwargs = result[2] if len(result) > 2 else {}
            self.switch_to(name, **kwargs)
        return False
