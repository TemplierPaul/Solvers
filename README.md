# Solvers
Solving a puzzle is fun.  
Understanding how a puzzle is solved is more fun.  
But coding a solver to play Minesweeper for you is just overengineering, and that's what this is all about.

*Disclaimer*: This is a collection of side projects made for fun with no goal to be optimal, efficient, or even to work on other people's computers. There is no machine learning here, just mostly brute force and a bunch of tricks. 

## Nonograms
A nonogram is a puzzle where you have to fill in a grid with black and white squares. 
This solver goes line by line, generates the possible solutions for each line, filters them based on the cells that are already filled in, and iterates over columns and rows until all cells are filled in.

## Wordle
Not a smart wordle solver, but it does the job. Filters a list of words based on current knowledge, then computes "probabilities" of each letter being in each spot and uses that to select a word. 

## Minesweeper
This solves a 16x16 Minesweeper board in 20s on my laptop by taking a screenshot of the board, determining the number of mines from cell colors, and then using a recursive algorithm to solve the board. It then clicks on the cells to reveal the solution with `pyautogui`. 
It needs Mines open on the left half of the screen (and the CLI with the code on the right half of the screen) and may be bugged if the screen resolution is not mine. 

The video is from an older version of the code, but it's the same idea.

## Scrabble
My mom was too good at Scrabble, so I did the next logical thing and ~~practiced for hours~~ wrote a solver.
I tries to solve row by row and column by column, then checks all possibilities and finds the best score. 

There is still a bunch of improvements to be made:
- [ ] Keep the solutions in memory and only compute solutions for rows and columns that have changed
- [ ] Joker: fix score where it counts points for the letter used as a joker 
- [ ] Joker management: add Ray parallelization to improve speed
- [ ] End game strategies: simulate multiple moves to best use the letters in hand without picking in the bag. 
- [ ] Keep track of the letters still in the bag to select a move that opens up more possibilities later
- [ ] Keep track of the letters that are still in the bag or in the opponent's hand to select a move that blocks the opponents
