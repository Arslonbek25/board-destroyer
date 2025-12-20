import threading
import time
import numpy as np

import analysis
import control
import detect
from board import Board
from debugger import DebugConfig, DebugRecorder, NullRecorder
import chess


def _now_ms() -> int:
    return int(time.time() * 1000)


def run(config, stop_game=None):
    DIFF_THRESHOLD = 1.7

    cfg = DebugConfig.from_config(config)
    cfg.diff_threshold = DIFF_THRESHOLD
    cfg.thumb_size = 160
    recorder = DebugRecorder(cfg) if cfg.enabled else NullRecorder()

    EXIT_REASON = "unknown"
    loop_id = 0

    restart_requested = False
    restart_reason = None
    restart_context = None
    restart_count = 0
    MAX_RESTARTS = 20
    opp_fail_streak = 0

    def _create_fresh_board():
        return Board(config)

    def _shutdown_board(b):
        try:
            if getattr(b, "engine", None) is not None:
                b.engine.quit()
        except Exception:
            pass

    def _request_restart(reason: str, context: dict):
        nonlocal restart_requested, restart_reason, restart_context
        restart_requested = True
        restart_reason = reason
        restart_context = context

    def _force_attach_session(board: Board):
        """
        Manual-restart equivalent:
        - capture
        - YOLO
        - set FEN
        - focus
        - sync diff baseline
        - initialize prev_pos
        """
        board.update()
        board.pos = detect.find_pieces(board, recorder=recorder)

        fen = analysis.get_fen(board.pos, board.turn)
        board.set_fen(fen)
        board.focus()

        recorder.event(
            "session_attached",
            fen=board.board.fen() if board.board else None,
            our_turn=bool(board.is_our_turn()),
        )
        recorder.event(
            "attach_summary",
            loop=loop_id,
            non_empty=int(np.count_nonzero(board.pos)) if board.pos is not None else 0,
        )

    board = None

    try:
        while config.game_running:
            if restart_count > MAX_RESTARTS:
                recorder.event("exit", reason="too_many_restarts", count=restart_count)
                EXIT_REASON = "too_many_restarts"
                break

            if board is not None:
                _shutdown_board(board)

            recorder.event("restart_begin", count=restart_count, reason=restart_reason)
            board = _create_fresh_board()

            try:
                _force_attach_session(board)
            except Exception as e:
                recorder.dump_exception(
                    e, tag="session_attach_exception", loop_id=loop_id
                )
                _request_restart("session_attach_exception", {"loop": loop_id})
                restart_count += 1
                recorder.event(
                    "restart_requested",
                    count=restart_count,
                    reason=restart_reason,
                    loop=loop_id,
                )
                continue

            # --- KICKSTART: if it's our turn at session start, play immediately ---
            if board.is_our_turn():
                best_move = board.get_best_move()
                board.push_move(best_move)

                play_move_ms = control.play_move(board, best_move)
                if play_move_ms is not None:
                    recorder.metric("ui.play_move", ms=play_move_ms)

                recorder.event(
                    "our_move_kickstart",
                    move=best_move,
                    fen=board.board.fen() if board.board else None,
                )

                board.pos = analysis.get_board_position(board.board)
                board.prev_pos = board.pos.copy()

                board.sync_diff_baseline()

                board.start_opp_move_time()
                board.switch_turn()
            # --- END KICKSTART ---

            last_changed_ms = _now_ms()
            last_yolo_ms = _now_ms()
            last_opp_move_ms = _now_ms()
            last_our_move_ms = _now_ms()

            changed_true_count = 0
            yolo_count = 0
            find_move_error_count = 0
            illegal_opp_move_count = 0
            exceptions_count = 0
            loop_broken = False

            opp_fail_streak = 0
            restart_requested = False
            restart_reason = None
            restart_context = None
            changed_true_count = 0
            yolo_count = 0
            find_move_error_count = 0
            illegal_opp_move_count = 0
            exceptions_count = 0

            while config.game_running and not board.game_over():
                if restart_requested:
                    break

                loop_id += 1
                loop_start = time.perf_counter()

                try:
                    board.update()
                except Exception as e:
                    exceptions_count += 1
                    EXIT_REASON = "main_loop_exception"
                    loop_broken = True
                    recorder.dump_exception(
                        e,
                        tag="main_loop_exception",
                        loop_id=loop_id,
                        fen=board.board.fen() if board.board else None,
                        our_turn=bool(board.is_our_turn()),
                        last_diff=float(getattr(board, "_last_diff_score", -1.0)),
                    )
                    recorder.dump_state(
                        board, tag="main_loop_exception", loop_id=loop_id
                    )
                    break

                if loop_id % 25 == 0:
                    recorder.event(
                        "heartbeat",
                        loop=loop_id,
                        fen=board.board.fen() if board.board else None,
                        our_turn=bool(board.is_our_turn()),
                        since_yolo_ms=_now_ms() - last_yolo_ms,
                        since_changed_ms=_now_ms() - last_changed_ms,
                        since_our_move_ms=_now_ms() - last_our_move_ms,
                        since_opp_move_ms=_now_ms() - last_opp_move_ms,
                        last_diff=float(getattr(board, "_last_diff_score", -1.0)),
                        counters={
                            "changed_true": changed_true_count,
                            "yolo": yolo_count,
                            "find_move_error": find_move_error_count,
                            "illegal_opp_move": illegal_opp_move_count,
                            "exceptions": exceptions_count,
                        },
                    )

                changed = board.board_changed_fast(threshold=DIFF_THRESHOLD)

                if not changed:
                    time.sleep(0.02)
                    loop_end = time.perf_counter()
                    recorder.metric(
                        "loop",
                        total_ms=(loop_end - loop_start) * 1000,
                        capture_ms=getattr(board, "last_capture_ms", None),
                        resize_ms=getattr(board, "last_resize_ms", None),
                        update_ms=getattr(board, "last_update_ms", None),
                    )
                    continue

                last_changed_ms = _now_ms()
                changed_true_count += 1
                try:
                    yolo_start = time.perf_counter()
                    board.pos = detect.find_pieces(board, recorder=recorder)
                    yolo_ms = (time.perf_counter() - yolo_start) * 1000
                    yolo_count += 1
                    last_yolo_ms = _now_ms()
                    recorder.metric("yolo", inference_ms=yolo_ms)
                except Exception as e:
                    exceptions_count += 1
                    EXIT_REASON = "detect_exception"
                    loop_broken = True
                    recorder.dump_exception(
                        e,
                        tag="detect_exception",
                        loop_id=loop_id,
                        fen=board.board.fen() if board.board else None,
                        our_turn=bool(board.is_our_turn()),
                        last_diff=float(getattr(board, "_last_diff_score", -1.0)),
                    )
                    recorder.dump_state(
                        board, tag="detect_exception", loop_id=loop_id
                    )
                    break

                is_first_run = False
                if board.pos_changed():
                    if not board.is_our_turn():
                        board.end_opp_move_time()
                        if not is_first_run:
                            move_made = analysis.find_move(board, recorder=recorder)
                            if move_made == "error":
                                opp_fail_streak += 1
                                find_move_error_count += 1
                                recorder.event(
                                    "opp_move_fail",
                                    kind="parse_error",
                                    streak=opp_fail_streak,
                                    loop=loop_id,
                                )
                                recorder.dump_state(
                                    board, tag="opp_move_fail", loop_id=loop_id
                                )
                                if opp_fail_streak >= 3:
                                    _request_restart(
                                        "opp_move_fail_streak_3",
                                        {
                                            "streak": opp_fail_streak,
                                            "fen": board.board.fen()
                                            if board.board
                                            else None,
                                            "moves": " ".join(
                                                [
                                                    m.uci()
                                                    for m in board.board.move_stack
                                                ]
                                            )
                                            if board.board
                                            else None,
                                            "loop": loop_id,
                                        },
                                    )
                                    break
                                time.sleep(0.02)
                                continue

                            try:
                                mv = chess.Move.from_uci(move_made)
                            except Exception:
                                opp_fail_streak += 1
                                find_move_error_count += 1
                                recorder.event(
                                    "opp_move_fail",
                                    kind="bad_uci",
                                    streak=opp_fail_streak,
                                    loop=loop_id,
                                    move_made=str(move_made),
                                )
                                recorder.dump_state(
                                    board, tag="opp_move_fail", loop_id=loop_id
                                )
                                if opp_fail_streak >= 3:
                                    _request_restart(
                                        "opp_move_fail_streak_3",
                                        {
                                            "streak": opp_fail_streak,
                                            "fen": board.board.fen()
                                            if board.board
                                            else None,
                                            "moves": " ".join(
                                                [
                                                    m.uci()
                                                    for m in board.board.move_stack
                                                ]
                                            )
                                            if board.board
                                            else None,
                                            "loop": loop_id,
                                        },
                                    )
                                    break
                                time.sleep(0.02)
                                continue

                            if mv not in board.board.legal_moves:
                                opp_fail_streak += 1
                                illegal_opp_move_count += 1
                                recorder.event(
                                    "opp_move_fail",
                                    kind="illegal",
                                    streak=opp_fail_streak,
                                    loop=loop_id,
                                    move=mv.uci(),
                                )
                                recorder.dump_state(
                                    board, tag="opp_move_fail", loop_id=loop_id
                                )
                                if opp_fail_streak >= 3:
                                    _request_restart(
                                        "opp_move_fail_streak_3",
                                        {
                                            "streak": opp_fail_streak,
                                            "fen": board.board.fen()
                                            if board.board
                                            else None,
                                            "moves": " ".join(
                                                [
                                                    m.uci()
                                                    for m in board.board.move_stack
                                                ]
                                            )
                                            if board.board
                                            else None,
                                            "loop": loop_id,
                                        },
                                    )
                                    break
                                time.sleep(0.02)
                                continue

                            opp_fail_streak = 0
                            board.push_move(move_made)
                            recorder.event(
                                "opp_move",
                                loop=loop_id,
                                move=move_made,
                                fen=board.board.fen() if board.board else None,
                            )
                            last_opp_move_ms = _now_ms()
                        board.switch_turn(is_first_run)
                    if board.is_our_turn():
                        try:
                            best_move = board.get_best_move()
                        except chess.engine.EngineTerminatedError as e:
                            recorder.event(
                                "engine_died",
                                loop=loop_id,
                                fen=board.board.fen() if board.board else None,
                                our_turn=bool(board.is_our_turn()),
                            )
                            recorder.dump_exception(
                                e,
                                tag="engine_died",
                                loop_id=loop_id,
                                fen=board.board.fen() if board.board else None,
                            )
                            try:
                                board.restart_engine()
                                best_move = board.get_best_move()
                                recorder.event("engine_recovered", loop=loop_id)
                            except Exception as e2:
                                recorder.dump_exception(
                                    e2, tag="engine_recover_failed", loop_id=loop_id
                                )
                                _request_restart(
                                    "engine_recover_failed", {"loop": loop_id}
                                )
                                break
                        board.push_move(best_move)
                        play_move_ms = control.play_move(board, best_move)
                        last_our_move_ms = _now_ms()
                        if play_move_ms is not None:
                            recorder.metric("ui.play_move", ms=play_move_ms)
                        recorder.event(
                            "our_move",
                            loop=loop_id,
                            move=best_move,
                            fen=board.board.fen() if board.board else None,
                        )

                        expected_pos = analysis.get_board_position(board.board)

                        for _ in range(4):
                            board.update()
                            board.pos = detect.find_pieces(board, recorder=recorder)
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

                loop_end = time.perf_counter()
                recorder.metric(
                    "loop",
                    total_ms=(loop_end - loop_start) * 1000,
                    capture_ms=getattr(board, "last_capture_ms", None),
                    resize_ms=getattr(board, "last_resize_ms", None),
                    update_ms=getattr(board, "last_update_ms", None),
                )

            if restart_requested:
                restart_count += 1
                event_fields = {
                    "count": restart_count,
                    "reason": restart_reason,
                    "fen_at_restart": board.board.fen() if board and board.board else None,
                    "our_turn_at_restart": bool(board.is_our_turn()) if board else None,
                }
                if restart_context:
                    event_fields.update(restart_context)
                recorder.event("restart_requested", **event_fields)
                continue

            if not loop_broken:
                if board.game_over():
                    EXIT_REASON = "game_over"
                elif not getattr(config, "game_running", True):
                    EXIT_REASON = "stopped"
                recorder.event(
                    "restart_done",
                    count=restart_count,
                    reason="session_ended_normally",
                )
            break
    except Exception as e:
        EXIT_REASON = "main_loop_exception"
        recorder.dump_exception(
            e,
            tag="main_loop_exception",
            loop_id=loop_id,
            fen=board.board.fen() if board and board.board else None,
            our_turn=bool(board.is_our_turn()) if board else None,
            last_diff=float(getattr(board, "_last_diff_score", -1.0))
            if board
            else None,
        )
        if board:
            recorder.dump_state(board, tag="main_loop_exception", loop_id=loop_id)
    finally:
        recorder.close(EXIT_REASON, loop_id)
        print(
            f"Game stopped | reason={EXIT_REASON} | run_dir={recorder.run_dir} | loop={loop_id}"
        )
        if board is not None:
            _shutdown_board(board)
        if callable(stop_game):
            stop_game()
