DEBUG = False  # Set to True to enable debug logging

def debug_log(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


import sys
import os
import pygame
from src.player import Player
from src.world import World, TILE_GRASS, TILE_WATER
from src.enemy import Enemy

# --- Health Bar Settings ---
MAX_HEALTH = 100
HEALTH_BAR_WIDTH = 200
HEALTH_BAR_HEIGHT = 24
HEALTH_BAR_MARGIN = 16
HEALTH_BAR_COLOR = (200, 0, 0)
HEALTH_BAR_BG = (0, 0, 0)


HITBOX_OFFSET_X = 16  # pixels to the right for visual fairness
HITBOX_OFFSET_Y = 8   # pixels down for visual fairness

# --- SwordProjectile (Disc) ---
class SwordProjectile:
    TILE_SIZE = 32
    def __init__(self, x, y, direction, max_range=4):
        self.x = x  # pixel position
        self.y = y
        # direction is now a (dx, dy) tuple, normalized
        self.direction = direction
        self.range_left = max_range * self.TILE_SIZE  # range in pixels
        self.active = True
        self.move_cooldown = 0  # not needed for pixel movement
        self.move_timer = 0
        self.returning = False
        self.player_ref = None
        base_dir = os.path.dirname(os.path.abspath(__file__))
        sprite_path = os.path.join(base_dir, 'assets', 'sprites', 'disc.png')
        if os.path.exists(sprite_path):
            img = pygame.image.load(sprite_path).convert_alpha()
            self.image = pygame.transform.smoothscale(img, (self.TILE_SIZE, self.TILE_SIZE))
        else:
            self.image = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE), pygame.SRCALPHA)
            self.image.fill((220, 220, 80))
        self.rect = pygame.Rect(self.x, self.y, self.TILE_SIZE, self.TILE_SIZE)
        self.speed = 8  # pixels per frame

    def move(self):
        if not self.returning:
            dx, dy = self.direction
            self.x += self.speed * dx
            self.y += self.speed * dy
            self.range_left -= self.speed
            if self.range_left <= 0:
                self.returning = True
        else:
            if self.player_ref is not None:
                px = self.player_ref.x + self.player_ref.rect.width // 2
                py = self.player_ref.y + self.player_ref.rect.height // 2
                dx = px - (self.x + self.TILE_SIZE // 2)
                dy = py - (self.y + self.TILE_SIZE // 2)
                dist = (dx ** 2 + dy ** 2) ** 0.5
                if dist < self.speed:
                    self.active = False
                    return
                if dist > 0:
                    self.x += self.speed * dx / dist
                    self.y += self.speed * dy / dist
        self.rect.topleft = (int(self.x), int(self.y))

    def draw(self, surface, tile_offset_x, tile_offset_y, screen):
        sx = int(self.x) - tile_offset_x * self.TILE_SIZE
        sy = int(self.y) - tile_offset_y * self.TILE_SIZE
        if 0 <= sx < screen.get_width() and 0 <= sy < screen.get_height():
            surface.blit(self.image, (sx, sy))

# --- OrbProjectile (Enemy Orb) ---
class OrbProjectile:
    TILE_SIZE = 32
    SPEED = 1  # pixels per frame (balanced speed)
    def __init__(self, wx, wy, player_ref):
        self.x = wx * self.TILE_SIZE
        self.y = wy * self.TILE_SIZE
        self.player_ref = player_ref
        base_dir = os.path.dirname(os.path.abspath(__file__))
        sprite_path = os.path.join(base_dir, 'assets', 'sprites', 'orb.png')
        if os.path.exists(sprite_path):
            img = pygame.image.load(sprite_path).convert_alpha()
            self.image = pygame.transform.smoothscale(img, (self.TILE_SIZE, self.TILE_SIZE))
        else:
            self.image = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE), pygame.SRCALPHA)
            self.image.fill((80, 200, 255))
        self.rect = pygame.Rect(self.x, self.y, self.TILE_SIZE, self.TILE_SIZE)
        self.active = True
    def move(self):
        # Move toward the player's world center, with rightward offset for fairness
        player_center_x = self.player_ref.x + self.player_ref.rect.width // 2 + HITBOX_OFFSET_X
        player_center_y = self.player_ref.y + self.player_ref.rect.height // 2 + HITBOX_OFFSET_Y
        orb_center_x = self.x + self.TILE_SIZE // 2
        orb_center_y = self.y + self.TILE_SIZE // 2
        dx = player_center_x - orb_center_x
        dy = player_center_y - orb_center_y
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist > 1e-2:
            self.x += self.SPEED * dx / dist
            self.y += self.SPEED * dy / dist
        self.rect.topleft = (int(self.x), int(self.y))
    def draw(self, surface, tile_offset_x, tile_offset_y, screen):
        sx = int(self.x) - tile_offset_x * self.TILE_SIZE
        sy = int(self.y) - tile_offset_y * self.TILE_SIZE
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
        debug_log(f"[DEBUG] Looking for blood.png at: {sprite_path}")
        if os.path.exists(sprite_path):
            debug_log("[DEBUG] blood.png found.")
            try:
                img = pygame.image.load(sprite_path).convert_alpha()
                self.image = pygame.transform.smoothscale(img, (self.TILE_SIZE, self.TILE_SIZE))
            except Exception as e:
                debug_log(f"[WARNING] Failed to load blood.png: {e}")
                self.image = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE), pygame.SRCALPHA)
                self.image.fill((200, 0, 0))
        else:
            debug_log("[WARNING] blood.png not found in assets/sprites! Using fallback red tile.")
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



