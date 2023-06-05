import cv2

from controls import get_prop
from detection import getChessboardCorners


class BoardProcessor:
    def __init__(self, image_path):
        self.image_path = image_path
        self.process_board()

    def calculate_dims(self, img):
        bh, bw = img.shape[:2]
        sq_size = int((bh + bw) / 16 * 0.99)
        return bh, bw, sq_size

    def process_board(self):
        # Load image
        self.img = cv2.imread(self.image_path)

        # Convert to gray scale
        self.img_gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

        # Calculate properties and corners
        self.prop = get_prop(self.img_gray)
        self.corners = getChessboardCorners(self.img_gray)
        self.topLeftCorner = self.corners[0]

        # Refine image to the needed part
        self.img = self.img[
            self.corners[0, 1] : self.corners[2, 1],
            self.corners[0, 0] : self.corners[2, 0],
        ]

        # Calculate original size and dimensions
        self.bh_orig, self.bw_orig, self.sq_size_orig = self.calculate_dims(self.img)

        # Resize the image
        scale = 800 / self.img.shape[0]
        self.img = cv2.resize(self.img, (0, 0), fx=scale, fy=scale)

        # Calculate new size and dimensions
        self.bh, self.bw, self.sq_size = self.calculate_dims(self.img)

        # Convert resized image to gray scale
        self.img_gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
