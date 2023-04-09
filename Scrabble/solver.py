try:
    from .scrabble import *
    from .word_match import *
except:
    from scrabble import *
    from word_match import *
    
from tqdm import tqdm

line_size = 15

p = {"A,E,I,L,N,O,R,S,T,U" : 1,
"D,G,M" : 2,
"B,C,P" : 3,
"F,H,V" : 4,
"J,Q" : 8,
"K,W,X,Y,Z" : 10}

POINTS = {}
for k, v in p.items():
    for l in k.split(","):
        POINTS[l.lower()] = v
POINTS[" "] = 0

import pandas as pd
DICO = pd.read_csv('words.csv')
DICO.fillna("nan", inplace=True)

class Tile:
    def __init__(self):
        self._letter = " "
        self.value = 0
        self.row = None
        self.col = None
        self.multiplier = 1
        self.word_multiplier = 1
        self.left = None
        self.right = None
        self.up = None
        self.down = None
        self.options = []
        self.char_mul = 1
        self.word_mul = 1

    @property
    def letter(self):
        return self._letter

    @letter.setter
    def letter(self, value):
        if self._letter == " ":
            self._letter = value
        elif self._letter != value:
            raise IOError(f"Letter already set: {self._letter} != {value}")
        

    def __repr__(self):
        return f"Tile {self.letter}"

    def __str__(self):
        return f"{self.left.letter} < {self.letter} > {self.right.letter}"

    def evaluate(self, letter):
        if self._letter != " ": # Letter already set
            # assert self._letter == letter , f"Letter already set: {self._letter} != {letter}"
            if self._letter != letter:
                return 0, 0
            return POINTS[letter], 1
        else: # Letter not set, can use multiplier
            return POINTS[letter] * self.char_mul, self.word_mul

class Solution:
    def __init__(self, word, start, row, score):
        self.word = word
        self.start = start
        self.row = row
        self.score = score

    def __repr__(self):
        return f"{self.get_pos():<3} - {self.word:<10} (+{self.score:>3})"

    def __str__(self):
        return self.__repr__()

    def __lt__(self, other):
        return self.score < other.score

    def __gt__(self, other):
        return self.score > other.score

    def __eq__(self, other):
        return self.score == other.score

    def get_pos(self):
        # sourcery skip: remove-unnecessary-else, swap-if-else-branches
        if "Row" in self.row.name:
            letter = alphabet[self.row.number].upper()
            return f"{letter}{self.start+1}"
        elif "Column" in self.row.name:
            letter = alphabet[self.start].upper()
            return f"{self.row.number+1}{letter}"

    
