import numpy as np
import pyautogui as pg

from config import Color

pg.PAUSE = 0
pg.MINIMUM_DURATION = 0
pg.MINIMUM_SLEEP = 0


def move_to_pixels(move, board):
    ranks = "abcdefgh"
    files = "12345678"

    if board.color == Color.BLACK:
        ranks = ranks[::-1]
        files = files[::-1]

    x1 = ranks.index(move[0])
    y1 = 7 - files.index(move[1])
    x2 = ranks.index(move[2])
    y2 = 7 - files.index(move[3])
    coords = (np.array([x1, y1, x2, y2], dtype=float) + 1) * board.sq_size_orig
    return coords


def focus(board) -> None:
    pg.click(board.corners[0, 0], board.corners[0, 1])


def play_move(board, move: str) -> None:
    move_coords = move_to_pixels(move, board)

    move_coords[:2] += board.corners[0] - board.sq_size
    move_coords[2:] += board.corners[0] - board.sq_size

    move_coords /= board.scale
    x1, y1, x2, y2 = move_coords

    pg.moveTo(x1, y1)
    pg.dragTo(x2, y2, button="left")
    promotion = "qnrb".find(move.lower()[-1])
    if promotion != -1:
        pg.moveTo(x2, y2 + promotion * board.sq_size)
        pg.click()
