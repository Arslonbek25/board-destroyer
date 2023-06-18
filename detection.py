import cv2
import numpy as np
from imutils.object_detection import non_max_suppression

from analysis import piece_names, piece_threshold


def is_square(A, threshold=10):
    center = sum(A) / 4.0
    rotated_points = [(A[0] - center) * (1j**i) + center for i in range(4)]

    for point in A:
        if not any(abs(point - rp) <= threshold for rp in rotated_points):
            return False

    return True


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

    if len(corners) == 4 and largest_area > 1000000:
        points = corners.reshape(corners.shape[0], 2)
        complex_points = [x + y * 1j for x, y in points]

        if not is_square(complex_points):
            raise Exception
        return points
    else:
        raise Exception


def find_piece(board, piece_name, sq_size, key):
    img_piece = cv2.imread(f"assets/{piece_name}.png", cv2.IMREAD_UNCHANGED)
    img_piece = cv2.resize(img_piece, (sq_size, sq_size))
    img_piece_gray = cv2.cvtColor(img_piece, cv2.COLOR_BGR2GRAY)
    h, w = img_piece_gray.shape
    # pawn = img_piece[:, :, 0:3]
    piece3d = img_piece[:, :, 0:3]
    board3d = board[:, :, 0:3]
    alpha = img_piece[:, :, 3]
    alpha = cv2.merge([alpha, alpha, alpha])
    # cv2.imshow("Board", board3d)
    # cv2.waitKey()
    # print(img_piece.shape)
    # print(board.shape)
    matches = cv2.matchTemplate(board3d, piece3d, cv2.TM_SQDIFF_NORMED, mask=alpha)
    # thresh = 0.1 if piece_name.startswith("white") else 0.2
    thresh = piece_threshold[key]
    locs = np.where(matches <= thresh)
    rects = [(x, y, x + w, y + h) for x, y in zip(*locs[::-1])]

    return non_max_suppression(np.array(rects))


def find_all_pieces(board):
    pos = np.zeros((8, 8), dtype=np.dtype("U1"))
    # print(board.img.shape)
    # g_board = cv2.cvtColor(board.imgbgr, cv2.COLOR_BGR2GRAY)
    for piece_name, key in piece_names.items():
        # cv2.imshow("bgr", board.img)
        # cv2.waitKey(0)
        pieces = find_piece(board.imgbgr, piece_name, board.sq_size, key)
        for piece in pieces:
            x, y, h, w = piece
            posX = round(8 * x / board.bw)
            posY = round(8 * y / board.bh)
            # print(x,y, board.bw, board.bh)
            # print(posX, posY)
            pos[posY, posX] = key
    return pos
