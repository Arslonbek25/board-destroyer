import cv2
import numpy as np

from board_processor import BoardProcessor
from controls import get_turn, play_best_move
from detection import find_all_pieces
from engine import get_fen

board = BoardProcessor("assets/screenshot-4.png")
board.process_board()

coords = find_all_pieces(board)


turn = get_turn()
fen = get_fen(coords, turn)
play_best_move(board, fen)