class Row:
    def __init__(self, number):
        self.number = number
        self.tiles = []
        left = None
        for _ in range(line_size):
            tile = Tile()
            tile.row = self
            tile.left = left
            if left:
                left.right = tile
            left = tile
            self.tiles.append(tile) 

    def __repr__(self):
        s = "|".join([tile.letter for tile in self.tiles])
        return f">{s}<"

    def __str__(self):
        return self.__repr__()

    def before(self, tile):
        return tile.left

    def after(self, tile):
        return tile.right

    def ortho_before(self, tile):
        return tile.up

    def ortho_after(self, tile):
        return tile.down

    def orthogonal(self, tile):
        return tile.col

    @property
    def name(self):
        return f"{self.__class__.__name__} {self.number}"

    def __getitem__(self, index):
        return self.tiles[index]

    def letters(self):
        return [tile.letter for tile in self.tiles]

    def set_word(self, word, start):
        for i, letter in enumerate(word):
            assert self[start + i].letter in [
                " ",
                letter,
            ], f"Letter already set: {self[start + i].letter} != {letter}"
        for i, letter in enumerate(word):
            self[start+i].letter = letter

    def eval_word(self, word, start):
        points = 0
        mul = 1
        new_letters = 0
        for i, letter in enumerate(word):
            # print(start+i, letter)
            p, m = self[start+i].evaluate(letter)
            if self[start+i].letter == " ":
                new_letters += 1
            points += p
            mul *= m
        # TODO: count Scrabble
        bonus = 50 if new_letters == 7 else 0
        points = 0 if new_letters == 0 else points
        return points, mul, bonus

    def get_conflicts(self, word, start):
        conflicts = []
        for i, letter in enumerate(word):
            tile = self[start+i]
            conflict = False
            if tile.letter != " ": # No conflict if letter already set
                continue
            if self.ortho_before(tile) and self.ortho_before(tile).letter != " ":
                conflict = True
            if self.ortho_after(tile) and self.ortho_after(tile).letter != " ":
                conflict = True

            if conflict:
                # Get conflicting word
                s = ""
                start_index = self.number
                while self.ortho_before(tile) and self.ortho_before(tile).letter != " ":
                    tile = self.ortho_before(tile)
                    s = tile.letter + s
                    start_index -= 1
                tile = self[start+i]
                s += letter
                while self.ortho_after(tile) and self.ortho_after(tile).letter != " ":
                    tile = self.ortho_after(tile)
                    s += tile.letter
                conflicts.append((i, s, start_index))
        return conflicts        
        

    def check_conflicts(self, word, start, verbose = False):
        # Check orthogonal words
        points = 0
        conflicts = self.get_conflicts(word, start)
        for i, s, start_index in conflicts:
                # Check if word is in dico
                wordlist = DICO["word"].tolist()
                if s not in wordlist:
                    if verbose:
                        print(f"{s} Not in dico")
                    return 0, 0 # Conflict so no points and no multiplier
                else:
                    # Evaluate new word
                    ortho = self.orthogonal(self[start+i]) # Get orthogonal line
                    try:
                        p, m, b = ortho.eval_word(s, start_index)
                        if verbose:
                            print(f"{s} in dico => {p} points, {m} multiplier")
                    except:
                        print(self.name, s, ortho.name,  start_index)
                        raise
                    points += p * m
        return points, 1
                

    def get_options(self):
        return get_options("".join(self.letters()))

    def solve(self, hand_letters):
        matches = []
        # with letters
        options = self.get_options()
        for o in options:
            letters = o.letters + hand_letters
            words = get_words(letters, DICO)["word"].tolist()
            for word in words:
                try:
                    l = re.search(o.regex, word)
                except re.error:
                    print("re.error")
                    print(o.regex, word)
                    raise re.error
                except Exception as e:
                    print(e)
                    print(o.regex, word)
                    raise e
                if l:
                    start = o.get_start(l.string)
                    points, mul, bonus = self.eval_word(l.string, start)
                    score = points * mul + bonus
                    # TODO Check conflicts
                    p, m = self.check_conflicts(l.string, start)
                    if m == 0:
                        continue
                    score += p
                    sol = Solution(l.string, start, self, score)
                    matches.append(sol)

        # With blanks and parallel words
        groups = get_groups(self.letters())
        index = 0
        for i, b in enumerate(groups):
            # print(f"Group {i}: >{b}<")
            if " " not in b:
                index += len(b)
                continue

            # Check for letters in parallel lines
            has_letter = False
            for j in range(len(b)):
                tile = self.tiles[index + j]
                if self.ortho_before(tile) and self.ortho_before(tile).letter != " ":
                    has_letter = True
                    break
                if self.ortho_after(tile) and self.ortho_after(tile).letter != " ":
                    has_letter = True
                    break
            
            if not has_letter:
                index += len(b)
                continue

            # print("Has letter in parallel line")

            # The blank space has letters in parallel lines
            # Remove first and / or last blanks for same-line conflicts
            if len(groups) == 1: # Blank line, can use all spaces
                n = len(b)
            elif i in [0, len(groups) - 1]: # First or last blank
                if len(b) <= 1:
                    continue
                n = len(b) - 1
            else: # Middle
                if len(b) <= 2:
                    continue
                n = len(b) - 2

            # Get all words with the letters
            words = get_words(hand_letters, DICO)
            # Get all words with n characters max
            words = words[words["length"] <= n]
            # to list
            words = words["word"].tolist()
            # print(words)

            # Starting index of the word
            if i==0:
                start = 0
            else:
                start = index + 1

            for w in words:
                max_shift = n - len(w) - start
                for shift in range(max_shift + 1): # Try all positions of the word
                    shifted_start = start + shift
                    # Check successful conflicts
                    p, m = self.check_conflicts(w, shifted_start, verbose=False)
                    if m == 0: # Conflict that doesn't work
                        continue
                    if p == 0: # No close word
                        continue
                    # New word complements the parallel word
                    # Evaluate 
                    points, mul, bonus = self.eval_word(w, shifted_start)
                    score = points * mul + bonus + p
                    sol = Solution(w, shifted_start, self, score)
                    matches.append(sol)
            
            index += len(b)

        # Sort
        matches.sort(reverse=True)
        return matches

class Column(Row):
    def __init__(self, number, tiles):
        self.number = number
        self.tiles = tiles
        up = None
        for t in tiles:
            t.col = self
            t.up = up
            if up:
                up.down = t
            up = t
    
    def before(self, tile):
        return tile.up

    def after(self, tile):
        return tile.down
    
    def ortho_before(self, tile):
        return tile.left

    def ortho_after(self, tile):
        return tile.right

    def orthogonal(self, tile):
        return tile.row


