import threading

import cv2
import numpy as np

from board_processor import BoardProcessor
from controls import get_turn, play_best_move
from detection import find_all_pieces
from engine import get_fen, init_engine

board = BoardProcessor("assets/screenshot-4.png")
board.process_board()
engine = init_engine()

turn = get_turn()


def run():
    coords = find_all_pieces(board)
    fen = get_fen(coords, turn)
    play_best_move(board, engine, fen)
    board.update()
    # threading.Timer(2, run).start()


run()

engine.quit()
