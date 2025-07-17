import pygame
import os
import random

class Enemy:
    TILE_SIZE = 32
    def __init__(self, wx, wy):
        self.wx = wx  # world x (tile)
        self.wy = wy  # world y (tile)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sprite_path = os.path.join(base_dir, 'assets', 'sprites', 'monster1.png')
        if os.path.exists(sprite_path):
            img = pygame.image.load(sprite_path).convert_alpha()
            self.image = pygame.transform.smoothscale(img, (self.TILE_SIZE, self.TILE_SIZE))
        else:
            self.image = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE), pygame.SRCALPHA)
            self.image.fill((150, 0, 150))
        self.rect = self.image.get_rect()

    def draw(self, surface, screen_x, screen_y):
        self.rect.topleft = (screen_x, screen_y)
        surface.blit(self.image, self.rect)
