import sys

text = sys.stdin.read()

symbols = [f"&{s.strip()}" for s in text.split("&")[1:]]

space = ["    "]

table = [
    symbols[:6] + [""] + space + [""] + symbols[6:12],
    symbols[12:18] + [""] + space + [""] + symbols[18:24],
    symbols[24:30] + [""] + space + [""] + symbols[30:36],
    [""] * 4 + symbols[36:39] + space + symbols[39:42] + [""] * 4,
]

max_lengths = []

for column in zip(*table):
    max_lengths.append(max(len(cell) for cell in column))

strings: list[str] = []

for row in table:
    strings.append("")
    for cell, max_length in zip(row, max_lengths):
        strings[-1] += f"{cell:<{max_length + 3}}"

for string in strings:
    print(string.rstrip())
