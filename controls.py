import pyautogui as pg
import cv2
from screen import getChessboardCorners


board = cv2.imread("assets/screenshot-3.png")
board_gray = cv2.cvtColor(board, cv2.COLOR_BGR2GRAY)

corners = getChessboardCorners(board_gray)
for corner in corners:
    x, y = corner.ravel()
    cv2.circle(board, (x, y), 20, (0, 255, 0), -1)

screen_size = pg.size()
img_size = board_gray.shape
prop = img_size[0] / screen_size[1]

x, y = corners[0].ravel()
pg.moveTo(x / prop, y / prop)


cv2.imshow("Board", board)
cv2.waitKey(0)