orb_projectiles = []  # List of OrbProjectile

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

# --- Load both player sprites for animation ---
base_dir = os.path.dirname(os.path.abspath(__file__))
sprite1_path = os.path.join(base_dir, 'assets', 'sprites', 'Player.png')
sprite2_path = os.path.join(base_dir, 'assets', 'sprites', 'Player2.png')
def load_player_image(path):
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, (TILE_SIZE, TILE_SIZE))
    else:
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        surf.fill((255, 0, 255))
        return surf
player_images = [load_player_image(sprite1_path), load_player_image(sprite2_path)]
player = Player(center_tile_x * TILE_SIZE, center_tile_y * TILE_SIZE)
player.health = MAX_HEALTH
player.animation_frame = 0
player.animation_timer = 0
player.animation_interval = 10  # frames between swaps
enemies = {}  # Dict[(wx, wy)] = Enemy
blood_overlays = []  # Blood overlays
sword_projectiles = []  # List of SwordProjectile

VIEW_TILES_X = screen.get_width() // TILE_SIZE
VIEW_TILES_Y = screen.get_height() // TILE_SIZE


# --- Load both monster sprites for animation ---
monster1_path = os.path.join(base_dir, 'assets', 'sprites', 'monster1.png')
monster2_path = os.path.join(base_dir, 'assets', 'sprites', 'monster2.png')
def load_monster_image(path):
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, (TILE_SIZE, TILE_SIZE))
    else:
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        surf.fill((0, 255, 0))
        return surf
monster_images = [load_monster_image(monster1_path), load_monster_image(monster2_path)]
monster_animation_frame = 0
monster_animation_timer = 0
monster_animation_interval = 10  # frames between swaps

