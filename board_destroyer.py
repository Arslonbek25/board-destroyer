import cv2
import numpy as np
from imutils.object_detection import non_max_suppression

img_board = cv2.imread("assets/cb.png")
img_piece = cv2.imread("assets/black_bishop.png", cv2.IMREAD_UNCHANGED)

img_board_gray = cv2.cvtColor(img_board, cv2.COLOR_BGR2GRAY)
img_piece_gray = cv2.cvtColor(img_piece, cv2.COLOR_BGR2GRAY)

h, w = img_piece_gray.shape
mask = img_piece[:, :, 3]

res = cv2.matchTemplate(img_board_gray, img_piece_gray, cv2.TM_SQDIFF_NORMED, mask=mask)
threshold = 0.1
loc = np.where(res <= threshold)

rects = []
for x, y in zip(*loc[::-1]):
    rects.append((x, y, x + w, y + h))

pick = non_max_suppression(np.array(rects))
for r in pick:
    x, y, h, w = r
    cv2.rectangle(img_board, (x, y), (h, w), (0, 0, 255), 5)

cv2.imshow("Chess", img_board)
cv2.waitKey()
