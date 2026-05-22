import threading
import time
import numpy as np

import analysis
import control
import detect
from board import Board
import chess


def run(config, stop_game=None):
    DIFF_THRESHOLD = 1.7

    EXIT_REASON = "unknown"

    restart_requested = False
    restart_count = 0
    MAX_RESTARTS = 20
    opp_fail_streak = 0

    def _create_fresh_board():
        return Board(config)

    def _shutdown_board(b):
        if getattr(b, "engine", None) is not None:
            b.engine.quit()

    def _request_restart():
        nonlocal restart_requested
        restart_requested = True

    def _force_attach_session(board: Board):
        board.update()
        board.pos = detect.find_pieces(board)
        fen = analysis.get_fen(board.pos, board.turn)
        board.set_fen(fen)
        board.focus()

    board = None

    try:
        while config.game_running:
            if restart_count > MAX_RESTARTS:
                EXIT_REASON = "too_many_restarts"
                break

            if board is not None:
                _shutdown_board(board)

            board = _create_fresh_board()

            try:
                _force_attach_session(board)
            except Exception:
                _request_restart()
                restart_count += 1
                continue

            # --- KICKSTART: if it's our turn at session start, play immediately ---
            if board.is_our_turn():
                best_move = board.get_best_move()
                board.push_move(best_move)
                control.play_move(board, best_move)

                board.pos = analysis.get_board_position(board.board)
                board.prev_pos = board.pos.copy()
                board.sync_diff_baseline()
                board.start_opp_move_time()
                board.switch_turn()
            # --- END KICKSTART ---

            opp_fail_streak = 0
            restart_requested = False

            while config.game_running and not board.game_over():
                if restart_requested:
                    break

                try:
                    board.update()
                except Exception:
                    EXIT_REASON = "main_loop_exception"
                    break

                changed = board.board_changed_fast(threshold=DIFF_THRESHOLD)

                if not changed:
                    time.sleep(0.02)
                    continue

                try:
                    board.pos = detect.find_pieces(board)
                except Exception:
                    EXIT_REASON = "detect_exception"
                    break

                is_first_run = False
                if board.pos_changed():
                    if not board.is_our_turn():
                        board.end_opp_move_time()
                        if not is_first_run:
                            move_made = analysis.find_move(board.prev_pos, board.pos)
                            if move_made == "error":
                                opp_fail_streak += 1
                                if opp_fail_streak >= 3:
                                    _request_restart()
                                    break
                                time.sleep(0.02)
                                continue

                            try:
                                mv = chess.Move.from_uci(move_made)
                            except Exception:
                                opp_fail_streak += 1
                                if opp_fail_streak >= 3:
                                    _request_restart()
                                    break
                                time.sleep(0.02)
                                continue

                            if mv not in board.board.legal_moves:
                                opp_fail_streak += 1
                                if opp_fail_streak >= 3:
                                    _request_restart()
                                    break
                                time.sleep(0.02)
                                continue

                            opp_fail_streak = 0
                            board.push_move(move_made)
                        board.switch_turn(is_first_run)
                    if board.is_our_turn():
                        try:
                            best_move = board.get_best_move()
                        except chess.engine.EngineTerminatedError:
                            try:
                                board.restart_engine()
                                best_move = board.get_best_move()
                            except Exception:
                                _request_restart()
                                break
                        board.push_move(best_move)
                        control.play_move(board, best_move)

                        expected_pos = analysis.get_board_position(board.board)

                        for _ in range(4):
                            board.update()
                            board.pos = detect.find_pieces(board)
                            if np.array_equal(board.pos, expected_pos):
                                break
                            time.sleep(0.03)

                        if not np.array_equal(board.pos, expected_pos):
                            board.pos = expected_pos

                        board.sync_diff_baseline()
                        board.start_opp_move_time()
                        board.switch_turn()

                        if config.lines > 0:
                            board.calc_thread = threading.Thread(
                                target=board.analyze_board
                            )
                            board.calc_thread.start()

            if restart_requested:
                restart_count += 1
                continue

            if board.game_over():
                EXIT_REASON = "game_over"
            elif not config.game_running:
                EXIT_REASON = "stopped"
            break
    finally:
        print(f"Game stopped | reason={EXIT_REASON}")
        if board is not None:
            _shutdown_board(board)
        if callable(stop_game):
            stop_game()
