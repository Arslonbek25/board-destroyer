import cv2
import numpy as np


img = cv2.imread("cb.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
template = cv2.imread("white_knight.png", 0)


kernel = np.ones((15, 15), np.uint8)
board = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)
piece = cv2.morphologyEx(template, cv2.MORPH_GRADIENT, kernel)

h, w = int(img.shape[0] / 8), int(img.shape[1] / 8)

res = cv2.matchTemplate(board, piece, cv2.TM_CCOEFF_NORMED)
threshold = 0.5

loc = np.where(res >= threshold)

rects = []
for pt in zip(*loc[::-1]):
    rects.append((pt[0], pt[1], w, h))

grects, _ = cv2.groupRectangles(rects, 1, 1)

for i in range(len(grects)):
    x, y, h, w = grects[i]
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 5)

cv2.imshow("Chess", board)
cv2.waitKey()
