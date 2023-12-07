import numpy as np
import pyautogui as pg


def move_to_pixels(move, board):
    ranks = "abcdefgh"
    files = "12345678"

    if board.color == "b":
        ranks = ranks[::-1]
        files = files[::-1]

    x1 = ranks.index(move[0])
    y1 = 7 - files.index(move[1])
    x2 = ranks.index(move[2])
    y2 = 7 - files.index(move[3])
    coords = (np.array([x1, y1, x2, y2], dtype=float) + 1) * board.sq_size_orig
    return coords


def play_move(board, move):
    move_coords = move_to_pixels(move, board)
    move_coords[:2] += board.corners[0] - board.sq_size
    move_coords[2:] += board.corners[0] - board.sq_size

    move_coords /= board.scale
    x1, y1, x2, y2 = move_coords
    pg.moveTo(x1, y1)
    pg.dragTo(x2, y2, button="left")


def get_turn():
    turn = ""
    while turn not in ["b", "w"]:
        turn = input("Whose turn is it? (b/w): \n")
    return turn


def get_color():
    turn = ""
    while turn not in ["b", "w"]:
        turn = input("What color are you playing? (b/w): \n")
    return turn


def get_timecontrol():
    tc_map = {"1": "bullet", "2": "blitz", "3": "rapid", "4": "puzzle"}
    options = ", ".join(tc_map.values())
    while True:
        inp = input(f"Enter time control [{options}]: \n").strip().lower()
        if inp in tc_map.values():
            return inp
        if inp in tc_map:
            return tc_map[inp]
