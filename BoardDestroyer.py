import random
import numpy as np

import analysis
import control
import detect
from board import Board
import time

board = Board()

turn = control.get_turn()
color = control.get_color()
timecontrol = control.get_timecontrol()


def change_turn():
    global turn
    turn = "b" if turn == "w" else "w"


def run():
    while True:
        board.update()
        pos = detect.find_pieces(board.img[:, :, :3])
        if not board.board:
            fen = analysis.get_fen(pos, turn, color)
            board.set_fen(fen)

        if not np.array_equal(board.prev_pos, pos):
            move_time = time.time() - board.last_speed if board.last_speed else 0.5
            board.last_speed = time.time()
            move_time = min(
                max(random.randint(35, 60) / 100 * move_time, 0.2),
                board.max_move_time[timecontrol],
            )
            board_changed = board.prev_pos is not None and pos is not None
            if board_changed:
                move_made = analysis.find_move(board.prev_pos, pos, color)
                if move_made == "error":  # TODO: remove
                    print("FEN", board.board.fen())
                    print(board.prev_pos)
                    print(pos)
                board.board.push_san(move_made)
            our_turn = color == turn
            if our_turn:
                best_move = board.get_best_move(move_time)
                control.play_best_move(board, best_move, color)

            change_turn()
            board.prev_pos = np.copy(pos)

        is_game_over = board.board.is_game_over()
        if is_game_over:
            print("Game over")
            break


if __name__ == "__main__":
    run()
