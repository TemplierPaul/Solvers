from solver import *
from read_screen import *

block_size = 43
space = 4

if __name__ == '__main__':
    playing = False 
    while True:
        screen = get_screen(click = playing)
        grid = parse_grid(screen)
        if np.any(grid == -3) or np.all(grid == -1):
            print(grid)
            print('No grid detected')
            # where = np.where(grid == -3)
            # for i, j in zip(*where):
            #     print(f"Can't get {i}, {j}")
            playing = False
            # sleep(0.5)
        else:
            print(grid)
            playing = True
            ms = MineSweeper(grid)
            # x, y, p = ms.get_move()
            moves, proba, best = ms.get_moves()

            if len(moves) == 0:
                print("No moves")
                x, y = best
                print(f"Move: {x}, {y} | proba {proba}")
                click(x, y)
            else:
                for x, y in moves:
                    print(f"Move: {x}, {y}")
                    click(x, y)
        # sleep(0.1)

