from PIL import ImageGrab
import cv2
import numpy as np
import matplotlib.pyplot as plt
import itertools
from time import sleep
import pyautogui


block_size = 43
space = 4

# colors={
#     -2: , # highlighted default
#     -1: (186, 189, 182), # default
#     0: (222, 222, 220),
#     1: (221, 250, 195),
#     2: (236, 237, 191),
#     3: (237, 218, 180),
#     4: (237, 195, 138),
#     "bomb": (136, 138, 133)
# }

class Color:
    def __init__(self, rgb, threshold=3000, value=-1):
        self.rgb = rgb
        self.threshold = threshold
        self.value = value

    def __call__(self, block):
        pixel_nb = np.sum(block == self.rgb)
        return self.value if pixel_nb > self.threshold else None

    def pixels(self, block):
        return np.sum(block == self.rgb)


colors = [
    Color((210, 214, 206), 3000, -1), # highlighted default
    Color((186, 189, 182), 3000, -1), # default
    Color((222, 222, 220), 3000, 0), # empty
    Color((221, 250, 195), 3000, 1), # 1
    Color((236, 237, 191), 1000, 2), # 2
    Color((237, 218, 180), 3000, 3), # 3
    Color((237, 195, 138), 3000, 4), # 4
    Color((247, 161, 162), 3000, 5), # 5
    Color((136, 138, 133), 3000, "bomb"), # bomb
]


def click(x, y):
    x, y = y, x
    x = 21 + x * (block_size + space) + block_size // 2
    y = 202 + y * (block_size + space) + block_size // 2
    pyautogui.click(x, y)
    pyautogui.click(button="left")

def mark_mines(probas):
    for i, j in itertools.product(range(16), range(16)):
        if probas[i, j] == 1:
            x = 21 + j * (block_size + space) + block_size // 2
            y = 202 + i * (block_size + space) + block_size // 2
            pyautogui.click(x, y, button="right")
            click(i, j)

def get_screen(click=False):
    if click:
        pyautogui.click(200, 100)
    # sleep(0.1)
    screen = np.array(ImageGrab.grab(bbox=(21,202,766,947)))
    # screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
    return screen

def get_block(screen, i, j):
    x = j * (block_size + space)
    y = i * (block_size + space)
    block = screen[y:y+block_size, x:x+block_size]
    # block = cv2.cvtColor(block, cv2.COLOR_RGB2BGR)
    return block

def get_number(block, override=False):
    c = [color.pixels(block) for color in colors]
    if np.max(c) < 1000:
        return -3

    # Get argmax 
    i = np.argmax(c)
    if override:
        return colors[i].value
    else:
        value = colors[i].value
        if value == "bomb":
            raise ValueError("Bomb detected")
        return value

def parse_grid(screen, override=False):
    grid = np.ones((16, 16), dtype=int) * -1
    for i, j in itertools.product(range(16), range(16)):
        block = get_block(screen, i, j)
        grid[i, j] = get_number(block, override=override)
    return grid

def plot(screen):
    plt.figure(figsize=(10, 10))
    plt.imshow(screen)
    plt.show()

if __name__ == '__main__':
    while True:
        screen = get_screen()
        grid = parse_grid(screen)
        if np.any(grid == -2) or np.all(grid == -1):
            print('No grid detected')
        else:
            print(grid)
        sleep(1)

