import threading
import time
import traceback
import numpy as np

import analysis
import control
import detect
from board import Board
from telemetry import now_ms, log_jsonl, ensure_dir
import chess


def run(config, stop_game=None):
    board = Board(config)
    DEBUG = True
    loop_id = 0
    DIFF_THRESHOLD = 1.7  # start here since it works for you; after diff fix you can try 1.9–2.2

    ensure_dir("debug")

    EXIT_REASON = "unknown"
    loop_id = 0

    last_changed_ms = now_ms()
    last_yolo_ms = now_ms()
    last_opp_move_ms = now_ms()
    last_our_move_ms = now_ms()

    changed_true_count = 0
    yolo_count = 0
    opp_move_error_count = 0
    detect_exception_count = 0

    def dump_state(tag: str):
        try:
            ts = int(time.time() * 1000)
            board.save_screenshot(f"debug/{ts}_{tag}.png")
            if board.pos is not None:
                np.save(f"debug/{ts}_{tag}_pos.npy", board.pos)
            if board.prev_pos is not None:
                np.save(f"debug/{ts}_{tag}_prev_pos.npy", board.prev_pos)
            if board.board is not None:
                with open(f"debug/{ts}_{tag}_fen.txt", "w") as f:
                    f.write(board.board.fen() + "\n")
                    f.write("turn_var=" + str(board.turn) + "\n")
                    f.write("color=" + str(board.color) + "\n")
                    f.write("board_turn=" + str(board.board.turn) + "\n")
                    f.write("moves=" + " ".join([m.uci() for m in board.board.move_stack]) + "\n")
        except Exception as e:
            print(f"[DUMP ERROR] {e}")

    try:
        while config.game_running and not board.game_over():
            loop_id += 1
            loop_start = time.perf_counter()

            board.update()

            # Liveness snapshot (cheap)
            if loop_id % 25 == 0:
                log_jsonl("debug/heartbeat.jsonl", {
                    "ts": now_ms(),
                    "loop": loop_id,
                    "game_running": bool(config.game_running),
                    "game_over": bool(board.game_over()),
                    "turn": str(board.turn),
                    "our_turn": bool(board.is_our_turn()),
                    "fen": board.board.fen() if board.board else None,
                    "since_changed_ms": now_ms() - last_changed_ms,
                    "since_yolo_ms": now_ms() - last_yolo_ms,
                    "since_opp_move_ms": now_ms() - last_opp_move_ms,
                    "since_our_move_ms": now_ms() - last_our_move_ms,
                    "changed_true_count": changed_true_count,
                    "yolo_count": yolo_count,
                    "opp_move_error_count": opp_move_error_count,
                    "detect_exception_count": detect_exception_count,
                    "last_diff": float(getattr(board, "_last_diff_score", -1.0)),
                })

            changed = board.board_changed_fast(threshold=DIFF_THRESHOLD)

            if changed:
                last_changed_ms = now_ms()
                changed_true_count += 1
                try:
                    board.pos = detect.find_pieces(board)
                    yolo_count += 1
                    last_yolo_ms = now_ms()
                except Exception:
                    detect_exception_count += 1
                    EXIT_REASON = "detect.find_pieces exception"
                    # Dump a screenshot + traceback
                    try:
                        board.save_screenshot(f"debug/{now_ms()}_detect_exception.png")
                    except Exception:
                        pass
                    log_jsonl("debug/exceptions.jsonl", {
                        "ts": now_ms(),
                        "loop": loop_id,
                        "where": "detect.find_pieces",
                        "traceback": traceback.format_exc(),
                        "fen": board.board.fen() if board.board else None,
                        "turn": str(board.turn),
                        "our_turn": bool(board.is_our_turn()),
                        "last_diff": float(getattr(board, "_last_diff_score", -1.0)),
                    })
                    break
            else:
                time.sleep(0.02)
                loop_end = time.perf_counter()
                print(f"[TOTAL LOOP] {(loop_end - loop_start)*1000:.2f} ms")
                continue

            if DEBUG:
                turn_now = board.turn
                our_turn = board.is_our_turn()
                fen = board.board.fen() if board.board else "None"
                print(f"[LOOP {loop_id}] changed=True diff={board._last_diff_score:.3f} turn={turn_now} our_turn={our_turn} fen={fen}")

            if DEBUG:
                print(f"[YOLO] pos_loaded pieces={int(np.sum(board.pos != 0)) if board.pos is not None else -1}")

            is_first_run = board.prev_pos is None
            if is_first_run:
                fen = analysis.get_fen(board.pos, board.turn)
                board.set_fen(fen)
                board.focus()
            if board.pos_changed():
                if DEBUG:
                    diff_cnt = int(np.sum(board.prev_pos != board.pos)) if (board.prev_pos is not None and board.pos is not None) else -1
                    print(f"[POS_CHANGED] diff_cnt={diff_cnt} our_turn={board.is_our_turn()} turn={board.turn}")
                if not board.is_our_turn():
                    board.end_opp_move_time()
                    if not is_first_run:
                        move_made = analysis.find_move(board)
                        opp_move_error_count += 1

                        if move_made == "error":
                            print("[OPP MOVE] find_move returned error")
                            dump_state("opp_move_error")
                            time.sleep(0.05)
                            continue

                        uci_move = chess.Move.from_uci(move_made)
                        if uci_move not in board.board.legal_moves:
                            print(f"[OPP MOVE] illegal move from vision: {move_made}")
                            dump_state("opp_move_illegal")

                            # Retry once after a short settle (one extra YOLO read)
                            time.sleep(0.05)
                            board.update()
                            board.pos = detect.find_pieces(board)
                            move_made2 = analysis.find_move(board)

                            if move_made2 == "error":
                                print("[OPP MOVE] retry still error")
                                dump_state("opp_move_retry_error")
                                time.sleep(0.05)
                                continue

                            uci_move2 = chess.Move.from_uci(move_made2)
                            if uci_move2 not in board.board.legal_moves:
                                print(f"[OPP MOVE] retry still illegal: {move_made2}")
                                dump_state("opp_move_retry_illegal")
                                time.sleep(0.05)
                                continue

                            move_made = move_made2
                            uci_move = uci_move2

                        print(f"[OPP MOVE] accepted {move_made}")
                        board.push_move(move_made)
                    board.switch_turn(is_first_run)
                if board.is_our_turn():
                    best_move = board.get_best_move()
                    board.push_move(best_move)
                    control.play_move(board, best_move)
                    last_our_move_ms = now_ms()

                    # IMPORTANT: resync from SCREEN so prev_pos matches what YOLO will see next.
                    expected_pos = analysis.get_board_position(board.board)

                    # Try a few times to let the UI settle and YOLO see the post-move board.
                    for _ in range(4):
                        board.update()
                        board.pos = detect.find_pieces(board)
                        if np.array_equal(board.pos, expected_pos):
                            break
                        time.sleep(0.03)

                    # If still not identical, fall back to the engine expected position to keep internal state consistent.
                    if not np.array_equal(board.pos, expected_pos):
                        board.pos = expected_pos

                    # Reset diff baseline to the post-move screenshot so diff doesn't fire on our own move.
                    board.sync_diff_baseline()

                    board.start_opp_move_time()
                    board.switch_turn()

                    if config.lines > 0:
                        board.calc_thread = threading.Thread(target=board.analyze_board)
                        board.calc_thread.start()

            loop_end = time.perf_counter()
            print(f"[TOTAL LOOP] {(loop_end - loop_start)*1000:.2f} ms")

    except Exception:
        EXIT_REASON = "main loop exception"
        try:
            board.save_screenshot(f"debug/{now_ms()}_main_exception.png")
        except Exception:
            pass
        log_jsonl("debug/exceptions.jsonl", {
            "ts": now_ms(),
            "loop": loop_id,
            "where": "main.py run()",
            "traceback": traceback.format_exc(),
        })
    finally:
        print(f"Game stopped | reason={EXIT_REASON} | loop={loop_id}")
        try:
            board.engine.quit()
        except Exception:
            pass
        stop_game()
