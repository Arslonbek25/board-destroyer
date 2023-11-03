import numpy as np

import analysis
import control
import detect
from board import Board


def run():
    board = Board()
    while not board.game_over():
        board.update()
        board.pos = detect.find_pieces(board)
        first_move = board.prev_pos is None
        if first_move:
            fen = analysis.get_fen(board.pos, board.turn)
            board.set_fen(fen)
        if board.pos_changed():
            if not first_move:
                move_made = analysis.find_move(board)
                if move_made == "error":  # TODO: remove
                    print("FEN", board.board.fen(), "\n")
                    print(board.prev_pos, "\n")
                    print(board.pos, "\n")
                board.board.push_san(move_made)
            if board.is_our_turn():
                best_move = board.get_best_move()
                control.play_move(board, best_move)
            board.switch_turn()
    print("\nGame over")


if __name__ == "__main__":
    run()
