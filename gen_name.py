import sys
import random

VOWELS = "aeiou"
CONSONANTS = "bcdfghjklmnpqrstvwxyz"
N_SYLLABLES_RANGE = (2, 2)

def gen_random_syllable():
    v = lambda: VOWELS[random.randint(0, len(VOWELS) - 1)]
    c = lambda: CONSONANTS[random.randint(0, len(CONSONANTS) - 1)]

    combinations = [
        (c, v),
        (v, c),
    ]

    n = random.randint(0, len(combinations)-1)
    combination = combinations[n]
    return "".join([i() for i in combination])

def gen_random_name():
    n = random.randint(N_SYLLABLES_RANGE[0], N_SYLLABLES_RANGE[1])
    parts = []
    for _ in range(n):
        parts.append(gen_random_syllable())
    return "".join(parts)

def main():
    count = 10
    for _ in range(count):
        print(gen_random_name())
    return

if __name__ == "__main__":
    main()