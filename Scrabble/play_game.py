from solver import *
import os
import sys

import requests

def check_word(word):
    url = f"https://lemot.net/{word}"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0",
        "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language" : "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding" : "gzip, deflate, br",
        "Referer": "https://lemot.net/",
        "Cookie": "_ga=GA1.2.1924450147.1672177718; _gid=GA1.2.916462351.1672177718; _gat_gtag_UA_1122275_60=1"
    }
    # print(url)
    r = requests.post(url, headers=headers)
    html = r.text
    if "n'est pas valide" in html:
        return "NOT valid"
    elif "est valide au" in html:
        return "valid"
    elif 'Page non trouvée' in html:
        return "not found"
    else:
        code = r.status_code
        print(html)
        return f"error {code}"

def clear():
    os.system("cls" if os.name == "nt" else "clear") # clear cli
clear()
b = Board()

# get first cli argument
save = None
if len(sys.argv) > 1:
    save = sys.argv[1]
    turns = b.load(save)
else:
    save = input("Save name: ")
    turns = 0

print(b)
sol = []

def is_position(word):
    # check there is 1 letter and 1 or 2 numbers in the word, with number before or after letter
    if len(word) < 2:
        return False
    if word[0].isalpha() and word[1:].isdigit():
        return True
    if word[-1].isalpha() and word[:-1].isdigit():
        return True
    return False
    

while True:
    print("Turns:", turns)
    # get input
    inp = input("Command: ")
    # parse input
    if inp in ["exit", "quit"]:
        break
    args = inp.split()
    if args[0] == "play":
        pos, word = args[1], args[2]
        if not is_position(pos):
            pos, word = word, pos
        if not is_position(pos):
            print("Invalid position")
            continue

        clear()
        b(pos, word)
        turns += 1
        if save != "":
            b.save(save)
        print(b)


    elif args[0] == "solve":
        letters = args[1]
        if turns == 0:
            sol = b.first_step(letters)
        else:
            sol = b.solve(letters)
            

        print(f"--- Solutions: {min(10, len(sol))}/{len(sol)} ---")
        for s in sol[:10]:
            checked = check_word(s)
            print(f" {s} ({checked})")
        
            conflicts = s.row.get_conflicts(s.word, s.start)
            for _, c, i in conflicts:
                checked = check_word(c)
                print(f"    - {c} ({checked})")

        print()

    elif args[0] == "more":
        print(f"--- Solutions: {min(20, len(sol))}/{len(sol)}---")
        for s in sol[:20]:
            checked = check_word(s)
            print(f" {s} ({checked})")
        
            conflicts = s.row.get_conflicts(s.word, s.start)
            for _, c, i in conflicts:
                checked = check_word(c)
                print(f"    - {c} ({checked})")
        print()


    elif args[0] == "cancel":
        if turns == 0:
            print("No turns made")
            continue
        b = Board()
        b.load(save, ignore_last=True)
        b.save(save)
        print(b)
        turns -= 1

    elif args[0] == "check":
        word = args[1]
        checked = check_word(word)
        print(f"{word} is {checked}")

    elif args[0] == "help":
        print("Commands:")
        print(" - play <position> <word>")
        print(" - solve <letters>")
        print(" - more")
        print(" - cancel")
        print(" - exit")
        print(" - help")

    
