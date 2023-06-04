import pyautogui as pg


def get_prop(board):
    screen_size = pg.size()
    img_size = board.shape
    prop = img_size[0] / screen_size[1]
    return prop


def playMove(move_coords, prop):
    print(move_coords, prop)
    move_coords /= prop
    x1, y1, x2, y2 = move_coords
    pg.moveTo(x1, y1, duration=0.3)
    pg.moveTo(x2, y2, duration=0.3)
