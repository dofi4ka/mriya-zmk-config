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

## Flashing firmware

[`burn.py`](./burn.py) copies a UF2 image onto the keyboard in UF2 bootloader mode.

1. Download firmware from [GitHub Actions](https://github.com/dofi4ka/mriya-zmk-config/actions) (or build elsewhere) and place the `.uf2` files in [`firmware/`](./firmware/).
2. Double-tap reset on the half you want to flash, then plug in USB.
3. Run:

```sh
uv run burn.py
```

The script lists removable USB block devices, asks which one is the keyboard, which image to flash (left, right, or settings reset), mounts it, copies the file, and ejects.

Expected files in `firmware/` (names from CI):

- `mriya_left nice_view_adapter nice_view_gem-nice_nano_v2-zmk.uf2`
- `mriya_right nice_view_adapter nice_view_gem-nice_nano_v2-zmk.uf2`
- `settings_reset-nice_nano_v2-zmk.uf2`

On nice!nano, the bootloader usually appears as a **whole disk** (e.g. `/dev/sdc`) with no partition — not `/dev/sdc1`. The script only shows removable USB devices, so system disks are not listed.

System packages: `util-linux` (`lsblk`), `udisks2` (`udisksctl`). Install [uv](https://docs.astral.sh/uv/) to run the script.

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
