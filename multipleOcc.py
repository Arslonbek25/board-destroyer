import cv2
import numpy as np

img = cv2.imread("cb.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
template = cv2.imread("bishop.png", 0)
h, w = template.shape

res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
threshold = 0.8
loc = np.where(res >= threshold)

rects = []
for pt in zip(*loc[::-1]):
    rects.append((pt[0], pt[1], w, h))
suppressed_rects = cv2.dnn.NMSBoxes(rects, res[loc], 0.5, 0.5)

for i in suppressed_rects:
    x, y, _, _ = rects[i]
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 10)

cv2.imshow("Chess", img)
cv2.waitKey()
