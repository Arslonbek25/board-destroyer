import pyautogui as pg

from analysis import san_to_coords


def play_move(move_coords, scale):
    move_coords /= scale
    x1, y1, x2, y2 = move_coords
    pg.moveTo(x1, y1)
    pg.dragTo(x2, y2, button="left")


def play_best_move(board, best_move, color):
    move_coords = san_to_coords(best_move, board.sq_size_orig, color)
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


def get_timecontrol():
    tc_map = {"1": "bullet", "2": "blitz", "3": "rapid"}
    options = ", ".join(tc_map.values())
    while True:
        inp = input(f"\nEnter time control [{options}]: ").strip().lower()
        if inp in tc_map.values():
            return inp
        if inp in tc_map:
            return tc_map[inp]
