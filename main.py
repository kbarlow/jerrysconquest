# filepath: jerrysconquest/main.py

import sys
import os
import pygame
from src.player import Player
from src.world import World, TILE_GRASS, TILE_WATER
from src.enemy import Enemy

class SwordProjectile:
    """
    Represents a disc projectile thrown by the player. Moves in a direction, then returns to the player.
    """
    TILE_SIZE: int = 32

    def __init__(self, wx: int, wy: int, direction: str, max_range: int = 4):
        self.wx: int = wx
        self.wy: int = wy
        self.direction: str = direction
        self.range_left: int = max_range
        self.active: bool = True
        self.move_cooldown: int = 3  # frames between moves
        self.move_timer: int = 0
        self.returning: bool = False
        self.player_ref: 'Player | None' = None  # Will be set when appended
        # Use disc.png for all sword projectiles
        base_dir = os.path.dirname(os.path.abspath(__file__))
        sprite_path = os.path.join(base_dir, 'assets', 'sprites', 'disc.png')
        if os.path.exists(sprite_path):
            img = pygame.image.load(sprite_path).convert_alpha()
            self.image = pygame.transform.smoothscale(img, (self.TILE_SIZE, self.TILE_SIZE))
        else:
            self.image = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE), pygame.SRCALPHA)
            self.image.fill((220, 220, 80))
        self.rect = pygame.Rect(0, 0, self.TILE_SIZE, self.TILE_SIZE)

    def move(self) -> None:
        """Move the projectile in its direction or return to the player."""
        if self.move_timer > 0:
            self.move_timer -= 1
            return
        self.move_timer = self.move_cooldown
        if not self.returning:
            if self.direction == 'right':
                self.wx += 1
            elif self.direction == 'left':
                self.wx -= 1
            elif self.direction == 'up':
                self.wy -= 1
            elif self.direction == 'down':
                self.wy += 1
            self.range_left -= 1
            if self.range_left <= 0:
                self.returning = True
        else:
            # Home back to player tile
            if self.player_ref is not None:
                px = int(self.player_ref.x // self.TILE_SIZE)
                py = int(self.player_ref.y // self.TILE_SIZE)
                dx = px - self.wx
                dy = py - self.wy
                if dx == 0 and dy == 0:
                    self.active = False
                    return
                # Move one step toward player (prioritize x if not zero)
                if abs(dx) > abs(dy):
                    self.wx += 1 if dx > 0 else -1
                elif dy != 0:
                    self.wy += 1 if dy > 0 else -1
                else:
                    self.wx += 1 if dx > 0 else -1

    def draw(self, surface: pygame.Surface, tile_offset_x: int, tile_offset_y: int, screen: pygame.Surface) -> None:
        """Draw the projectile on the screen if in view."""
        sx = (self.wx - tile_offset_x) * self.TILE_SIZE
        sy = (self.wy - tile_offset_y) * self.TILE_SIZE
        if 0 <= sx < screen.get_width() and 0 <= sy < screen.get_height():
            surface.blit(self.image, (sx, sy))


class Blood:
    """
    Represents a blood overlay left behind when an enemy is defeated.
    """
    TILE_SIZE: int = 32

    def __init__(self, wx: int, wy: int):
        self.wx: int = wx
        self.wy: int = wy
        # Use project root as base directory
        project_root = os.path.dirname(os.path.abspath(__file__))
        sprite_path = os.path.join(project_root, 'assets', 'sprites', 'blood.png')
        print(f"[DEBUG] Looking for blood.png at: {sprite_path}")
        if os.path.exists(sprite_path):
            print("[DEBUG] blood.png found.")
            try:
                img = pygame.image.load(sprite_path).convert_alpha()
                self.image = pygame.transform.smoothscale(img, (self.TILE_SIZE, self.TILE_SIZE))
            except Exception as e:
                print(f"[WARNING] Failed to load blood.png: {e}")
                self.image = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE), pygame.SRCALPHA)
                self.image.fill((200, 0, 0))
        else:
            print("[WARNING] blood.png not found in assets/sprites! Using fallback red tile.")
            self.image = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE), pygame.SRCALPHA)
            self.image.fill((200, 0, 0))
        self.rect = self.image.get_rect()

    def draw(self, surface: pygame.Surface, screen_x: int, screen_y: int) -> None:
        """Draw the blood overlay at the given screen coordinates."""
        self.rect.topleft = (screen_x, screen_y)
        surface.blit(self.image, self.rect)


