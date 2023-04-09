import matplotlib.pyplot as plt
import numpy as np
from numpy.random import default_rng
import pandas as pd
import emoji

# Loading data


def get_alphabet(words):
    alphabet = []
    for i in words:
        for j in i:
            if j not in alphabet:
                alphabet.append(j)
    return "".join(alphabet)


def load_words(source):
    file = f"data/{source}.csv"
    lex = pd.read_csv(file, header=None, names=["word"])
    word_list = lex.word.tolist()

    return word_list

# Display


def squares(result):
    d = {
        0: ":cross_mark:",
        1: ":white_question_mark:",
        2: ":check_mark_button:"
    }
    return emoji.emojize("".join([d[i] for i in result]))


def display(result):
    print(squares(result))
    return result

# Game


class Wordle:
    def __init__(self, word):
        self.word = word.lower()
        self.tried = []

    def check(self, word):
        array_result = []
        for i in range(len(self.word)):
            if word[i] == self.word[i]:
                array_result.append(2)
            elif word[i] in self.word:
                array_result.append(1)
            else:
                array_result.append(0)
        return array_result

    def test(self, word):
        self.tried.append(word)
        return self.check(word)

    def display(self):
        print(f"{len(self.tried)} words tried:")
        for i in self.tried:
            print(i, squares(self.check(i)))

# Solver


class Solver:
    def __init__(self, word_list, size=5):
        self.word_list = word_list
        self.alphabet = get_alphabet(word_list)
        self.letter_rank = {self.alphabet[i]: i for i in range(len(self.alphabet))}
        self.size = size
        self.words = [i for i in word_list if len(i) == size]
        self.probas = None
        self.get_current_probas()
        self.tries = 0
        self.rng = default_rng()

    def __repr__(self):
        return f"Wordle ({self.size}): {self.tries} words tried, {len(self.words)} words left"

    def __str__(self):
        return self.__repr__()

    def ask(self, random=True):
        assert len(self.words) > 0
        w_p = [self.word_proba(w) for w in self.words]
        if random:
            w_p /= np.sum(w_p)  # Normalize
            return self.rng.choice(self.words, p=w_p)
        else:
            return self.words[np.argmax(w_p)]

    def tell(self, word, result):
        self.filter_words(word, result)
        self.tries += 1
        self.get_current_probas()
        return self

    def get_current_probas(self):
        count = np.zeros((self.size, 26))
        for w in self.words:
            for i in range(self.size):
                letter = w[i].lower()
                rank = self.letter_rank[letter]
                count[i][rank] += 1
        self.probas = count / (np.sum(count)/5)
        return self.probas

    def filter_words(self, word, res):
        for i in range(len(res)):
            if res[i] == 2:  # Letter is known
                self.words = [w for w in self.words if (word[i] == w[i])]

            elif res[i] == 1:  # Letter not here
                self.words = [w for w in self.words if (
                    word[i] != w[i])]  # Not that letter here
                # And that letter is in the word
                self.words = [w for w in self.words if (word[i] in w)]

            elif res[i] == 0:  # Letter not in the word
                # And that letter is in the word
                self.words = [w for w in self.words if (word[i] not in w)]
        return self.words

    def word_proba(self, word):
        # TODO: count proba letter is somewhere else?
        p = 1
        for i in range(len(word)):
            l = word[i]
            rank = self.letter_rank[l]
            p *= self.probas[i][rank]
        return p

    def plot_letters(self):
        plt.figure(figsize=(20, 8))
        for i in range(self.size):
            l = self.probas[i]
            plt.subplot(1, self.size, i+1)
            plt.bar([i for i in self.alphabet], l)
            plt.title(f"Letter #{i}")
        plt.show()

    def plot_words(self):
        assert len(self.words) <= 10000, "Too many words"
        w_p = [self.word_proba(w) for w in self.words]
        plt.figure(figsize=(16, 8))
        plt.bar(self.words, w_p)
        plt.show()

    def solve(self, wordle, verbose=True, random=True):
        self.size = len(wordle.word)
        self.words = [i.lower() for i in self.word_list if len(i) ==
                      self.size]
        self.get_current_probas()
        self.tries = 0
        r = [0]
        while not np.all([i == 2 for i in r]):
            t = self.ask(random=random)
            r = wordle.test(t)
            if verbose:
                print(f"({self.tries+1}) {t} -> {squares(r)}")
#                 print(wordle.word in self.words)
#                 self.plot_letters()
            self.tell(t, r)
        return t
