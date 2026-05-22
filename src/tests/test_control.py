import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import Color
from control import move_to_pixels


def board(color: Color, sq_size_orig: float = 10.0):
    return SimpleNamespace(color=color, sq_size_orig=sq_size_orig)


def test_white_a1a2():
    coords = move_to_pixels("a1a2", board(Color.WHITE))
    # a1: file=a(0), rank=1 → x=0, y=7; a2: x=0, y=6
    # (x+1, y+1) * sq_size = (1,8,1,7) * 10
    assert list(coords) == [10.0, 80.0, 10.0, 70.0]


def test_white_h8h1():
    coords = move_to_pixels("h8h1", board(Color.WHITE))
    # h8: x=7, y=0; h1: x=7, y=7
    assert list(coords) == [80.0, 10.0, 80.0, 80.0]


def test_black_a1a2():
    coords = move_to_pixels("a1a2", board(Color.BLACK))
    # ranks/files reversed: "a" → index 7, "1" → index 7 so y=0; "2" → index 6 so y=1
    assert list(coords) == [80.0, 10.0, 80.0, 20.0]


def test_black_h8h1():
    coords = move_to_pixels("h8h1", board(Color.BLACK))
    # "h" reversed → 0, "8" reversed → 0 so y=7; "1" reversed → 7 so y=0
    assert list(coords) == [10.0, 80.0, 10.0, 10.0]


def test_color_mirror_symmetry():
    # For any move on a square board, white_coord + black_coord = (board_size + 1) * sq_size
    # (because reversing an 8-element string maps index i to 7 - i, and the function adds +1
    # before scaling — so the sum is (i+1) + (7-i+1) = 9 per axis)
    sq = 10.0
    for move in ["e2e4", "g8f6", "d7d5", "a1h8", "h1a8"]:
        w = move_to_pixels(move, board(Color.WHITE, sq))
        b = move_to_pixels(move, board(Color.BLACK, sq))
        for i in range(4):
            assert w[i] + b[i] == 9 * sq, f"mismatch at {move}[{i}]"


def test_promotion_suffix_ignored_for_pixel_math():
    # The promotion piece is consumed elsewhere (play_move); move_to_pixels reads
    # only the first four characters' file/rank values, so it must not crash and
    # must produce the same coordinates as the bare move.
    bare = move_to_pixels("a7a8", board(Color.WHITE))
    promo = move_to_pixels("a7a8q", board(Color.WHITE))
    assert list(bare) == list(promo)


def test_scales_with_sq_size():
    small = move_to_pixels("e2e4", board(Color.WHITE, sq_size_orig=1.0))
    big = move_to_pixels("e2e4", board(Color.WHITE, sq_size_orig=50.0))
    for s, b in zip(small, big):
        assert b == s * 50.0
