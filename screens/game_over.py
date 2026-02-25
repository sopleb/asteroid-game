import threading

import pygame

import leaderboard


class GameOverScreen:
    def __init__(self, app, score=0):
        self.app = app
        self.score = score

        self.title_font = pygame.font.Font(None, 80)
        self.score_font = pygame.font.Font(None, 60)
        self.font = pygame.font.Font(None, 42)
        self.small_font = pygame.font.Font(None, 32)

        # name entry
        self.name = ""
        self.max_name_len = 10
        self.submitted = False

        # post-submit menu
        self.menu_items = ["Play Again", "Main Menu"]
        self.menu_selected = 0

        # leaderboard -- fetched in the background so we don't freeze
        self.lb_entries = None
        self.lb_error = None
        self.lb_loading = True
        self._fetch_leaderboard()

    def _fetch_leaderboard(self):
        self.lb_loading = True
        self.lb_entries = None
        self.lb_error = None
        leaderboard.fetch_leaderboard_async(self._on_leaderboard)

    def _on_leaderboard(self, entries, error):
        # runs on a background thread -- just stash the results and let
        # draw() pick them up next frame
        if error:
            self.lb_error = error
        else:
            self.lb_entries = entries
        self.lb_loading = False

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None

        if not self.submitted:
            return self._handle_name_entry(event)
        return self._handle_menu(event)

    def _handle_name_entry(self, event):
        if event.key in (pygame.K_RETURN, pygame.K_SPACE) and self.name:
            self.submitted = True
            self._submit_score()
            return None
        elif event.key == pygame.K_BACKSPACE:
            self.name = self.name[:-1]
        else:
            ch = event.unicode
            # block * and / -- dreamlo uses them as URL delimiters
            if ch.isalnum() and ch != "*" and len(self.name) < self.max_name_len:
                self.name += ch.upper()
        return None

    def _submit_score(self):
        def _do():
            try:
                leaderboard.submit_score(self.name, self.score)
            except Exception:
                pass  # not much we can do -- leaderboard will still show old data
            self._fetch_leaderboard()

        threading.Thread(target=_do, daemon=True).start()

    def _handle_menu(self, event):
        if event.key in (pygame.K_UP, pygame.K_w):
            self.menu_selected = (self.menu_selected - 1) % len(self.menu_items)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.menu_selected = (self.menu_selected + 1) % len(self.menu_items)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            choice = self.menu_items[self.menu_selected]
            if choice == "Play Again":
                return ("switch", "playing")
            elif choice == "Main Menu":
                return ("switch", "title")
        return None

    def update(self, dt):
        return None

    def draw(self, surface):
        surface.fill("black")
        w, h = surface.get_size()

        # score + name entry on the left third, leaderboard on the right
        left_cx = w // 3

        title = self.title_font.render("GAME OVER", True, "white")
        surface.blit(title, title.get_rect(center=(left_cx, 80)))

        score_text = self.score_font.render(f"Score: {self.score}", True, "white")
        surface.blit(score_text, score_text.get_rect(center=(left_cx, 160)))

        if not self.submitted:
            self._draw_name_entry(surface, left_cx)
        else:
            self._draw_menu(surface, left_cx)

        self._draw_leaderboard(surface, w * 2 // 3)

    def _draw_name_entry(self, surface, cx):
        prompt = self.font.render("Enter your name:", True, "white")
        surface.blit(prompt, prompt.get_rect(center=(cx, 260)))

        name_text = self.score_font.render(self.name + "_", True, (255, 255, 0))
        surface.blit(name_text, name_text.get_rect(center=(cx, 330)))

        hint = self.small_font.render("Press ENTER or SPACE to submit", True, (128, 128, 128))
        surface.blit(hint, hint.get_rect(center=(cx, 400)))

    def _draw_menu(self, surface, cx):
        start_y = 280
        for i, item in enumerate(self.menu_items):
            color = (255, 255, 0) if i == self.menu_selected else (255, 255, 255)
            text = self.font.render(item, True, color)
            surface.blit(text, text.get_rect(center=(cx, start_y + i * 60)))

    def _draw_leaderboard(self, surface, cx):
        header = self.font.render("TOP SCORES", True, "white")
        surface.blit(header, header.get_rect(center=(cx, 80)))

        y = 130
        if self.lb_loading:
            msg = self.small_font.render("Loading...", True, (128, 128, 128))
            surface.blit(msg, msg.get_rect(center=(cx, y)))
        elif self.lb_error:
            msg = self.small_font.render("Could not load leaderboard", True, (200, 80, 80))
            surface.blit(msg, msg.get_rect(center=(cx, y)))
        elif self.lb_entries:
            for i, entry in enumerate(self.lb_entries[:10]):
                line = f"{i + 1:>2}. {entry['name']:<12} {entry['score']:>8}"
                text = self.small_font.render(line, True, "white")
                surface.blit(text, text.get_rect(center=(cx, y + i * 35)))
        else:
            msg = self.small_font.render("No scores yet", True, (128, 128, 128))
            surface.blit(msg, msg.get_rect(center=(cx, y)))
