from datetime import datetime

import cv2
import mss
import numpy as np
import pyautogui as pg

from detection import getChessboardCorners


class Board:
    def __init__(self):
        self.IMG_SIZE = 640
        self.sct = mss.mss()
        self._init_board()

    def update(self):
        self._capture_screenshot(cropped=True)
        self._resize()

    def save_screenshot(self, filename=f"screenshots/screenshot{id}.png"):
        now = datetime.now()
        id = now.strftime("%Y%m%d_%H%M%S_%f")
        cv2.imwrite(filename, self.img)

    def _init_board(self):
        while True:
            try:
                self._find_board()
                break
            except:
                pass

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
