import numpy as np

import analysis
import control
import detect
from board import Board

board = Board()

turn = control.get_turn()
color = control.get_color()


def change_turn():
    global turn
    turn = "b" if turn == "w" else "w"


def run():
    while True:
        board.update()
        pos = detect.find_pieces(board.img[:, :, :3])
        fen = analysis.get_fen(pos, turn)
        board.set_fen(fen)
        if not np.array_equal(board.prev_pos, pos):
            if board.prev_pos is not None and pos is not None:
                move_made = analysis.find_move(board.prev_pos, pos)
                print("Move made:", move_made)
                print("FEN", board.board.fen())
                board.board.push_san(move_made)
            if color == turn:
                best_move = board.get_best_move()
                control.play_best_move(board, best_move)
            change_turn()
            board.prev_pos = np.copy(pos)


if __name__ == "__main__":
    run()
