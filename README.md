## ZMK Config for the MRIYA Keyboard

Inspired by Miryoku. With russian language support.

## Formatting

[`format.py`](./format.py) is a small script that auto-aligns the columns in
[`config/mriya.keymap`](./config/mriya.keymap). It looks for blocks delimited by
`/* start format */` / `/* end format */` comments inside the keymap and pads every column
to the same width, keeping the layout readable.

Run it with:

```sh
python format.py
```
