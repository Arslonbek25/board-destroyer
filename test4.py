import cv2
import numpy as np


def draw_results(img, rects):
    for r in rects:
        print(r)
        cv2.rectangle(img, (r[0], r[1]), (r[0] + r[2], r[1] + r[3]), (0, 0, 255), 2)


def check_color(img, temp, rect):
    y0, y1, x0, x1 = rect[1], rect[1] + rect[3], rect[0], rect[0] + rect[2]
    crop = (img[y0:y1, x0:x1]).copy()
    diff = cv2.absdiff(temp, crop)
    avg_diff = cv2.mean(diff)[0] / 255
    return avg_diff < 0.4  # a tricky threshold


def find_template_multiple(img, temp):
    rects = []
    w, h = temp.shape[1], temp.shape[0]

    result = cv2.matchTemplate(img, temp, cv2.TM_CCOEFF_NORMED)
    threshold = 0.5  # matching threshold, relatively stable.
    loc = np.where(result >= threshold)

    for pt in zip(*loc[::-1]):
        rects.append((pt[0], pt[1], w, h))

    # Perform a simple non-max suppression
    rects, _ = cv2.groupRectangles(rects, 1, 1)

    # Flatten list of list to list of elements
    rects = [r for r in rects]

    return rects


# Load the chess board and chess piece images
img_board = cv2.imread("screenshot.png")
img_piece = cv2.imread("assets/black_pawn.png")

# Convert both images to grayscale
img_board_gray = cv2.cvtColor(img_board, cv2.COLOR_BGR2GRAY)
img_piece_gray = cv2.cvtColor(img_piece, cv2.COLOR_BGR2GRAY)

s = 3
kernel = np.ones((s, s), np.uint8)
# morphological gradient stabilizes the template matching by focusing on the shape's edges rather than its content.
img_board_gray_grad = cv2.morphologyEx(img_board_gray, cv2.MORPH_GRADIENT, kernel)
img_piece_gray_grad = cv2.morphologyEx(img_piece_gray, cv2.MORPH_GRADIENT, kernel)


rects = find_template_multiple(img_board_gray_grad, img_piece_gray_grad)

matching_color_list = [check_color(img_board_gray, img_piece_gray, r) for r in rects]

# Keep only matching color rectangles.
matching_color_rects = [
    r for (r, is_matching) in zip(rects, matching_color_list) if is_matching
]

print(rects)
draw_results(img_board, matching_color_rects)


# Show the result
cv2.imshow("Result", img_board)
cv2.waitKey(0)
cv2.destroyAllWindows()