def draw_world(surface, player, enemies):
    global monster_animation_frame, monster_animation_timer
    # Camera offset: center player on screen
    camera_x = player.x - screen.get_width() // 2 + player.TILE_SIZE // 2
    camera_y = player.y - screen.get_height() // 2 + player.TILE_SIZE // 2
    # Draw terrain with random tile variations
    for y in range(VIEW_TILES_Y + 2):
        for x in range(VIEW_TILES_X + 2):
            wx = int(camera_x // TILE_SIZE) + x
            wy = int(camera_y // TILE_SIZE) + y
            tile = world.get_tile(wx, wy)
            variants = tile_images.get(tile)
            if variants:
                seed = f"{wx},{wy},{tile}"
                rnd = random.Random(seed)
                img = variants[rnd.randint(0, len(variants)-1)]
                sx = wx * TILE_SIZE - camera_x
                sy = wy * TILE_SIZE - camera_y
                surface.blit(img, (sx, sy))
    # Animate monster sprites globally
    monster_animation_timer += 1
    if monster_animation_timer >= monster_animation_interval:
        monster_animation_timer = 0
        monster_animation_frame = (monster_animation_frame + 1) % len(monster_images)
    # Draw enemies with animated sprite
    for (wx, wy), enemy in enemies.items():
        sx = wx * TILE_SIZE - camera_x
        sy = wy * TILE_SIZE - camera_y
        if 0 <= sx < screen.get_width() and 0 <= sy < screen.get_height():
            surface.blit(monster_images[monster_animation_frame], (sx, sy))
    # Draw sword projectiles (player disc)
    for disc in sword_projectiles:
        sx = int(disc.x) - camera_x
        sy = int(disc.y) - camera_y
        if 0 <= sx < screen.get_width() and 0 <= sy < screen.get_height():
            surface.blit(disc.image, (sx, sy))
    # Draw orb projectiles (enemy orbs)
    for orb in orb_projectiles:
        sx = int(orb.x) - camera_x
        sy = int(orb.y) - camera_y
        if 0 <= sx < screen.get_width() and 0 <= sy < screen.get_height():
            surface.blit(orb.image, (sx, sy))
    # Draw blood overlays
    for blood in blood_overlays:
        sx = blood.wx * TILE_SIZE - camera_x
        sy = blood.wy * TILE_SIZE - camera_y
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
import time
import random

# Track last shot time for each enemy
enemy_orb_timers = {}  # (wx, wy): next_shot_time
SPAWN_CHANCE = 0.01  # Chance per frame to spawn an enemy in view


def draw_health_bar(surface, health):
    # Draws the health bar at the bottom left
    x = HEALTH_BAR_MARGIN
    y = surface.get_height() - HEALTH_BAR_HEIGHT - HEALTH_BAR_MARGIN
    # Background (empty bar)
    pygame.draw.rect(surface, HEALTH_BAR_BG, (x, y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT), border_radius=8)
    # Foreground (current health)
    health_width = int(HEALTH_BAR_WIDTH * max(0, health) / MAX_HEALTH)
    if health_width > 0:
        pygame.draw.rect(surface, HEALTH_BAR_COLOR, (x, y, health_width, HEALTH_BAR_HEIGHT), border_radius=8)

running = True
while running:

    # --- Health bar and orb collision logic ---
    player.rect.topleft = (int(player.x), int(player.y))
    player_hitbox = pygame.Rect(
        player.x + player.rect.width // 2 + HITBOX_OFFSET_X - 2,
        player.y + player.rect.height // 2 + HITBOX_OFFSET_Y - 2,
        5, 5
    )
    debug_log(f"[PLAYER] Location: x={player.x:.2f}, y={player.y:.2f}, screen=({screen.get_width()}x{screen.get_height()})")
    # Only reduce health once per orb hit, and only if not already in invulnerable state
    orb_hit = False
    orbs_to_remove = []
    for orb in orb_projectiles:
        orb.rect.topleft = (int(orb.x), int(orb.y))
        orb_hitbox = pygame.Rect(
            orb.x + orb.rect.width // 2,
            orb.y + orb.rect.height // 2,
            1, 1
        )
        debug_log(f"[ORB] Location: x={orb.x:.2f}, y={orb.y:.2f}")
        if player_hitbox.colliderect(orb_hitbox):
            orb_hit = True
            orbs_to_remove.append(orb)
    # Only reduce health if an orb hit is detected and player was not already hit in the previous frame
    if not hasattr(player, 'was_hit_last_frame'):
        player.was_hit_last_frame = False
    if orb_hit and not player.was_hit_last_frame:
        player.health -= 10
        player.health = max(0, player.health)
        if player.health <= 0:
            font = pygame.font.SysFont('Arial', 64, bold=True)
            text = font.render('GAME OVER', True, (255, 0, 0))
            text_rect = text.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
            screen.blit(text, text_rect)
            pygame.display.flip()
            pygame.time.wait(2000)
            show_splash()
            os.execv(sys.executable, ['python3'] + sys.argv)
    player.was_hit_last_frame = orb_hit
    # Remove orbs that hit the player
    for orb in orbs_to_remove:
        if orb in orb_projectiles:
            orb_projectiles.remove(orb)
    # --- Disc defeats orbs: pass through and remove orb ---
    for disc in sword_projectiles:
        if not disc.active:
            continue
        for orb in list(orb_projectiles):
            # Check if orb is within a 3x3 area centered on the disc (pixel-based)
            if abs((disc.x + disc.TILE_SIZE//2) - (orb.x + orb.TILE_SIZE//2)) <= disc.TILE_SIZE and \
               abs((disc.y + disc.TILE_SIZE//2) - (orb.y + orb.TILE_SIZE//2)) <= disc.TILE_SIZE:
                orb_projectiles.remove(orb)
    # --- Disc hits enemy: defeat monster, add blood overlay ---
    for disc in sword_projectiles:
        if not disc.active:
            continue
        for (wx, wy), enemy in list(enemies.items()):
            # If disc overlaps enemy (pixel-based)
            enemy_rect = pygame.Rect(wx * TILE_SIZE, wy * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if enemy_rect.colliderect(disc.rect):
                blood_overlays.append(Blood(wx, wy))
                del enemies[(wx, wy)]
    for event in pygame.event.get():
        debug_log(f"[EVENT] type={event.type} key={getattr(event, 'key', None)}")
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_x:
            # Fire sword projectile in direction of currently held key(s), else last_dir
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
            left = keys[pygame.K_LEFT] or keys[pygame.K_a]
            up = keys[pygame.K_UP] or keys[pygame.K_w]
            down = keys[pygame.K_DOWN] or keys[pygame.K_s]
            xfire = keys[pygame.K_x]
            # Log for debugging
            debug_log(f"[DISC TOSS] xfire={xfire} right={right} left={left} up={up} down={down}")
            if right and not left:
                dx = 1
            if left and not right:
                dx = -1
            if down and not up:
                dy = 1
            if up and not down:
                dy = -1
            # Normalize diagonal
            if dx != 0 and dy != 0:
                dx *= 0.7071
                dy *= 0.7071
            # Logging for debugging
            debug_log(f"[DISC TOSS] Keys: right={right}, left={left}, up={up}, down={down} | dx={dx}, dy={dy}")
            if dx == 0 and dy == 0:
                # No direction pressed, use last_dir
                dir = player.last_dir
                dir_map = {'right': (1, 0), 'left': (-1, 0), 'up': (0, -1), 'down': (0, 1)}
                dx, dy = dir_map.get(dir, (1, 0))
                debug_log(f"[DISC TOSS] No direction pressed, using last_dir={dir} -> dx={dx}, dy={dy}")
            # Only update last_dir if a single cardinal direction is pressed
            if (dx == 1 and dy == 0):
                player.last_dir = 'right'
            elif (dx == -1 and dy == 0):
                player.last_dir = 'left'
            elif (dx == 0 and dy == -1):
                player.last_dir = 'up'
            elif (dx == 0 and dy == 1):
                player.last_dir = 'down'
            debug_log(f"[DISC TOSS] Final direction: ({dx}, {dy})")
            # Start projectile at center of player
            px_center = player.x + player.rect.width // 2 - TILE_SIZE // 2
            py_center = player.y + player.rect.height // 2 - TILE_SIZE // 2
            proj = SwordProjectile(px_center, py_center, (dx, dy), max_range=4)
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
    # No collision: always allow movement
    player.move(dx * player.speed, dy * player.speed)

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



    # Move sword projectiles (disc)
    for disc in sword_projectiles:
        if disc.active:
            disc.move()
    sword_projectiles[:] = [d for d in sword_projectiles if d.active]

    # Move orb projectiles (enemy orbs)
    for orb in orb_projectiles:
        if orb.active:
            orb.move()
    orb_projectiles[:] = [o for o in orb_projectiles if o.active]



    # Enemies shoot orbs at the player every 5-10 seconds, independently
    now = time.time()
    for (wx, wy), enemy in enemies.items():
        key = (wx, wy)
        if key not in enemy_orb_timers:
            # Schedule first shot randomly in 5-10 seconds
            enemy_orb_timers[key] = now + random.uniform(5, 10)
        if now >= enemy_orb_timers[key]:
            orb_projectiles.append(OrbProjectile(wx, wy, player))
            # Schedule next shot
            enemy_orb_timers[key] = now + random.uniform(5, 10)
    # Remove inactive disc projectiles
    sword_projectiles[:] = [d for d in sword_projectiles if d.active]
    # Clean up timers for dead enemies
    for key in list(enemy_orb_timers.keys()):
        if key not in enemies:
            del enemy_orb_timers[key]


    # Draw infinite world centered on player, with enemies and blood overlays
    draw_world(screen, player, enemies)


    # Animate player sprite only when moving
    keys = pygame.key.get_pressed()
    moving = (
        keys[pygame.K_LEFT] or keys[pygame.K_a] or
        keys[pygame.K_RIGHT] or keys[pygame.K_d] or
        keys[pygame.K_UP] or keys[pygame.K_w] or
        keys[pygame.K_DOWN] or keys[pygame.K_s]
    )
    if moving:
        player.animation_timer += 1
        if player.animation_timer >= player.animation_interval:
            player.animation_timer = 0
            player.animation_frame = (player.animation_frame + 1) % len(player_images)
    else:
        player.animation_frame = 0
        player.animation_timer = 0
    player_screen_x = screen.get_width() // 2
    player_screen_y = screen.get_height() // 2
    screen.blit(player_images[player.animation_frame], (player_screen_x, player_screen_y))
    if player.sword_active and player.sword_dir in player.sword_images:
        offset = {
            'right': (player.TILE_SIZE, 0),
            'left': (-player.TILE_SIZE, 0),
            'up': (0, -player.TILE_SIZE),
            'down': (0, player.TILE_SIZE)
        }[player.sword_dir]
        sword_rect = pygame.Rect(player_screen_x + offset[0], player_screen_y + offset[1], player.TILE_SIZE, player.TILE_SIZE)
        screen.blit(player.sword_images[player.sword_dir], sword_rect)

    # Draw health bar
    draw_health_bar(screen, player.health)

    pygame.display.flip()
    clock.tick(60)


pygame.quit()
sys.exit()