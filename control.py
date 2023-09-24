import pyautogui as pg

from analysis import san_to_coords


def play_move(move_coords, scale):
    move_coords /= scale
    x1, y1, x2, y2 = move_coords
    pg.moveTo(x1, y1, duration=0.1)
    pg.dragTo(x2, y2, duration=0.1, button="left")


def play_best_move(board, best_move):
    move_coords = san_to_coords(best_move, board.sq_size_orig)
    move_coords[:2] += board.corners[0] - board.sq_size / 2
    move_coords[2:] += board.corners[0] - board.sq_size / 2

    play_move(move_coords, board.scale)


def get_turn():
    turn = ""
    while turn not in ["b", "w"]:
        turn = input("Whose turn is it? (b/w): ")
    return turn


def get_color():
    turn = ""
    while turn not in ["b", "w"]:
        turn = input("\nWhat color are you playing? (b/w): ")
    return turn
