import time
from enum import Enum, auto
from typing import Callable

import chess
import numpy as np

import control
import position
import vision
from board_session import BoardSession
from config import Config
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


def attach(board: BoardSession) -> None:
    board.update()
    board.pos = vision.find_pieces(board)
    board.set_fen(position.get_fen(board.pos, board.color))
    board.prev_pos = board.pos.copy()
    control.focus(board)


def parse_opp_move(prev_pos, pos, chess_board) -> chess.Move | None:
    raw = position.find_move(prev_pos, pos)
    if raw == "error":
        return None
    try:
        mv = chess.Move.from_uci(raw)
    except ValueError:
        return None
    if mv not in chess_board.legal_moves:
        return None
    return mv


def play_our_move(board: BoardSession, engine: Engine, config: Config) -> bool:
    """Play our move. Returns True if render verification failed (restart)."""
    best_move = None
    if board.board.move_stack:
        best_move = engine.try_anticipated(
            board.board.move_stack[-1], board=board.board
        )

    if best_move is None:
        t = None if board.clock.tc.depth else board.get_move_time()
        best_move = engine.best_move(
            board.board, time=t, depth=board.clock.tc.depth
        )

    board.push_our_move(best_move)
    control.play_move(board, best_move)

    expected_pos = position.get_board_position(board.board)
    for _ in range(RENDER_RETRIES):
        board.update()
        board.pos = vision.find_pieces(board)
        if np.array_equal(board.pos, expected_pos):
            break
        time.sleep(RENDER_RETRY_SLEEP)
    if not np.array_equal(board.pos, expected_pos):
        return True

    board.sync_diff_baseline()
    board.start_opp_move_time()
    board.commit_pos_baseline()

    engine.anticipate(board.board, config.lines)
    return False


def play_session(config: Config) -> bool:
    """Run one attach-to-restart session. Returns True if a restart is needed."""
    board = BoardSession(config)
    engine = Engine(config.time_control.skill_level)
    try:
        attach(board)

        state = State.OUR_TURN if board.is_our_turn() else State.AWAITING_OPP
        opp_fail_streak = 0

        while config.game_running and not board.game_over():
            if state is State.OUR_TURN:
                if play_our_move(board, engine, config):
                    return True
                state = State.AWAITING_OPP
                continue

            board.update()
            if not board.board_changed_fast(threshold=DIFF_THRESHOLD):
                time.sleep(IDLE_SLEEP)
                continue

            board.pos = vision.find_pieces(board)
            if not board.pos_changed():
                continue

            board.end_opp_move_time()
            mv = parse_opp_move(board.prev_pos, board.pos, board.board)
            if mv is None:
                opp_fail_streak += 1
                if opp_fail_streak >= OPP_FAIL_LIMIT:
                    return True
                time.sleep(IDLE_SLEEP)
                continue

            opp_fail_streak = 0
            board.push_opp_move(mv.uci())
            board.commit_pos_baseline()
            state = State.OUR_TURN

        return False
    finally:
        engine.quit()


def run(config: Config, stop_game: Callable[[], None] | None = None) -> None:
    restart_count = 0

    try:
        while config.game_running and restart_count <= MAX_RESTARTS:
            try:
                restart = play_session(config)
            except Exception:
                restart_count += 1
                if restart_count > MAX_RESTARTS:
                    # Out of restart slots — surface the underlying error
                    # rather than exiting silently.
                    raise
                continue

            if restart:
                restart_count += 1
                continue

            break
    finally:
        if callable(stop_game):
            stop_game()
