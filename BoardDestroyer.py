import threading

from analysis import get_fen, init_engine, is_game_over
from board_processor import BoardProcessor
from controls import get_turn, play_best_move, get_color
import detect
import numpy as np

board = BoardProcessor()
while True:
    try:
        board.process_board()
        break
    except:
        print("Chessboard not detected")

engine = init_engine()

turn = get_turn()
color = get_color()
first_turn = turn
prev_pos = None


def change_turn():
    global turn
    if turn == "w":
        turn = "b"
    else:
        turn = "w"


def run():
    if is_game_over:
        engine.quit()
        return

    global prev_pos, first_turn, turn
    try:
        board.update()
        pos = detect.find_pieces(board.imgbgr[:, :, :3])
        # pos = find_all_pieces(board)
    except Exception as e:
        print("can't update")
        # raise e
        # return threading.Timer(0.1, run).start()
    fen = get_fen(pos, turn)
    print(fen)
    if not (prev_pos == pos).all():
        if color == turn:
            play_best_move(board, engine, fen)
        change_turn()
    print(color, turn)
    prev_pos = np.copy(pos)
    threading.Timer(1, run).start()


run()
