import threading

import analysis
import control
import detect
from board import Board


def run():
    board = Board()
    while not board.game_over():
        board.update()
        board.pos = detect.find_pieces(board)
        is_first_run = board.prev_pos is None
        if is_first_run:
            fen = analysis.get_fen(board.pos, board.turn)
            board.set_fen(fen)
        if board.pos_changed():
            if not board.is_our_turn():
                board.end_opp_move_time()
                if not is_first_run:
                    move_made = analysis.find_move(board)
                    board.push_move(move_made)
                board.switch_turn(is_first_run)
            if board.is_our_turn():
                best_move = board.get_best_move()
                board.push_move(best_move)
                control.play_move(board, best_move)
                board.start_opp_move_time()
                board.pos = analysis.get_board_position(board.board)
                board.switch_turn()
                board.calc_thread = threading.Thread(target=board.analyze_board)
                board.calc_thread.start()
    print("Game over\n")


if __name__ == "__main__":
    run()
