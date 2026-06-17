#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Flash a ZMK UF2 image to the keyboard bootloader volume.

Usage:
    uv run burn.py

Expects UF2 files in firmware/ (CI artifact names from GitHub Actions).
System tools: lsblk (util-linux), udisksctl (udisks2) for mount/eject.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIRMWARE_DIR = ROOT / "firmware"

# GitHub Actions artifact names from build-user-config.yml
FIRMWARE_CHOICES: dict[str, tuple[str, str]] = {
    "1": (
        "mriya_left nice_view_adapter nice_view_gem-nice_nano_v2-zmk.uf2",
        "Left half",
    ),
    "2": (
        "mriya_right nice_view_adapter nice_view_gem-nice_nano_v2-zmk.uf2",
        "Right half",
    ),
    "3": (
        "settings_reset-nice_nano_v2-zmk.uf2",
        "Settings reset (clear NVS / Bluetooth)",
    ),
}


def run(
    cmd: list[str],
    *,
    check: bool = True,
    capture: bool = True,
) -> subprocess.CompletedProcess[str]:
    display = " ".join(cmd)
    print(f"+ {display}")
    return subprocess.run(
        cmd,
        text=True,
        capture_output=capture,
        check=check,
    )


def require_tool(name: str, package: str) -> str:
    path = shutil.which(name)
    if not path:
        print(f"{name} not found. Install {package}.", file=sys.stderr)
        sys.exit(1)
    return path


def parse_lsblk() -> list[dict[str, str]]:
    result = run(
        [
            "lsblk",
            "-o",
            "NAME,SIZE,TYPE,MOUNTPOINT,MODEL,TRAN,LABEL,RM,PKNAME",
            "--paths",
            "--pairs",
        ]
    )
    devices: list[dict[str, str]] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        fields: dict[str, str] = {}
        for match in re.finditer(r'(\w+)="([^"]*)"', line):
            fields[match.group(1)] = match.group(2)
        if fields.get("NAME", "").startswith("/dev/"):
            devices.append(fields)
    return devices


def is_removable(dev: dict[str, str], by_name: dict[str, dict[str, str]]) -> bool:
    if dev.get("RM") == "1":
        return True
    if dev.get("TRAN") == "usb":
        return True
    parent = dev.get("PKNAME")
    if parent and parent in by_name:
        return is_removable(by_name[parent], by_name)
    return False


def flashable_devices(devices: list[dict[str, str]]) -> list[dict[str, str]]:
    """Partitions and whole-disk UF2 volumes (e.g. /dev/sdc with no partition table)."""
    by_name = {d["NAME"]: d for d in devices}
    disks_with_parts = {
        d["PKNAME"] for d in devices if d.get("TYPE") == "part" and d.get("PKNAME")
    }

    candidates: list[dict[str, str]] = []
    for dev in devices:
        if not is_removable(dev, by_name):
            continue
        if dev.get("TYPE") == "part":
            candidates.append(dev)
        elif dev.get("TYPE") == "disk" and dev["NAME"] not in disks_with_parts:
            candidates.append(dev)
    return candidates


def format_partition(dev: dict[str, str]) -> str:
    parts = [
        dev.get("NAME", ""),
        dev.get("SIZE", ""),
        dev.get("MODEL", ""),
        dev.get("LABEL", ""),
        dev.get("TRAN", ""),
    ]
    mount = dev.get("MOUNTPOINT", "")
    if mount:
        parts.append(f"mounted at {mount}")
    else:
        parts.append("not mounted")
    return "  ".join(p for p in parts if p)


def pick_device(devices: list[dict[str, str]]) -> str:
    candidates = flashable_devices(devices)
    print("\nRemovable block devices:\n")
    names: list[str] = []
    for index, dev in enumerate(candidates, start=1):
        name = dev["NAME"]
        names.append(name)
        kind = dev.get("TYPE", "dev")
        print(f"  {index}) [{kind}] {format_partition(dev)}")

    if not names:
        print(
            "No removable devices found. Double-tap reset to enter UF2 bootloader, then reconnect USB.",
            file=sys.stderr,
        )
        sys.exit(1)

    while True:
        choice = input("\nKeyboard device number or /dev/sdX path: ").strip()
        if choice.startswith("/dev/"):
            return choice
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(names):
                return names[idx - 1]
        print("Invalid choice.")


def firmware_path(name: str) -> Path:
    return FIRMWARE_DIR / name


def pick_firmware() -> Path:
    print("\nFirmware to flash:\n")
    for key, (filename, label) in FIRMWARE_CHOICES.items():
        path = firmware_path(filename)
        status = "ok" if path.is_file() else "missing"
        print(f"  {key}) {label}")
        print(f"      {path.name}  [{status}]")

    while True:
        choice = input("\nChoice [1-3]: ").strip()
        if choice not in FIRMWARE_CHOICES:
            print("Enter 1, 2, or 3.")
            continue
        filename, _ = FIRMWARE_CHOICES[choice]
        path = firmware_path(filename)
        if not path.is_file():
            print(f"{path} not found. Copy UF2 builds into {FIRMWARE_DIR}/", file=sys.stderr)
            sys.exit(1)
        return path


def current_mountpoint(device: str) -> str:
    result = run(["lsblk", "-no", "MOUNTPOINT", device], check=False)
    return result.stdout.strip()


def mount_device(device: str) -> tuple[str, bool]:
    """Return (mountpoint, mounted_by_script)."""
    mountpoint = current_mountpoint(device)
    if mountpoint:
        return mountpoint, False

    require_tool("udisksctl", "udisks2 (pacman: udisks2)")
    result = run(["udisksctl", "mount", "-b", device], check=False)
    if result.returncode != 0:
        print(result.stderr or result.stdout, file=sys.stderr)
        sys.exit(1)

    mountpoint = current_mountpoint(device)
    if not mountpoint:
        match = re.search(r"at (\S+)", result.stdout)
        mountpoint = match.group(1) if match else ""
    if not mountpoint:
        print(f"Mounted {device} but could not determine mount point.", file=sys.stderr)
        sys.exit(1)
    return mountpoint, True


def eject_device(device: str) -> None:
    if not shutil.which("udisksctl"):
        if shutil.which("eject"):
            run(["eject", device], check=False)
        return

    run(["udisksctl", "unmount", "-b", device], check=False)
    run(["udisksctl", "power-off", "-b", device], check=False)


def flash(mountpoint: str, firmware: Path) -> None:
    dest = Path(mountpoint) / firmware.name
    print(f"\nCopying {firmware} -> {dest}")
    shutil.copy2(firmware, dest)
    print("UF2 copied. The board should reboot and flash automatically.")


def main() -> int:
    require_tool("lsblk", "util-linux")

    if not FIRMWARE_DIR.is_dir():
        print(f"{FIRMWARE_DIR}/ does not exist.", file=sys.stderr)
        return 1

    print("Put the keyboard half in UF2 bootloader mode (double-tap reset), then connect USB.")
    input("Press Enter when ready...")

    device = pick_device(parse_lsblk())
    firmware = pick_firmware()
    mountpoint, we_mounted = mount_device(device)

    try:
        flash(mountpoint, firmware)
    finally:
        if we_mounted:
            print("\nEjecting...")
            eject_device(device)
        else:
            answer = input("\nUnmount/eject now? [Y/n] ").strip().lower()
            if answer in {"", "y", "yes"}:
                eject_device(device)

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
