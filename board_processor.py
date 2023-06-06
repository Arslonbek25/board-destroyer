import cv2

from controls import get_prop
from detection import getChessboardCorners


class BoardProcessor:
    def __init__(self, image_path):
        self.image_path = image_path
        self.process_board()

    def load_image(self):
        self.img = cv2.imread(self.image_path, cv2.IMREAD_GRAYSCALE)

    def get_dims(self):
        bh, bw = self.img.shape[:2]
        sq_size = int((bh + bw) / 16 * 0.99)
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

    def process_board(self):
        self.load_image()

        # Calculate proportions and corners
        self.get_props_corners()

        # Crop image to the needed part
        self.crop()

        # Calculate original square sizes (for mouse movement)
        self.bh_orig, self.bw_orig, self.sq_size_orig = self.get_dims()

        self.resize()

        # Calculate new size and dimensions (for template matching)
        self.bh, self.bw, self.sq_size = self.get_dims()

    def get_props_corners(self):
        self.prop = get_prop(self.img)
        self.corners = getChessboardCorners(self.img)
        self.topLeftCorner = self.corners[0]

    def update(self):
        self.load_image()
        self.crop()
        self.resize()
