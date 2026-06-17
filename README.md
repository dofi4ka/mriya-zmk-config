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

## Bluetooth

Bluetooth controls are on the `FUN` layer. Hold the `FUN` thumb key, then use:

- Top row right side: `BT_SEL 0`, `BT_SEL 1`, `BT_SEL 2`, `BT_SEL 3`, `BT_SEL 4`
- Middle row far right: `BT_CLR`
- Bottom row far right: `BT_CLR_ALL`

Use one Bluetooth profile per host device. For example, pair the phone on
`BT_SEL 0`, the laptop on `BT_SEL 1`, and the desktop on `BT_SEL 2`. To switch
between already paired devices, select the matching profile on the keyboard.

If pairing starts failing with authorization, PIN, or passkey errors:

1. Select the broken profile and press `BT_CLR`, or press `BT_CLR_ALL` to clear
   every profile.
2. Remove/forget `MRIYA` in the host device Bluetooth settings.
3. Select the profile again and pair `MRIYA` from scratch.

If the keyboard cannot be controlled from the keymap, flash the `settings_reset`
build once, then flash the normal left/right firmware again.
