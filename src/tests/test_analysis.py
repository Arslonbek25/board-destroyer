import sys
from pathlib import Path

import chess
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analysis import get_board_position, get_fen


def empty_pos():
    return np.zeros((8, 8), dtype=np.dtype("U1"))


def rc(square: str):
    file = "abcdefgh".index(square[0])
    rank = int(square[1])
    return (8 - rank, file)


def test_get_fen_starting_position():
    pos = np.array(
        [
            list("rnbqkbnr"),
            list("pppppppp"),
            [""] * 8,
            [""] * 8,
            [""] * 8,
            [""] * 8,
            list("PPPPPPPP"),
            list("RNBQKBNR"),
        ]
    )
    fen = get_fen(pos, "w")
    assert fen == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w"


def test_get_fen_empty_board():
    assert get_fen(empty_pos(), "w") == "8/8/8/8/8/8/8/8 w"


def test_get_fen_runs_empty_then_piece_then_empty():
    pos = empty_pos()
    pos[rc("d4")] = "P"
    # rank 4 row (index 4): 3 empty, P, 4 empty → "3P4"
    fen = get_fen(pos, "b")
    assert "3P4" in fen.split("/")[4]
    assert fen.endswith(" b")


def test_get_fen_turn_token_is_last():
    fen = get_fen(empty_pos(), "b")
    assert fen.split(" ")[-1] == "b"


def test_get_board_position_starting_board():
    board = chess.Board()
    pos = get_board_position(board)
    assert pos[0] == ["r", "n", "b", "q", "k", "b", "n", "r"]
    assert pos[1] == ["p"] * 8
    assert pos[6] == ["P"] * 8
    assert pos[7] == ["R", "N", "B", "Q", "K", "B", "N", "R"]
    for rank in pos[2:6]:
        assert rank == [""] * 8


def test_get_board_position_after_e2e4():
    board = chess.Board()
    board.push_san("e4")
    pos = get_board_position(board)
    assert pos[6][4] == ""   # e2 empty
    assert pos[4][4] == "P"  # e4 has pawn


def test_get_fen_roundtrip_via_chess():
    board = chess.Board()
    board.push_san("e4")
    board.push_san("c5")
    pos = get_board_position(board)
    fen_piece_field = get_fen(pos, "w").split(" ")[0]
    assert fen_piece_field == board.fen().split(" ")[0]
