import threading

from analysis import get_fen, init_engine, is_game_over
from board_processor import BoardProcessor
from controls import get_turn, play_best_move
from detection import find_all_pieces

board = BoardProcessor("assets/screenshot-4.png")
board.process_board()
engine = init_engine()

turn = get_turn()
prev_pos = None


def run():
    if is_game_over:
        engine.quit()
        return

    global prev_pos
    board.update()
    pos = find_all_pieces(board)
    if not (prev_pos == pos).all():
        fen = get_fen(pos, turn)
        play_best_move(board, engine, fen)
    prev_pos = pos
    threading.Timer(0.1, run).start()


run()
