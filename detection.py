import cv2
import numpy as np
from imutils.object_detection import non_max_suppression
from engine import piece_names


def getChessboardCorners(board):
    _, thresholded = cv2.threshold(board, 120, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(
        thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    largest_area = 0
    largest_contour = None

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > largest_area:
            largest_area = area
            largest_contour = contour

    epsilon = 0.05 * cv2.arcLength(largest_contour, True)
    corners = cv2.approxPolyDP(largest_contour, epsilon, True)

    return corners.reshape(corners.shape[0], 2)


def find_piece(board, piece, sq_size):
    img_piece = cv2.resize(
        cv2.imread(f"assets/{piece}.png", cv2.IMREAD_UNCHANGED),
        (sq_size, sq_size),
    )
    img_piece_gray = cv2.cvtColor(img_piece, cv2.COLOR_BGR2GRAY)
    h, w = img_piece_gray.shape

    img_piece_inverted = cv2.bitwise_not(img_piece_gray)
    if piece.startswith("black"):
        mask = cv2.threshold(img_piece_inverted, 70, 255, cv2.THRESH_BINARY)[1]
    else:
        mask = img_piece[:, :, 3]

    matches = cv2.matchTemplate(board, img_piece_gray, cv2.TM_SQDIFF_NORMED, mask=mask)
    locs = np.where(matches <= 0.095)
    rects = [(x, y, x + w, y + h) for x, y in zip(*locs[::-1])]

    return non_max_suppression(np.array(rects))


def find_all_pieces(board):
    coords = np.zeros((8, 8), dtype=np.dtype("U1"))
    for piece_name, key in piece_names.items():
        pieces = find_piece(board.img_gray, piece_name, board.sq_size)
        for piece in pieces:
            x, y, h, w = piece
            posX = round(8 * x / board.bw)
            posY = round(8 * y / board.bh)
            coords[posY, posX] = key
            # cv2.rectangle(img_board, (x, y), (h, w), (0, 0, 255), 3)
    return coords
