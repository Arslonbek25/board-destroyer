import pyautogui as pg

from engine import get_best_move, san_to_coords


def get_prop(board):
    screen_size = pg.size()
    img_size = board.shape
    prop = img_size[0] / screen_size[1]
    return prop


def play_move(move_coords, prop):
    move_coords /= prop
    x1, y1, x2, y2 = move_coords
    pg.moveTo(x1, y1, duration=0.3)
    pg.moveTo(x2, y2, duration=0.3)


def play_best_move(board, engine, fen):
    best_move = get_best_move(fen, engine)
    move_coords = san_to_coords(best_move, board.sq_size_orig)

    move_coords[:2] += board.topLeftCorner - board.sq_size / 2
    move_coords[2:] += board.topLeftCorner - board.sq_size / 2

    play_move(move_coords, board.prop)


def get_turn():
    turn = ""
    while turn not in ["b", "w"]:
        turn = input("Whose turn is it? (b/w): ")
    return turn
