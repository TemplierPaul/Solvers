import pandas as pd
from glob import glob

alphabet = "abcdefghijklmnopqrstuvwxyz"


# Replace accent letters with letters without accents
def replace_accents(df):
    to_replace = {
        "a": ["á", "à", "ä", "â"],
        "e": ["é", "è", "ë", "ê"],
        "i": ["í", "ì", "ï", "î"],
        "o": ["ó", "ò", "ö", "ô"],
        "u": ["ú", "ü", "ù", "û"],
        "n": ["ñ"],
        "c": ["ç"]

    }
    for k, v in to_replace.items():
        for letter in v:
            df = df.str.replace(letter, k)
    return df

def get_files():
    L = []
    for file in glob("data/*.txt"):
        print(file)
        df = pd.read_csv(file, header=None)[0]
        df = df.str.lower()
        df = replace_accents(df)
        # Drop nan
        df = df.dropna(axis = 0)
        # Drop words with -
        df = df[~df.str.contains("-")]
        # Drop words with '
        df = df[~df.str.contains("'")]
        L += df.tolist()

    L = list(set(L))
    len(L)
    L.pop(1)
    return L

def count_letters(word):
    word = word.lower()
    # Return a list with the number of times each letter appears in the word
    return [word.count(letter) for letter in alphabet]

def parse_data():
    L = get_files()
    # Create a dataframe with the number of times each letter appears in each word
    df = pd.DataFrame(L, columns=["word"])
    count = df.applymap(count_letters) # Apply the function to each word
    count = count["word"].apply(pd.Series) # Convert the list of lists into a dataframe
    count = count.fillna(0) # Replace NaN with 0
    count = count.astype(int) # Convert to integer
    count.columns = list(alphabet)

    df = pd.concat([df, count], axis=1)
    df["length"] = df["word"].apply(len)
    return df

def get_words(letters, words):
    df = words.copy()
    letters_count = count_letters(letters)
    for i, letter in enumerate(alphabet):
        df = df[df[letter] <= letters_count[i]]
    # get word with highest length
    df = df.sort_values("length", ascending=False)
    return df