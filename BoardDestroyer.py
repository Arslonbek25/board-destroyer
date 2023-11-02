import numpy as np

import analysis
import control
import detect
from board import Board

board = Board()


def run():
    while True:
        board.update()
        pos = detect.find_pieces(board.img[:, :, :3])
        if board.color == "b":
            pos = np.flip(pos, axis=(0, 1))
        if not board.board:
            fen = analysis.get_fen(pos, board.turn)
            board.set_fen(fen)
        if not np.array_equal(board.prev_pos, pos):
            board_changed = board.prev_pos is not None and pos is not None
            if board_changed:
                move_made = analysis.find_move(board.prev_pos, pos, board.color)
                if move_made == "error":  # TODO: remove
                    print("FEN", board.board.fen())
                    print(board.prev_pos)
                    print(pos)
                board.board.push_san(move_made)
            our_turn = board.color == board.turn
            if our_turn:
                best_move = board.get_best_move()
                control.play_best_move(board, best_move, board.color)

            board.turn = "b" if board.turn == "w" else "w"
            board.prev_pos = np.copy(pos)

        is_game_over = board.board.is_game_over()
        if is_game_over:
            print("\nGame over")
            break


if __name__ == "__main__":
    run()