class Board:
    def __init__(self):
        self.rows = [Row(i) for i in range(line_size)]
        self.cols = []
        for i in range(line_size):
            tiles = [l[i] for l in self.rows]
            col = Column(i, tiles)
            self.cols.append(col)
        self.set_multipliers()
        self.moves = []

    def __repr__(self):
        s = "   " + "|".join([f"{i:^3}" for i in range(1, line_size+1)]) + "\n"
        for i, l in enumerate(self.rows):
            line = []
            for c in l:
                line += [f"{c.letter.upper():^3}"]
            letter = alphabet[i].upper()
            s += f"{letter} >" + "|".join(line) + "<\n"
        return s 

    def __str__(self):
        return self.__repr__()

    def __getitem__(self, pos):
        i, j = pos
        return self.rows[i][j]

    def __setitem__(self, pos, letter):
        i, j = pos
        self.rows[i][j].letter = letter

    def set_word(self, word, i, j, axis):
        if axis == 0:
            line = self.rows[i]
            p, m, b = line.eval_word(word, j)
            c_p, _ = line.check_conflicts(word, j)
            p += c_p
            line.set_word(word, j)
        elif axis == 1:
            line = self.cols[j]
            p, m, b = line.eval_word(word, i)
            c_p, _ = line.check_conflicts(word, i)
            p += c_p
            line.set_word(word, i)
        else:
            raise IOError
        return p * m + b

    def set_multipliers(self):
        # Diagonals 
        for i in range(15):
            if 5 <= i <= 9:
                continue
            self[i, i].word_mul = 2
            self[i, 14-i].word_mul = 2

        # Corners
        for i in [0, 7, 14]:
            for j in [0, 7, 14]:
                self[i, j].word_mul = 3
        # Center
        self[7, 7].word_mul = 2

        # Triple char
        for i in [1, 5, 9, 13]:
            for j in [1, 5, 9, 13]:
                if i in [1, 13] and j in [1, 13]:
                    continue
                self[i, j].char_mul = 3 

        # Double char border
        for i in [0, 14]:
            for j in [3, 11]:
                self[i, j].char_mul = 2
                self[j, i].char_mul = 2

        # Double char center
        for i, j in [(6, 2), (7, 3), (8, 2), (6, 6), (8, 6)]:
            self[i, j].char_mul = 2
            self[j, i].char_mul = 2
            self[14-i, 14-j].char_mul = 2
            self[14-j, 14-i].char_mul = 2

    def mul_matrices(self):
        s = []
        for r in self.rows:
            L = []
            for t in r:
                v = str(t.word_mul) if t.word_mul > 1 else " " 
                L.append(v)
            s.append("|".join(L))
        words = "\n".join(s)

        s = []
        for r in self.rows:
            L = []
            for t in r:
                v = str(t.char_mul) if t.char_mul > 1 else " " 
                L.append(v)
            s.append("|".join(L))
        char = "\n".join(s)
        return words, char

    def solve(self, hand_letters):
        matches = []
        if "*" in hand_letters: # Joker: reccursive call for each letter
            for joker in alphabet:
                print("Joker:", joker)
                real_letters = hand_letters.replace("*", joker)
                matches += self.solve(real_letters)
        else:
            bar = tqdm(self.rows + self.cols)
            for line in bar:
                try:
                    matches += line.solve(hand_letters)
                    matches.sort(reverse=True)
                    if len(matches) > 0:
                        best_so_far = matches[0]  
                        bar.set_description(f"Best score: {best_so_far}")
                    else:
                        bar.set_description(f"No solution found yet")
                # allow keyboard interrupt
                except KeyboardInterrupt:
                    print("Keyboard interrupt")
                    break
        return matches

    def first_step(self, hand_letters):
        row = self.rows[7]
        # Get all words
        words = get_words(hand_letters, DICO)["word"].tolist()
        # Evaluate all words
        matches = []
        for word in words:
            # print(word)
            for start_i in range(7 - len(word), 7):
                # print(start_i)
                points, mul, bonus = row.eval_word(word, start_i)
                if points == 0:
                    continue
                score = points * mul + bonus
                sol = Solution(word, start_i, row, score)
                matches.append(sol)
        matches.sort(reverse=True)
        return matches


    def __call__(self, pos, word):
        pos = pos.lower()
        if len(pos) == 2:
            a, b = pos
        elif len(pos) == 3:
            if pos[0] in alphabet: # A12
                a, b = pos[0], pos[1:]
            elif pos[2] in alphabet: # 12A
                a, b = pos[:2], pos[2]
        else:
            raise IOError(f"Invalid position: {pos}")
        if a in alphabet:
            i = alphabet.index(a)
            j = int(b) - 1
            # print("Horizontal", i, j)
            score = self.set_word(word, i, j, 0)
        elif b in alphabet:
            j = int(a) - 1
            i = alphabet.index(b)
            # print("Vertical", i, j)
            score = self.set_word(word, i, j, 1)
        else:
            raise IOError 
        print(f"Playing {word} at {pos} - Score: {score}")
        self.moves.append({
            "pos": pos,
            "word": word,
            "score": score,
        })
        return self

    def save(self, filename):
        moves_df = pd.DataFrame(self.moves)
        moves_df.to_csv(filename, index=False)

    def load(self, filename, ignore_last = False):
        moves_df = pd.read_csv(filename)
        if ignore_last:
            # Remove last move
            if len(moves_df) > 0:
                moves_df = moves_df[:-1]
        for i, row in moves_df.iterrows():
            self(row["pos"], row["word"])

        return len(moves_df)