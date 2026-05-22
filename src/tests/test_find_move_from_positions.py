import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from position import find_move


def empty_pos():
    return np.zeros((8, 8), dtype=np.dtype("U1"))


def rc(square: str):
    files = "abcdefgh"
    file = files.index(square[0])
    rank = int(square[1])
    row = 8 - rank
    col = file
    return (row, col)


def test_simple_move_e2e4():
    before = empty_pos()
    after = empty_pos()
    before[rc("e2")] = "P"
    after[rc("e4")] = "P"
    assert find_move(before, after) == "e2e4"


def test_capture_e4d5():
    before = empty_pos()
    after = empty_pos()
    before[rc("e4")] = "P"
    before[rc("d5")] = "p"
    after[rc("d5")] = "P"
    assert find_move(before, after) == "e4d5"


def test_promotion_a7a8q():
    before = empty_pos()
    after = empty_pos()
    before[rc("a7")] = "P"
    after[rc("a8")] = "Q"
    assert find_move(before, after) == "a7a8q"


def test_castle_kingside_white():
    before = empty_pos()
    after = empty_pos()
    before[rc("e1")] = "K"
    before[rc("h1")] = "R"
    after[rc("g1")] = "K"
    after[rc("f1")] = "R"
    assert find_move(before, after) == "e1g1"


def test_en_passant_returns_error_current_impl():
    before = empty_pos()
    after = empty_pos()
    before[rc("e5")] = "P"
    before[rc("d5")] = "p"
    after[rc("d6")] = "P"
    assert find_move(before, after) == "error"


def test_queenside_castle_order_dependent_bug_check():
    # White O-O-O: e1c1 and a1d1
    before = empty_pos()
    after = empty_pos()
    before[rc("e1")] = "K"
    before[rc("a1")] = "R"
    after[rc("c1")] = "K"
    after[rc("d1")] = "R"

    # If this fails, your castling branch is order-dependent.
    assert find_move(before, after) == "e1c1"


def test_noise_diff_1_piece_missing():
    before = empty_pos()
    after = empty_pos()
    before[rc("e2")] = "P"
    # after misses the pawn entirely for a frame
    assert find_move(before, after) == "error"


def test_noise_diff_1_piece_ghost_duplicate():
    before = empty_pos()
    after = empty_pos()
    before[rc("e2")] = "P"
    after[rc("e2")] = "P"
    after[rc("h8")] = "q"  # spurious extra detection
    assert find_move(before, after) == "error"


def test_noise_move_but_source_not_cleared():
    # YOLO often does this: destination filled but source still filled
    before = empty_pos()
    after = empty_pos()
    before[rc("e2")] = "P"
    after[rc("e2")] = "P"  # still there (ghost)
    after[rc("e4")] = "P"
    # diff_cnt will be 1 (only e4 changed) or 2 depending on representation; this should be error
    assert find_move(before, after) == "error"


def test_en_passant_should_be_error_current():
    before = empty_pos()
    after = empty_pos()
    before[rc("e5")] = "P"
    before[rc("d5")] = "p"
    after[rc("d6")] = "P"  # pawn moved diagonally
    # captured pawn removed at d5
    assert find_move(before, after) == "error"
