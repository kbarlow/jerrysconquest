
# Jerry's Conquest

## Overview
Jerry's Conquest is a modern 2D action RPG (ARPG) built in Python using pygame. Explore an infinite, procedurally generated world, battle monsters, and master sword and disc combat in a visually rich, highly interactive environment.

---

## Features

- **Procedural Infinite Terrain:**
  - The world is generated on-the-fly as you explore, with seamless chunk loading and a variety of grass and water tile variants for a natural look.
- **Smooth Player Movement & Camera:**
  - Responsive controls and a camera system that keeps the player centered, ensuring all movement and collisions are visually and logically in sync.
- **Combat System:**
  - Use sword and disc attacks to defeat monsters. The disc can be thrown in any direction and returns to the player, defeating orbs and monsters in its path.
- **Enemy AI:**
  - Monsters spawn randomly and shoot orbs at the player. Orbs track the player and disappear on hit, reducing health.
- **Modern Health Bar:**
  - A stylish ARPG-style health bar is displayed at the bottom left. Each orb hit reduces health by 10%. Game over triggers at 0%.
- **Pixel-Perfect Collision:**
  - All collisions (player, orbs, disc, monsters) use carefully tuned hitboxes for fair, visually accurate gameplay.
- **Visual Polish:**
  - Animated player and monster sprites, blood overlays on enemy defeat, splash screen, and multiple tile variants for a lively world.
- **Debugging & Dev Tools:**
  - Toggleable debug logging, centralized position logic, and robust error handling for smooth development.

---

## Setup Instructions

### 1. Prerequisites
* Python 3.12 or later
* pip (Python package manager)

### 2. Install Dependencies
From the project root directory, run:

```bash
pip install -r requirements.txt
```

This will install `pygame` and any other required packages.

### 3. Run the Game
From the project root directory, run:

```bash
python main.py
```

The game window should open. Use the controls below to play.

---

## How to Play

1. Run `main.py` to start the game.
2. Press Enter or Space to begin from the splash screen.
3. Move with arrow keys or WASD. Explore the world, avoid water, and fight monsters.
4. Use X to throw your disc. The disc returns automatically and can defeat monsters and orbs.
5. Survive as long as possible! Each orb hit reduces your health. When health reaches zero, it's game over.

---

## Controls

- **Movement:** Arrow keys or WASD
- **Throw Disc:** X
- **Start Game:** Enter or Space (on splash screen)

The disc can be thrown in any direction, including diagonals. Sword attacks are directional and context-sensitive.

---

## Assets

All art and sound assets are located in the `assets/` folder:

- **Sprites:**
  - `Player.png`, `Player2.png`: Animated player frames
  - `monster1.png`, `monster2.png`: Animated monster frames
  - `disc.png`: Player's disc projectile
  - `orb.png`: Enemy orb projectile
  - `blood.png`: Blood overlay for defeated enemies
- **Tiles:**
  - `grass.png`, `grass1.png`, `grass2.png`: Grass tile variants
  - `water.png`, `water1.png`, `water2.png`: Water tile variants
- **Audio:**
  - (If present) All sound effects and music are in `assets/audio/`

---

## Development & Testing

- All main game logic is in `main.py` and the `src/` folder.
- Tests are in the `tests/` directory. Run them with your preferred Python test runner.
- To add new features, see the modular structure in `src/` and follow the existing code style.

---

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change. See `CONTRIBUTING.md` for guidelines on submitting issues and pull requests.

- Please keep code clean and well-documented.
- Add or update tests in the `tests/` folder as needed.
- Art and sound contributions are welcome—see `ASSETS.md` for asset guidelines.

---

## Notes

This project was developed with the help of GitHub Copilot, an AI programming assistant, for code, documentation, and troubleshooting support.

---

## License
MIT License (see LICENSE file if present)
