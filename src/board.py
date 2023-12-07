import time
from datetime import datetime

import chess
import chess.engine
import cv2
import mss
import numpy as np
import pyautogui as pg

import control
from clock import Clock
from detect import getBoardCorners


class Board:
    def __init__(self, util=False):
        self.IMG_SIZE = 640
        self.sct = mss.mss()
        if not util:
            self.turn = control.get_turn()
            self.color = control.get_color()
            self.timecontrol = control.get_timecontrol()
            self.clock = Clock(self.timecontrol)
            self._init_engine()
        self._init_board()
        self.prev_pos = None
        self.board = None
        self.opp_move_start_time = None
        self.opp_move_time = self.clock.tc.min_time
        self.obvious_move = False

    def update(self):
        self.last_update = time.time()
        self._capture_screenshot(cropped=True)
        self._resize()

    def set_fen(self, fen):
        if self.board is None:
            self.board = chess.Board()
            self.board.set_fen(fen)
            try:
                self.board.set_castling_fen("KQkq")
            except ValueError:
                pass

    def save_screenshot(self, filename=None):
        if not filename:
            now = datetime.now()
            id = now.strftime("%Y%m%d_%H%M%S_%f")
            filename = f"screenshots/screenshot{id}.png"
        cv2.imwrite(filename, self.img)

    def get_move_time(self):
        if self.obvious_move:
            return self.clock.tc.min_time

        num_pieces = len(self.board.piece_map())
        newtime = self.clock.calculate_move_time(self.opp_move_time, num_pieces)

        return newtime

    def track_opp_move_time(self):
        self.opp_move_time = self.last_update - self.opp_move_start_time

        print(self.opp_move_time)

    def start_opp_move_time(self):
        self.opp_move_start_time = time.time()

    def get_best_move(self):
        result = self.engine.play(
            self.board, chess.engine.Limit(time=self.get_move_time())
        )
        return str(result.move)

    def switch_turn(self, is_first_run=False):
        if not is_first_run:
            self.turn = "b" if self.turn == "w" else "w"
        self.prev_pos = np.copy(self.pos)

    def game_over(self):
        return self.board.is_game_over() if self.board else False

    def pos_changed(self):
        return not np.array_equal(self.prev_pos, self.pos)

    def is_our_turn(self):
        return self.color == self.turn

    def push_move(self, move):
        uci = chess.Move.from_uci(move)
        is_capture = self.board.is_capture(uci)

        self.board.push_san(move)

        if not self.is_our_turn():
            is_check = self.board.is_check()
            self.obvious_move = is_capture or is_check

            if self.board.piece_at(uci.to_square).piece_type == chess.PAWN:
                is_threat = any(
                    self.board.piece_at(sq)
                    and self.board.piece_at(sq).color == self.board.turn
                    for sq in self.board.attacks(uci.to_square)
                )
                self.obvious_move |= is_threat

    def _init_board(self):
        while True:
            try:
                self._find_board()
                break
            except:
                pass

    def _init_engine(self):
        self.engine = chess.engine.SimpleEngine.popen_uci("stockfish")
        self.engine.configure({"Skill Level": self.clock.tc.skill_level})

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
        scale = self.IMG_SIZE / self.img.shape[0]
        self.img = cv2.resize(
            self.img, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR
        )

    def _set_scale(self):
        self.scale = self.img.shape[0] / pg.size()[1]
