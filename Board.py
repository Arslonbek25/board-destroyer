import random
from datetime import datetime

import chess
import chess.engine
import cv2
import mss
import numpy as np
import pyautogui as pg

from detection import getChessboardCorners


class Board:
    def __init__(self):
        self.engine_path = "/usr/local/bin/stockfish"
        self.IMG_SIZE = 640
        self.sct = mss.mss()
        self._init_board()
        self._init_engine()
        self.prev_pos = None
        self.board = None

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

    def get_best_move(self):
        result = self.engine.play(
            self.board, chess.engine.Limit(time=random.randint(5, 30) / 10)
        )
        return str(result.move)

    def _init_board(self):
        while True:
            try:
                self._find_board()
                break
            except:
                pass

    def _init_engine(self):
        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        self.engine.configure({"Skill Level": 3})

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
        self.corners = getChessboardCorners(self.img)

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
