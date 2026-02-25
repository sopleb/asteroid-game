# Asteroids

A classic asteroids clone built with pygame. Shoot rocks, dodge debris, chase high scores.

## How to play

```
uv run python main.py
```

**Controls:**

| Action | Keys |
|--------|------|
| Turn | A/D or Left/Right |
| Thrust | W/S or Up/Down |
| Shoot | Space |

Menus use the same keys -- WASD or arrows to navigate, Space or Enter to confirm.

## What's in the game

- Asteroids that split into smaller chunks when you shoot them
- Powerups that drop from destroyed asteroids (shield, speed boost, rapid fire, extra life)
- Screen wrapping for the ship and asteroids
- Respawn countdown with invulnerability after getting hit
- 3 background music tracks you can swap in settings
- Resolution and volume settings that persist between sessions
- Online leaderboard via dreamlo -- enter your name after dying and see how you stack up

## Project structure

```
main.py              entry point
app.py               owns the display, clock, settings, and screen transitions
constants.py         all the tunable numbers in one place
screens/
  title.py           title screen with drifting background asteroids
  settings_screen.py resolution, music track, volume sliders
  game_screen.py     the actual gameplay (refactored from the old Game class)
  game_over.py       score display, name entry, leaderboard
player.py            ship with triangle collision detection
asteroid.py          jagged rocks that split and bounce
asteroidfield.py     spawns asteroids from screen edges
shot.py              bullets that fly straight and despawn off-screen
powerup.py           random drops with blink-before-despawn
circleshape.py       base class for anything round that wraps around the screen
leaderboard.py       dreamlo API wrapper (private key is lightly obfuscated)
logger.py            frame state and event logging for debugging
```

## Requirements

- Python 3.12+
- pygame (installed via uv)
