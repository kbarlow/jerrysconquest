import pygame
import os

class Player:
    def set_position(self, x, y):
        """Set player position and update rect."""
        self.x = x
        self.y = y
        self.rect.topleft = (self.x, self.y)

    def move(self, dx, dy):
        """Move player by (dx, dy) and update rect."""
        self.x += dx
        self.y += dy
        self.rect.topleft = (self.x, self.y)
    def __init__(self, x, y, speed=2):
        self.x = x
        self.y = y
        self.speed = speed
        self.last_dir = 'right'  # Track last direction for sword
        self.sword_active = False
        self.sword_dir = 'right'
        self.sword_timer = 0
        self.TILE_SIZE = 32
        # Load player sprite
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sprite_path = os.path.join(base_dir, 'assets', 'sprites', 'Player.png')
        if not os.path.exists(sprite_path):
            sprite_path = os.path.join(base_dir, 'assets', 'sprites', 'player.png')
        if os.path.exists(sprite_path):
            img = pygame.image.load(sprite_path).convert_alpha()
            self.image = pygame.transform.smoothscale(img, (self.TILE_SIZE, self.TILE_SIZE))
        else:
            self.image = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE), pygame.SRCALPHA)
            self.image.fill((200, 30, 30))
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        # Load sword sprites
        self.sword_images = {}
        for dir_name in ['Right', 'Left', 'Up', 'Down']:
            sword_path = os.path.join(base_dir, 'assets', 'sprites', f'{dir_name}Sword.png')
            if os.path.exists(sword_path):
                img = pygame.image.load(sword_path).convert_alpha()
                self.sword_images[dir_name.lower()] = pygame.transform.smoothscale(img, (self.TILE_SIZE, self.TILE_SIZE))

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        dir_pressed = None
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
            dir_pressed = 'left'
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
            dir_pressed = 'right'
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
            dir_pressed = 'up'
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1
            dir_pressed = 'down'
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
        self.move(dx * self.speed, dy * self.speed)
        # Track last direction
        if dir_pressed:
            self.last_dir = dir_pressed
        # Decrease sword timer
        if self.sword_active:
            self.sword_timer -= 1
            if self.sword_timer <= 0:
                self.sword_active = False

    def attack(self, direction=None):
        # Called from main loop when spacebar is pressed
        sword_dir = direction or self.last_dir
        self.sword_active = True
        self.sword_dir = sword_dir
        self.sword_timer = 8  # frames to show sword

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        # Draw sword if active
        if self.sword_active and self.sword_dir in self.sword_images:
            offset = {
                'right': (self.TILE_SIZE, 0),
                'left': (-self.TILE_SIZE, 0),
                'up': (0, -self.TILE_SIZE),
                'down': (0, self.TILE_SIZE)
            }[self.sword_dir]
            sword_rect = self.rect.move(offset)
            surface.blit(self.sword_images[self.sword_dir], sword_rect)