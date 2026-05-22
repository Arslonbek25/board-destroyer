import time
from enum import Enum, auto

import chess
import numpy as np

import analysis
import control
import detect
from board_session import BoardSession
from engine import Engine


DIFF_THRESHOLD = 1.7
MAX_RESTARTS = 20
OPP_FAIL_LIMIT = 3
RENDER_RETRIES = 4
RENDER_RETRY_SLEEP = 0.03
IDLE_SLEEP = 0.02


class State(Enum):
    AWAITING_OPP = auto()
    OUR_TURN = auto()


def _attach(board: BoardSession) -> None:
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


def _play_our_move(board: BoardSession, engine: Engine, config) -> None:
    best_move = None
    if board.board.move_stack:
        best_move = engine.try_anticipated(board.board.move_stack[-1])

    if best_move is None:
        t = None if board.clock.tc.depth else board.get_move_time()
        best_move = engine.best_move(
            board.board, time=t, depth=board.clock.tc.depth
        )

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

    engine.anticipate(board.board, config.lines)


def _play_session(config) -> tuple[BoardSession, bool]:
    """Run one attach-to-restart session. Returns (board, restart_requested)."""
    board = BoardSession(config)
    engine = Engine(config.time_control.skill_level)
    try:
        _attach(board)

        state = State.OUR_TURN if board.is_our_turn() else State.AWAITING_OPP
        opp_fail_streak = 0

        while config.game_running and not board.game_over():
            if state is State.OUR_TURN:
                _play_our_move(board, engine, config)
                state = State.AWAITING_OPP
                continue

            board.update()
            if not board.board_changed_fast(threshold=DIFF_THRESHOLD):
                time.sleep(IDLE_SLEEP)
                continue

            board.pos = detect.find_pieces(board)
            if not board.pos_changed():
                continue

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
            state = State.OUR_TURN

        return board, False
    finally:
        engine.quit()


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
        if callable(stop_game):
            stop_game()
