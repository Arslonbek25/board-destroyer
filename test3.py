import cv2
from analysis import piece_names
import numpy as np


def crop_transparent(img_path):
    # Load the image with alpha channel
    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)

    # Make a mask of non-zero pixels
    _, _, _, alpha = cv2.split(img)
    non_zero_pixels = np.where(alpha > 0)

    # Get the bounding box
    min_x = np.min(non_zero_pixels[1])
    max_x = np.max(non_zero_pixels[1])
    min_y = np.min(non_zero_pixels[0])
    max_y = np.max(non_zero_pixels[0])

    # Crop the image with the bounding box coordinates
    result = img[min_y : max_y + 1, min_x : max_x + 1]

    return result


for piece_name, key in piece_names.items():
    piece = crop_transparent(f"assets/{piece_name}.png")
    # cv2.imwrite(f"assets/{piece_name}.png", piece)
    # cv2.imshow("Piece", piece)
    cv2.waitKey(0)
