import re

line_size = 15
n_letters = 7
alphabet = "abcdefghijklmnopqrstuvwxyz"

def get_groups(s):
    # Split the string into groups of letters and spaces
    group = ""
    L = []
    is_space = s[0] == " "
    for letter in s:
        if letter == " ":
            if is_space:
                group += letter
            else:
                L.append(group)
                group = letter
                is_space = True
        else:
            if is_space:
                L.append(group)
                group = letter
                is_space = False
            else:
                group += letter

    L.append(group)
    return L

def get_regex(groups):
    # sourcery skip: assign-if-exp, remove-redundant-fstring, simplify-fstring-formatting
    if len(groups) == 1:
        return fr"\b.{groups[0]}.\b"
    # Left spaces
    left_spaces = len(groups[0]) if " " in groups[0] else 0
    word_regex = fr"\b.{{0,{left_spaces}}}" if left_spaces > 0 else r"\b"
    if left_spaces > 0:
        groups = groups[1:]
    # Right spaces
    right_spaces = len(groups[-1]) if " " in groups[-1] else 0
    if right_spaces > 0:
        groups = groups[:-1]
    # Middle groups
    for group in groups:
        if " " in group:
            word_regex += r".{" + str(len(group)) + r"}"
        else:
            word_regex += fr"{group}"
    word_regex += fr".{{0,{right_spaces}}}\b" if right_spaces > 0 else r"\b"
    return word_regex


class Option:
    def __init__(self, word, regex, index):
        self.regex = re.compile(regex)
        self.expression = regex
        self.word = word
        self.index = index
        self.len = len(self.word.strip())
        self.letters = self.word.replace(" ", "")

    def __repr__(self):
        return self.word

    def get_start(self, word):
        regex = self.word.strip().replace(" ", ".")
        regex = re.compile(regex)
        for match in re.finditer(regex, word):
            if len(self.word.lstrip()) < len(word) - match.start(): # Not enough space to fit the whole word
                continue
            return self.index - match.start()
        return -1
        


def get_options(s):
    if s[0] == " ":
        s = f" {s}" # Add spaces at the beginning 
    if s[-1] == " ":
        s = f"{s} " # Add spaces at the end
    L = get_groups(s)
    options = []
    # Regex for the completion of groups

    max_n_groups = len([i for i in L if " " not in i]) # count letter groups

    for n_groups in range(1, max_n_groups+1): # For each grouping of words
        for i, group in enumerate(L): # iterate on characters groups
            if group[0] == " ": # iterate on letter groups only
                continue
            # Get previous block
            i_min = max(0, i-1)
            # Get next blocks of letters + one space block
            i_max = min(len(L), i + 2 * n_groups)
            groups = L[i_min:i_max]

            # Remove one space from first and last space groups
            if " " in groups[0]:
                if len(groups[0]) == 1:
                    groups = groups[1:]
                else:
                    groups[0] = groups[0][1:]

            if " " in groups[-1]:
                if len(groups[-1]) == 1:
                    groups = groups[:-1]
                else:
                    groups[-1] = groups[-1][1:]

            # print(groups, i_min)
            word_regex = get_regex(groups)

            index = sum(len(g) for g in L[:i_min])
            # print("str start", index, L[:i_min])
            word = "".join(groups)
            # print("strip", len(word) - len(word.lstrip()))
            index += len(word) - len(word.lstrip())


            o = Option(
                word = word,
                regex = word_regex,
                index = index
            )
            options.append(o)
            if i + n_groups * 2 + 1 > len(L):
                break
            
    return options