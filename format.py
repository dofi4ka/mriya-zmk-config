def format_layout(text):
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

    formatted = ""

    for string in strings:
        formatted += string.rstrip() + "\n"

    return formatted.rstrip()


def format_keymap(text):
    formatted = ""
    current_layout = None

    for line in text.split("\n"):
        if line.strip() == "/* end format */" and current_layout is not None:
            formatted += format_layout(current_layout) + "\n"
            current_layout = None

        if current_layout is None:
            formatted += line.rstrip() + "\n"
        else:
            current_layout += line

        if line.strip() == "/* start format */":
            current_layout = ""
    return formatted.rstrip() + "\n"


with open("config/mriya.keymap", "r") as f:
    keymap = f.read()

with open("config/mriya.keymap", "w") as f:
    f.write(format_keymap(keymap))
