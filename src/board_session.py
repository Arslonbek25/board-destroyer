import time

import chess
import cv2
import mss
import numpy as np
import pyautogui as pg

from clock import Clock
from config import Color
from vision import getBoardCorners


class BoardSession:
    IMG_SIZE = 640

    def __init__(self, config):
        self.color = config.color
        self.clock = Clock(config)
        self.opp_move_time = config.time_control.min_time
        self.sct = mss.mss()
        self._init_board()
        self.prev_pos = None
        self.board: chess.Board | None = None
        self.obvious_move = False
        self.opp_move_start_time = time.time()
        self._prev_thumb = None
        self._thumb_size = 256

    def update(self):
        self.last_update = time.time()
        self._capture_screenshot(cropped=True)
        self._resize()

    def board_changed_fast(self, threshold: float = 2.2) -> bool:
        """
        Fast + reliable board diff.
        Key property: baseline only updates when frame is 'stable' (< threshold),
        so slow/gradual changes can't slip under the threshold forever.
        """
        img = self.img
        if img is None:
            return True

        gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        thumb = cv2.resize(
            gray,
            (self._thumb_size, self._thumb_size),
            interpolation=cv2.INTER_AREA,
        )

        if self._prev_thumb is None:
            self._prev_thumb = thumb
            return True

        diff = cv2.absdiff(thumb, self._prev_thumb)
        score = float(diff.mean())

        # IMPORTANT: Only advance baseline when the scene is stable.
        if score < threshold:
            self._prev_thumb = thumb

        return score >= threshold

    def sync_diff_baseline(self) -> None:
        """
        Make the diff baseline equal to the current screenshot.
        Call this right after our own move is applied on screen.
        """
        if self.img is None:
            return
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGRA2GRAY)
        self._prev_thumb = cv2.resize(
            gray,
            (self._thumb_size, self._thumb_size),
            interpolation=cv2.INTER_AREA,
        )

    def set_fen(self, fen):
        # One-shot: subsequent calls are silently ignored. Vision-derived FEN
        # has no reliable castling info; chess.Board infers what it can from
        # piece placement, which is the most we can do without history.
        if self.board is None:
            self.board = chess.Board()
            self.board.set_fen(fen)

    def get_move_time(self):
        if self.obvious_move:
            self.clock.opponent_total_time += self.opp_move_time
            return self.clock.tc.min_time

        num_pieces = len(self.board.piece_map())
        move_time = self.clock.calculate_move_time(self.opp_move_time, num_pieces)

        return move_time

    def end_opp_move_time(self):
        self.opp_move_time = self.last_update - self.opp_move_start_time

    def start_opp_move_time(self):
        self.opp_move_start_time = time.time()

    def commit_pos_baseline(self):
        """Snapshot the current YOLO position as the next diff baseline."""
        self.prev_pos = np.copy(self.pos)

    def complete_our_move(self):
        """After our move has rendered on screen: sync diff baseline,
        start opp's clock, snapshot pos for the next diff."""
        self.sync_diff_baseline()
        self.start_opp_move_time()
        self.commit_pos_baseline()

    def complete_opp_move(self, uci: str):
        """After opp's move has been parsed and validated: push to
        chess.Board (which sets obvious_move), snapshot pos baseline."""
        self.push_opp_move(uci)
        self.commit_pos_baseline()

    def game_over(self):
        return self.board.is_game_over() if self.board else False

    def pos_changed(self):
        return not np.array_equal(self.prev_pos, self.pos)

    def is_our_turn(self) -> bool:
        # Before attach, chess.Board doesn't exist yet — assume our turn at session start.
        if self.board is None:
            return True
        we_are_white = self.color == Color.WHITE
        return self.board.turn == we_are_white

    def push_our_move(self, uci: str) -> None:
        _, is_capture = self._push(uci)
        self.obvious_move = is_capture

    def push_opp_move(self, uci: str) -> None:
        mv, is_capture = self._push(uci)
        # The "obvious" heuristic for opp moves: capture / check / pawn-creates-threat
        # → respond fast because the move forces us. (See clock.get_move_time.)
        self.obvious_move = is_capture or self.board.is_check() or self._is_pawn_threat(mv)

    def _push(self, uci: str) -> tuple[chess.Move, bool]:
        mv = chess.Move.from_uci(uci)
        is_capture = (
            self.board.is_capture(mv)
            and self.board.piece_at(mv.from_square).piece_type != chess.PAWN
        )
        self.board.push(mv)
        return mv, is_capture

    def _is_pawn_threat(self, mv: chess.Move) -> bool:
        landed = self.board.piece_at(mv.to_square)
        if landed is None or landed.piece_type != chess.PAWN:
            return False
        return any(
            self.board.piece_at(sq) and self.board.piece_at(sq).color == self.board.turn
            for sq in self.board.attacks(mv.to_square)
        )

    def _init_board(self):
        for _ in range(30):
            try:
                self._find_board()
                return
            except ValueError:
                # vision.getBoardCorners raises ValueError when the contour
                # isn't a 4-corner square — transient during page render.
                time.sleep(0.1)
        raise RuntimeError("could not find chess board on screen after 30 attempts")

    def _find_board(self):
        self._capture_screenshot()
        self._find_corners()
        self._set_scale()
        self._crop_to_board()
        self.sq_size_orig = self._get_sq_size()
        self._resize()
        self.sq_size = self._get_sq_size()

    def _capture_screenshot(self, cropped=False):
        if not cropped:
            monitor = self.sct.monitors[1]
        else:
            monitor = {
                "top": self.corners[0, 1] / 2,
                "left": self.corners[0, 0] / 2,
                "width": (self.corners[2, 1] - self.corners[0, 1]) / 2,
                "height": (self.corners[2, 0] - self.corners[0, 0]) / 2,
            }
        self.img = np.array(self.sct.grab(monitor))

    def _find_corners(self):
        self.corners = getBoardCorners(self.img)

    def _get_sq_size(self):
        return sum(self.img.shape[:2]) / 16

    def _crop_to_board(self):
        self.img = self.img[
            self.corners[0, 1] : self.corners[2, 1],
            self.corners[0, 0] : self.corners[2, 0],
        ]

    def _resize(self):
        scale = BoardSession.IMG_SIZE / self.img.shape[0]
        self.img = cv2.resize(
            self.img, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR
        )

    def _set_scale(self):
        self.scale = self.img.shape[0] / pg.size()[1]
