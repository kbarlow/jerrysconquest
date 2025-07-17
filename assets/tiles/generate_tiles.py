import pygame
import os

# Define tile size and colors
TILE_SIZE = 32
TILES = {
    'grass': (34, 177, 76),   # green
    'water': (0, 162, 232)    # blue
}

# Ensure output directory exists
output_dir = os.path.dirname(__file__)

pygame.init()
for name, color in TILES.items():
    surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
    surface.fill(color)
    pygame.image.save(surface, os.path.join(output_dir, f"{name}.png"))
pygame.quit()

print("Tiles generated in:", output_dir)