# Set new screen size
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jerry's Conquest")

# Splash screen
def show_splash():
    font_title = pygame.font.SysFont('Arial', 48, bold=True)
    font_sub = pygame.font.SysFont('Arial', 28)
    title = font_title.render("Jerry's Conquest", True, (255, 255, 0))
    sub = font_sub.render("Press Start", True, (255, 255, 255))
    # Draw vertical gradient of green shades
    for y in range(SCREEN_HEIGHT):
        # Interpolate between two greens
        t = y / SCREEN_HEIGHT
        r = int((40 * (1-t)) + (80 * t))
        g = int((120 * (1-t)) + (200 * t))
        b = int((60 * (1-t)) + (100 * t))
        pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    # Center text
    title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
    sub_rect = sub.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30))
    screen.blit(title, title_rect)
    screen.blit(sub, sub_rect)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    waiting = False
        pygame.time.wait(10)

show_splash()



# Set tile size before loading tiles
TILE_SIZE = 32

# Load tile variations for grass and water
def load_tile_variants(base_name, tint=None):
    variants = []
    base_path = os.path.join('assets', 'tiles')
    # Always include the base tile
    main_path = os.path.join(base_path, f'{base_name}.png')
    if os.path.exists(main_path):
        img = pygame.image.load(main_path).convert()
        img = pygame.transform.smoothscale(img, (TILE_SIZE, TILE_SIZE))
        if tint:
            img = img.copy()
            tint_surf = pygame.Surface(img.get_size()).convert()
            tint_surf.fill(tint)
            img.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_MULT)
        variants.append(img)
    # Look for numbered variants (e.g., grass1.png, grass2.png)
    for i in range(1, 10):
        var_path = os.path.join(base_path, f'{base_name}{i}.png')
        if os.path.exists(var_path):
            img = pygame.image.load(var_path).convert()
            img = pygame.transform.smoothscale(img, (TILE_SIZE, TILE_SIZE))
            if tint:
                img = img.copy()
                tint_surf = pygame.Surface(img.get_size()).convert()
                tint_surf.fill(tint)
                img.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_MULT)
            variants.append(img)
    return variants

import random

grass_tiles = load_tile_variants('grass')
water_tiles = load_tile_variants('water')

tile_images = {
    TILE_GRASS: grass_tiles,
    TILE_WATER: water_tiles
}



# World, player, and enemies setup

world = World(chunk_size=8)
# Find a grass tile near the center of the world to start the player
center_tile_x = 0
center_tile_y = 0
for dy in range(-2, 3):
    for dx in range(-2, 3):
        tx = world.chunk_size // 2 + dx
        ty = world.chunk_size // 2 + dy
        if world.get_tile(tx, ty) == TILE_GRASS:
            center_tile_x = tx
            center_tile_y = ty
            break
    else:
        continue
    break
player = Player(center_tile_x * TILE_SIZE, center_tile_y * TILE_SIZE)
enemies = {}  # Dict[(wx, wy)] = Enemy
blood_overlays = []  # Blood overlays
sword_projectiles = []  # List of SwordProjectile

VIEW_TILES_X = screen.get_width() // TILE_SIZE
VIEW_TILES_Y = screen.get_height() // TILE_SIZE

# Map rendering function for infinite world
def draw_world(surface, player, enemies):
    # Center the view on the player
    px, py = int(player.x), int(player.y)
    tile_offset_x = px // TILE_SIZE - VIEW_TILES_X // 2
    tile_offset_y = py // TILE_SIZE - VIEW_TILES_Y // 2
    # Draw terrain with random tile variations
    for y in range(VIEW_TILES_Y + 2):
        for x in range(VIEW_TILES_X + 2):
            wx = tile_offset_x + x
            wy = tile_offset_y + y
            tile = world.get_tile(wx, wy)
            variants = tile_images.get(tile)
            if variants:
                # Use a deterministic random seed for consistent look per tile
                seed = f"{wx},{wy},{tile}"
                rnd = random.Random(seed)
                img = variants[rnd.randint(0, len(variants)-1)]
                surface.blit(img, (x * TILE_SIZE, y * TILE_SIZE))
    # Draw enemies
    for (wx, wy), enemy in enemies.items():
        sx = (wx - tile_offset_x) * TILE_SIZE
        sy = (wy - tile_offset_y) * TILE_SIZE
        if 0 <= sx < screen.get_width() and 0 <= sy < screen.get_height():
            enemy.draw(surface, sx, sy)
    # Draw sword projectiles
    for proj in sword_projectiles:
        proj.draw(surface, tile_offset_x, tile_offset_y, screen)
    # Draw blood overlays
    for blood in blood_overlays:
        sx = (blood.wx - tile_offset_x) * TILE_SIZE
        sy = (blood.wy - tile_offset_y) * TILE_SIZE
        if 0 <= sx < screen.get_width() and 0 <= sy < screen.get_height():
            blood.draw(surface, sx, sy)

