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
    cfg.thumb_size = 256
    recorder = DebugRecorder(cfg) if cfg.enabled else NullRecorder()

    EXIT_REASON = "unknown"
    loop_id = 0

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

    board = Board(config)

    try:
        while config.game_running and not board.game_over():
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
                recorder.dump_state(board, tag="main_loop_exception", loop_id=loop_id)
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
                recorder.dump_state(board, tag="detect_exception", loop_id=loop_id)
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
                        move_made = analysis.find_move(board, recorder=recorder)
                        if move_made == "error":
                            find_move_error_count += 1
                            EXIT_REASON = "opp_move_parse_error"
                            recorder.event(
                                "opp_move_parse_error",
                                loop=loop_id,
                                fen=board.board.fen() if board.board else None,
                                our_turn=bool(board.is_our_turn()),
                            )
                            recorder.dump_state(
                                board, tag="opp_move_parse_error", loop_id=loop_id
                            )
                            time.sleep(0.05)
                            continue

                        uci_move = chess.Move.from_uci(move_made)
                        if uci_move not in board.board.legal_moves:
                            illegal_opp_move_count += 1
                            EXIT_REASON = "opp_move_illegal"
                            recorder.event(
                                "opp_move_illegal",
                                loop=loop_id,
                                move=move_made,
                                fen=board.board.fen() if board.board else None,
                            )
                            recorder.dump_state(
                                board, tag="opp_move_illegal", loop_id=loop_id
                            )

                            time.sleep(0.05)
                            board.update()
                            try:
                                yolo_start = time.perf_counter()
                                board.pos = detect.find_pieces(
                                    board, recorder=recorder
                                )
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
                                    last_diff=float(
                                        getattr(board, "_last_diff_score", -1.0)
                                    ),
                                )
                                recorder.dump_state(
                                    board, tag="detect_exception", loop_id=loop_id
                                )
                                break
                            move_made2 = analysis.find_move(board, recorder=recorder)

                            if move_made2 == "error":
                                find_move_error_count += 1
                                EXIT_REASON = "opp_move_parse_error"
                                recorder.event(
                                    "opp_move_parse_error",
                                    loop=loop_id,
                                    fen=board.board.fen() if board.board else None,
                                    our_turn=bool(board.is_our_turn()),
                                    retry=True,
                                )
                                recorder.dump_state(
                                    board, tag="opp_move_retry_error", loop_id=loop_id
                                )
                                time.sleep(0.05)
                                continue

                            uci_move2 = chess.Move.from_uci(move_made2)
                            if uci_move2 not in board.board.legal_moves:
                                illegal_opp_move_count += 1
                                EXIT_REASON = "opp_move_illegal"
                                recorder.event(
                                    "opp_move_illegal",
                                    loop=loop_id,
                                    move=move_made2,
                                    fen=board.board.fen() if board.board else None,
                                    retry=True,
                                )
                                recorder.dump_state(
                                    board,
                                    tag="opp_move_retry_illegal",
                                    loop_id=loop_id,
                                )
                                time.sleep(0.05)
                                continue

                            move_made = move_made2
                            uci_move = uci_move2

                        recorder.event(
                            "opp_move",
                            loop=loop_id,
                            move=move_made,
                            fen=board.board.fen() if board.board else None,
                        )
                        board.push_move(move_made)
                        last_opp_move_ms = _now_ms()
                    board.switch_turn(is_first_run)
                if board.is_our_turn():
                    best_move = board.get_best_move()
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
                        board.calc_thread = threading.Thread(target=board.analyze_board)
                        board.calc_thread.start()

            loop_end = time.perf_counter()
            recorder.metric(
                "loop",
                total_ms=(loop_end - loop_start) * 1000,
                capture_ms=getattr(board, "last_capture_ms", None),
                resize_ms=getattr(board, "last_resize_ms", None),
                update_ms=getattr(board, "last_update_ms", None),
            )

        if not loop_broken:
            if board.game_over():
                EXIT_REASON = "game_over"
            elif not getattr(config, "game_running", True):
                EXIT_REASON = "stopped"
    except Exception as e:
        EXIT_REASON = "main_loop_exception"
        exceptions_count += 1
        loop_broken = True
        recorder.dump_exception(
            e,
            tag="main_loop_exception",
            loop_id=loop_id,
            fen=board.board.fen() if board.board else None,
            our_turn=bool(board.is_our_turn()),
            last_diff=float(getattr(board, "_last_diff_score", -1.0)),
        )
        recorder.dump_state(board, tag="main_loop_exception", loop_id=loop_id)
    finally:
        recorder.close(EXIT_REASON, loop_id)
        print(
            f"Game stopped | reason={EXIT_REASON} | run_dir={recorder.run_dir} | loop={loop_id}"
        )
        try:
            board.engine.quit()
        except Exception:
            pass
        if callable(stop_game):
            stop_game()
