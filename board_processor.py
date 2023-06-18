import cv2
import mss
import numpy as np

from controls import get_prop
from detection import getChessboardCorners


class BoardProcessor:
    def __init__(self):
        self.sct = mss.mss()

    def get_dims(self):
        bh, bw = self.img.shape[:2]
        sq_size = int((bh + bw) / 16)
        return bh, bw, sq_size

    def crop(self):
        self.img = self.img[
            self.corners[0, 1] : self.corners[2, 1],
            self.corners[0, 0] : self.corners[2, 0],
        ]

    def resize(self):
        scale = 800 / self.img.shape[0]
        self.img = cv2.resize(
            self.img, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR
        )
        self.imgbgr = cv2.resize(
            self.imgbgr, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR
        )

    def capture_screenshot(self, monitor_index=1):
        monitor = self.sct.monitors[monitor_index]
        screenshot = np.array(self.sct.grab(monitor))
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        self.imgbgr = screenshot
        self.img = gray

        # cv2.imshow("Screenshot", screenshot)
        # cv2.waitKey()
        # return img

    def capture_screenshot_cropped(self):
        monitor = {
            "top": self.corners[0, 1] / 2,
            "left": self.corners[0, 0] / 2,
            "width": (self.corners[2, 1] - self.corners[0, 1]) / 2,
            "height": (self.corners[2, 0] - self.corners[0, 0]) / 2,
        }
        screenshot = np.array(self.sct.grab(monitor))
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        self.img = gray
        self.imgbgr = screenshot

    def process_board(self):
        self.capture_screenshot()

        # Calculate proportions and corners
        try:
            self.get_props_corners()
        except Exception:
            raise

        # Crop image to the needed part
        self.crop()

        # Calculate original square sizes (for mouse movement)
        self.bh_orig, self.bw_orig, self.sq_size_orig = self.get_dims()
        print("ORIG SIZES", self.bw_orig, self.bw_orig)
        self.resize()

        # Calculate new size and dimensions (for template matching)
        self.bh, self.bw, self.sq_size = self.get_dims()
        print("SIZES", self.bw, self.bw)

    def get_props_corners(self):
        self.prop = get_prop(self.img)
        self.corners = getChessboardCorners(self.img)
        self.topLeftCorner = self.corners[0]

    def update(self):
        self.capture_screenshot_cropped()
        self.resize()
        cv2.imwrite("screenshot.png", self.imgbgr)
        # cv2.imwrite("screenshot.png", self.img)
        # print(self.img.shape)
        # print(self.sq_size)
