import numpy as np
import matplotlib.pyplot as plt
import itertools

class MineSweeper:
    def __init__(self, board):
        self.size = len(board)
        self.board = board
        self.mine_proba = None
        
    def get_probas(self):
        self.mine_proba = np.ones((self.size, self.size)) * -1 # -1 means not computed
        max_steps = 10
        for _ in range(max_steps):
            new_proba = self.refine_probas(self.mine_proba)
            if np.allclose(new_proba, self.mine_proba):
                break
            self.mine_proba = new_proba
            # self.plot_proba()
        print(f"Done in {_ + 1} steps")
        return self.mine_proba
        

    def refine_probas(self, probas):
        probas = probas.copy()
        for i, j in itertools.product(range(self.size), range(self.size)): # Iterate over all cells
            to_find = self.board[i, j]
            if to_find == 0:
                probas[i, j] = 0
                continue
            elif to_find == -1: # -1 cell
                continue
            else: # has a number
                probas[i, j] = 0
                # Get -1 cells around
                x_min = max(0, i-1)
                x_max = min(self.size, i+2)
                y_min = max(0, j-1)
                y_max = min(self.size, j+2)

                nb_blocks = (x_max - x_min) * (y_max - y_min)
                found = 0 # Number of mines known
                possible = [] # List of cells where it's not sure
                for x in range(x_min, x_max):
                    for y in range(y_min, y_max):
                        if self.board[x, y] == -1:
                            if probas[x, y] == 1: # Mine
                                found += 1
                            elif probas[x, y] == 0: # Empty
                                pass
                            else: # Unknown
                                possible.append((x, y))
                nb_unknown = len(possible)

                if nb_unknown == 0:
                    continue

                if found == to_find:
                    for x, y in possible:
                        probas[x, y] = 0

                elif nb_unknown + found == to_find:
                    for x, y in possible:
                        probas[x, y] = 1

                else:
                    for x, y in possible:
                        probas[x, y] = max(probas[x, y], (to_find - found) / nb_unknown)

        # Set all -1 values to 1
        probas[probas == -1] = 0.9
        return probas
                
    def plot_proba(self):
        plt.figure(figsize=(10, 10))
        plt.imshow(self.mine_proba)
        # Red at 1, green at 0
        plt.set_cmap('Reds')
        # Add value on each cell
        for i, j in itertools.product(range(self.size), range(self.size)):
            if self.board[i, j] != -1:
                plt.text(j, i, self.board[i, j], ha="center", va="center", color="black")
            # plt.text(j, i, f"{self.mine_proba[i, j]:^.2f}", ha="center", va="center", color="w")
        plt.colorbar()
        plt.show()

    def get_move(self):
        proba = self.get_probas()
        best = None
        best_proba = 1
        # Select the cell with -1 value in board and the lowest probability
        for i, j in itertools.product(range(self.size), range(self.size)):
            if self.board[i, j] == -1 and proba[i, j] < best_proba:
                best_proba = proba[i, j]
                best = (i, j)
        return best[0], best[1], best_proba
                
    def get_moves(self):
        proba = self.get_probas()
        best = None
        best_proba = 1
        can_click = []
        # Select the cell with -1 value in board and the lowest probability
        for i, j in itertools.product(range(self.size), range(self.size)):
            if self.board[i, j] == -1 and proba[i, j] < best_proba:
                best_proba = proba[i, j]
                best = (i, j)
            if self.board[i, j] == -1 and proba[i, j] == 0:
                can_click.append((i, j))
        return can_click, best_proba, best
            