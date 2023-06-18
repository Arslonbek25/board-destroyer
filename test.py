import cv2
import numpy as np
from imutils.object_detection import non_max_suppression


def find_piece(board, piece, sq_size):
    img_piece = cv2.resize(
        cv2.imread(f"assets/{piece}.png", cv2.IMREAD_UNCHANGED), (sq_size, sq_size)
    )
    # binary_piece = binarize_image(img_piece_gray, 50)

    alpha = img_piece[:, :, 3]
    alpha = cv2.merge([alpha, alpha, alpha])
    b = board[:, :, :3]
    p = img_piece[:, :, :3]
    img_piece_gray = cv2.cvtColor(p, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("img_piece_gray", b)
    # cv2.waitKey(0)
    h, w = img_piece_gray.shape
    matches = cv2.matchTemplate(b, p, cv2.TM_CCORR_NORMED, mask=alpha)
    locs = np.where(matches >= 0.97)
    rects = [(x, y, x + w, y + h) for x, y in zip(*locs[::-1])]
    return non_max_suppression(np.array(rects))


def binarize_image(image, threshold=127):
    _, binary = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
    return binary


board = cv2.imread("screenshot.png", cv2.IMREAD_GRAYSCALE)
board_bgr = cv2.imread("screenshot.png", cv2.IMREAD_UNCHANGED)
board_bin = binarize_image(board)

# binary_board = binarize_image(board)
# kernel = np.ones((3, 3), np.uint8)

# canny = cv2.morphologyEx(board, cv2.MORPH_GRADIENT, kernel)

pieces = find_piece(board_bgr, "white_pawn", 200)
for piece in pieces:
    cv2.rectangle(
        board_bgr, (piece[0], piece[1]), (piece[2], piece[3]), (255, 0, 0), 7
    )


cv2.imshow("board", board_bin)
cv2.waitKey(0)
