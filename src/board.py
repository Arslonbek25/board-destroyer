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
    def __init__(self):
        self.engine_path = "/usr/local/bin/stockfish"
        self.IMG_SIZE = 750
        self.sct = mss.mss()
        self._init_board()
        self._init_engine()
        self.turn = control.get_turn()
        self.color = control.get_color()
        self.timecontrol = control.get_timecontrol()
        self.prev_pos = None
        self.board = None
        self.last_speed = None
        self.is_capture = False
        self.max_move_time = {"rapid": 10, "blitz": 6, "bullet": 1}
        self.clock = Clock(self.max_move_time[self.timecontrol])

    def update(self):
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
        if self.is_capture:
            return self.clock.min_time

        move_time = time.time() - self.last_speed if self.last_speed else 0.1
        self.last_speed = time.time()
        num_pieces = len(self.board.piece_map())
        newtime = self.clock.calculate_move_time(move_time, num_pieces)

        return newtime

    def get_best_move(self):
        result = self.engine.play(
            self.board, chess.engine.Limit(time=self.get_move_time())
        )
        return str(result.move)

    def switch_turn(self, is_first_move=False):
        if not is_first_move:
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
        self.is_capture = self.board.is_capture(uci)
        self.board.push_san(move)

    def _init_board(self):
        while True:
            try:
                self._find_board()
                break
            except:
                pass

    def _init_engine(self):
        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        self.engine.configure({"Skill Level": 20})

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
