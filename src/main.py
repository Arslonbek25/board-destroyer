import threading

import analysis
import control
import detect
from board import Board
import chess


def run(config_instance, stop_game=None):
    board = Board(config_instance)
    while config_instance.game_running and not board.game_over():
        board.update()
        try:
            board.pos = detect.find_pieces(board)
        except IndexError:
            break
        is_first_run = board.prev_pos is None
        if is_first_run:
            fen = analysis.get_fen(board.pos, board.turn)
            board.set_fen(fen)
            board.focus()
        if board.pos_changed():
            if not board.is_our_turn():
                board.end_opp_move_time()
                if not is_first_run:
                    move_made = analysis.find_move(board)
                    if (
                        move_made == "error"
                        or chess.Move.from_uci(move_made) not in board.board.legal_moves
                    ):
                        break
                    board.push_move(move_made)
                board.switch_turn(is_first_run)
            if board.is_our_turn():
                best_move = board.get_best_move()
                board.push_move(best_move)
                control.play_move(board, best_move)
                board.start_opp_move_time()
                board.pos = analysis.get_board_position(board.board)
                board.switch_turn()
                if config_instance.lines > 0:
                    board.calc_thread = threading.Thread(target=board.analyze_board)
                    board.calc_thread.start()
    print("Game stopped\n")
    board.engine.quit()
    stop_game()
