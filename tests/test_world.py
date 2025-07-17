import pytest
from src.world import World, TILE_GRASS, TILE_WATER

def test_world_generation():
    world = World(chunk_size=8)
    # Check that the world has at least some grass and water tiles
    grass_count = 0
    water_count = 0
    for x in range(8):
        for y in range(8):
            tile = world.get_tile(x, y)
            if tile == TILE_GRASS:
                grass_count += 1
            elif tile == TILE_WATER:
                water_count += 1
    assert grass_count > 0
    assert water_count > 0
