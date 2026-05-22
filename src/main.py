import threading
import time

import chess
import numpy as np

import analysis
import control
import detect
from board import Board


DIFF_THRESHOLD = 1.7
MAX_RESTARTS = 20
OPP_FAIL_LIMIT = 3
RENDER_RETRIES = 4
RENDER_RETRY_SLEEP = 0.03
IDLE_SLEEP = 0.02


def _attach(board: Board) -> None:
    board.update()
    board.pos = detect.find_pieces(board)
    board.set_fen(analysis.get_fen(board.pos, board.turn))
    board.prev_pos = board.pos.copy()
    board.focus()


def _parse_opp_move(prev_pos, pos, chess_board) -> chess.Move | None:
    raw = analysis.find_move(prev_pos, pos)
    if raw == "error":
        return None
    try:
        mv = chess.Move.from_uci(raw)
    except ValueError:
        return None
    if mv not in chess_board.legal_moves:
        return None
    return mv


def _play_our_move(board: Board, config) -> None:
    best_move = board.get_best_move()
    board.push_move(best_move)
    control.play_move(board, best_move)

    expected_pos = analysis.get_board_position(board.board)
    for _ in range(RENDER_RETRIES):
        board.update()
        board.pos = detect.find_pieces(board)
        if np.array_equal(board.pos, expected_pos):
            break
        time.sleep(RENDER_RETRY_SLEEP)
    if not np.array_equal(board.pos, expected_pos):
        board.pos = expected_pos

    board.sync_diff_baseline()
    board.start_opp_move_time()
    board.switch_turn()

    if config.lines > 0:
        board.calc_thread = threading.Thread(target=board.analyze_board)
        board.calc_thread.start()


def _play_session(config) -> tuple[Board, bool]:
    """Run one attach-to-restart session. Returns (board, restart_requested)."""
    board = Board(config)
    _attach(board)

    if board.is_our_turn():
        _play_our_move(board, config)

    opp_fail_streak = 0
    while config.game_running and not board.game_over():
        board.update()
        if not board.board_changed_fast(threshold=DIFF_THRESHOLD):
            time.sleep(IDLE_SLEEP)
            continue

        board.pos = detect.find_pieces(board)
        if not board.pos_changed():
            continue

        if not board.is_our_turn():
            board.end_opp_move_time()
            mv = _parse_opp_move(board.prev_pos, board.pos, board.board)
            if mv is None:
                opp_fail_streak += 1
                if opp_fail_streak >= OPP_FAIL_LIMIT:
                    return board, True
                time.sleep(IDLE_SLEEP)
                continue
            opp_fail_streak = 0
            board.push_move(mv.uci())
            board.switch_turn()

        if board.is_our_turn():
            _play_our_move(board, config)

    return board, False


def run(config, stop_game=None):
    board = None
    restart_count = 0
    exit_reason = "stopped"

    try:
        while config.game_running and restart_count <= MAX_RESTARTS:
            try:
                board, restart = _play_session(config)
            except Exception:
                restart_count += 1
                continue

            if restart:
                restart_count += 1
                continue

            exit_reason = "game_over" if board.game_over() else "stopped"
            break

        if restart_count > MAX_RESTARTS:
            exit_reason = "too_many_restarts"
    finally:
        print(f"Game stopped | reason={exit_reason}")
        if board is not None and getattr(board, "engine", None) is not None:
            board.engine.quit()
        if callable(stop_game):
            stop_game()
