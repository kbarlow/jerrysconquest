import random

TILE_GRASS = 0
TILE_WATER = 1

class World:
    def __init__(self, chunk_size=8):
        self.chunk_size = chunk_size
        self.chunks = {}  # (cx, cy): [[tile,...], ...]

    def get_chunk(self, cx, cy):
        if (cx, cy) not in self.chunks:
            self.chunks[(cx, cy)] = self.generate_chunk(cx, cy)
        return self.chunks[(cx, cy)]

    def generate_chunk(self, cx, cy):
        # Grouped water: more likely to be water if neighbors are water
        grid = [[TILE_WATER for _ in range(self.chunk_size)] for _ in range(self.chunk_size)]
        # 1. Carve a guaranteed grass path from left to right
        # Widened, natural path using random walk with width
        path_y = self.chunk_size // 2
        path_width = random.choice([2, 3])
        for x in range(self.chunk_size):
            # For each x, carve a vertical band of grass (width 2-3)
            for w in range(-path_width//2, path_width//2 + 1):
                py = path_y + w + random.choice([-1, 0, 0, 1])  # Add some jitter
                if 0 <= py < self.chunk_size:
                    grid[py][x] = TILE_GRASS
            # Move the center of the path up/down by 0, 1, or -1
            if x < self.chunk_size - 1:
                move = random.choice([-1, 0, 1, 0])
                path_y = max(0, min(self.chunk_size - 1, path_y + move))
        # 2. Add more random grass patches (about 40% of remaining water tiles)
        for y in range(self.chunk_size):
            for x in range(self.chunk_size):
                if grid[y][x] == TILE_WATER and random.random() < 0.4:
                    grid[y][x] = TILE_GRASS
        # Debug: count water tiles
        water_count = sum(row.count(TILE_WATER) for row in grid)
        grass_count = sum(row.count(TILE_GRASS) for row in grid)
        from main import debug_log
        debug_log(f"[DEBUG] Chunk ({cx},{cy}) water tiles: {water_count}, grass tiles: {grass_count}")
        return grid

    def get_tile(self, wx, wy):
        # wx, wy: world tile coordinates
        cx, tx = divmod(wx, self.chunk_size)
        cy, ty = divmod(wy, self.chunk_size)
        chunk = self.get_chunk(cx, cy)
        return chunk[ty][tx]
