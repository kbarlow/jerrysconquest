import pytest
from src.player import Player

def test_player_initial_position():
    player = Player(32, 32)
    assert player.x == 32
    assert player.y == 32
    assert hasattr(player, 'rect')