# Get the target tile (wx, wy) of the sword attack
def sword_target_tile(player):
    px, py = int(player.x), int(player.y)
    tx, ty = px // TILE_SIZE, py // TILE_SIZE
    if player.sword_dir == 'right':
        return (tx+1, ty)
    elif player.sword_dir == 'left':
        return (tx-1, ty)
    elif player.sword_dir == 'up':
        return (tx, ty-1)
    elif player.sword_dir == 'down':
        return (tx, ty+1)
    return (tx, ty)

clock = pygame.time.Clock()



import random
SPAWN_CHANCE = 0.01  # Chance per frame to spawn an enemy in view

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            # Fire sword projectile in direction of currently held key, else last_dir
            px, py = int(player.x), int(player.y)
            tx, ty = px // TILE_SIZE, py // TILE_SIZE
            keys = pygame.key.get_pressed()
            dir = None
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dir = 'right'
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dir = 'left'
            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                dir = 'up'
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dir = 'down'
            if dir is None:
                dir = player.last_dir
            else:
                player.last_dir = dir
            # Start projectile at tile in front of player
            if dir == 'right':
                tx += 1
            elif dir == 'left':
                tx -= 1
            elif dir == 'up':
                ty -= 1
            elif dir == 'down':
                ty += 1
            proj = SwordProjectile(tx, ty, dir, max_range=4)
            proj.player_ref = player
            sword_projectiles.append(proj)


    # --- Water collision logic in main loop ---
    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        dx -= 1
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        dx += 1
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        dy -= 1
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        dy += 1
    # Normalize diagonal movement
    if dx != 0 and dy != 0:
        dx *= 0.7071
        dy *= 0.7071
    new_x = player.x + dx * player.speed
    new_y = player.y + dy * player.speed
    # No collision: always allow movement
    player.x = new_x
    player.y = new_y
    player.rect.topleft = (player.x, player.y)

    # Randomly spawn enemies in view
    if random.random() < SPAWN_CHANCE:
        px, py = int(player.x), int(player.y)
        tile_offset_x = px // TILE_SIZE - VIEW_TILES_X // 2
        tile_offset_y = py // TILE_SIZE - VIEW_TILES_Y // 2
        rx = random.randint(tile_offset_x, tile_offset_x + VIEW_TILES_X)
        ry = random.randint(tile_offset_y, tile_offset_y + VIEW_TILES_Y)
        # Only spawn if not on player and not already an enemy there
        if not (rx == px // TILE_SIZE and ry == py // TILE_SIZE) and (rx, ry) not in enemies:
            enemies[(rx, ry)] = Enemy(rx, ry)

    # Move and resolve sword projectiles
    for proj in sword_projectiles:
        if not proj.active:
            continue
        # Check collision with enemy
        if (proj.wx, proj.wy) in enemies:
            blood_overlays.append(Blood(proj.wx, proj.wy))
            del enemies[(proj.wx, proj.wy)]
            proj.active = False
        else:
            proj.move()
    # Remove inactive projectiles
    sword_projectiles[:] = [p for p in sword_projectiles if p.active]

    # Draw infinite world centered on player, with enemies and blood overlays
    draw_world(screen, player, enemies)
    # Draw player on top (centered)

    player_screen_x = screen.get_width() // 2
    player_screen_y = screen.get_height() // 2
    player.rect.topleft = (player_screen_x, player_screen_y)
    player.draw(screen)
    pygame.display.flip()
    clock.tick(60)


pygame.quit()
sys.exit()