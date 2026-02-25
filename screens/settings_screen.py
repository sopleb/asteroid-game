import pygame


RESOLUTIONS = [
    [1280, 720],
    [1920, 1080],
    [2560, 1440],
]

BG_TRACKS = ["bg1", "bg2", "bg3"]


class SettingsScreen:
    def __init__(self, app):
        self.app = app
        self.title_font = pygame.font.Font(None, 72)
        self.item_font = pygame.font.Font(None, 42)
        self.hint_font = pygame.font.Font(None, 30)

        self.items = ["Resolution", "BG Track", "SFX Volume", "Music Volume", "Back"]
        self.selected = 0

    def _get_value_text(self, item):
        s = self.app.settings
        if item == "Resolution":
            return f"{s['resolution'][0]}x{s['resolution'][1]}"
        elif item == "BG Track":
            return s["bg_track"]
        elif item == "SFX Volume":
            return f"{int(s['sfx_volume'] * 100)}%"
        elif item == "Music Volume":
            return f"{int(s['music_volume'] * 100)}%"
        return ""

    def _adjust(self, direction):
        s = self.app.settings
        item = self.items[self.selected]

        if item == "Resolution":
            idx = RESOLUTIONS.index(s["resolution"]) if s["resolution"] in RESOLUTIONS else 0
            idx = max(0, min(len(RESOLUTIONS) - 1, idx + direction))
            s["resolution"] = RESOLUTIONS[idx]
            self.app.apply_resolution_live()

        elif item == "BG Track":
            idx = BG_TRACKS.index(s["bg_track"]) if s["bg_track"] in BG_TRACKS else 0
            idx = max(0, min(len(BG_TRACKS) - 1, idx + direction))
            s["bg_track"] = BG_TRACKS[idx]
            self.app.switch_music(s["bg_track"])

        elif item == "SFX Volume":
            vol = round(s["sfx_volume"] + direction * 0.1, 2)
            s["sfx_volume"] = max(0.0, min(1.0, vol))

        elif item == "Music Volume":
            vol = round(s["music_volume"] + direction * 0.1, 2)
            s["music_volume"] = max(0.0, min(1.0, vol))
            pygame.mixer.music.set_volume(s["music_volume"])

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.items)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.items)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self._adjust(-1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self._adjust(1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.items[self.selected] == "Back":
                    self.app.save_settings()
                    return ("switch", "title")
            elif event.key == pygame.K_ESCAPE:
                self.app.save_settings()
                return ("switch", "title")
        return None

    def update(self, dt):
        return None

    def draw(self, surface):
        surface.fill("black")
        w, h = surface.get_size()

        title = self.title_font.render("SETTINGS", True, "white")
        surface.blit(title, title.get_rect(center=(w // 2, 80)))

        start_y = 180
        for i, item in enumerate(self.items):
            is_sel = i == self.selected
            color = (255, 255, 0) if is_sel else (255, 255, 255)

            label = self.item_font.render(item, True, color)
            value_text = self._get_value_text(item)

            if value_text:
                val = self.item_font.render(value_text, True, color)
                label_rect = label.get_rect(midleft=(w // 2 - 200, start_y + i * 60))
                val_rect = val.get_rect(midright=(w // 2 + 200, start_y + i * 60))
                surface.blit(label, label_rect)
                surface.blit(val, val_rect)

                # little arrows around the value when it's selected
                if is_sel:
                    arrow_l = self.item_font.render("<", True, color)
                    arrow_r = self.item_font.render(">", True, color)
                    surface.blit(arrow_l, arrow_l.get_rect(midright=(val_rect.left - 10, val_rect.centery)))
                    surface.blit(arrow_r, arrow_r.get_rect(midleft=(val_rect.right + 10, val_rect.centery)))
            else:
                # "Back" has no value, just center it
                surface.blit(label, label.get_rect(center=(w // 2, start_y + i * 60)))

        hint = self.hint_font.render("Up/Down: navigate   Left/Right: adjust   Esc: back", True, (128, 128, 128))
        surface.blit(hint, hint.get_rect(center=(w // 2, h - 40)))
