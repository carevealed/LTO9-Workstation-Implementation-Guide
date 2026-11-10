#!/usr/bin/env python3
"""tape-inventory.py - make a TSV inventory of a mounted LTFS tape (LTO-8 or LTO-6)
or of an external hard drive.

Usage: tape-inventory.py [lto8|lto6|external]
Leave the option out and the script asks.

Every file is listed, including .md5 sidecars and hidden or system files.
Filtering is left to the tools that read the inventory (car_pvr_verify.py).
Only the tape index is read (names and sizes), never file contents.
Folders or files that cannot be read are reported on screen and counted.
"""

import os
import sys
import datetime
import subprocess
import getpass

USAGE = "Usage: tape-inventory.py [lto8|lto6|external]"

# One mount folder per drive (must match tape-mount.sh)
TAPE_MOUNTS = {
    "lto8": "/media/tape-lto8",
    "lto6": "/media/tape-lto6",
}
TAPE_LABELS = {
    "lto8": "LTO-8",
    "lto6": "LTO-6",
}
EXTERNAL_MOUNT_BASE = f"/media/{getpass.getuser()}"
OUTPUT_DIR = os.path.expanduser("~/Media_Inventories")


def get_volume_name(mount_point):
    try:
        result = subprocess.run(
            ["attr", "-g", "ltfs.volumeName", mount_point],
            capture_output=True, text=True
        )
    except FileNotFoundError:
        print("Error: the 'attr' command is not installed.")
        print("Install it with: sudo apt install attr")
        return None
    except Exception:
        return None
    for line in result.stdout.splitlines():
        line = line.strip()
        if line and not line.startswith("Attribute"):
            return line
    return None


def get_external_drives():
    drives = []
    if os.path.exists(EXTERNAL_MOUNT_BASE):
        for entry in os.listdir(EXTERNAL_MOUNT_BASE):
            full_path = os.path.join(EXTERNAL_MOUNT_BASE, entry)
            if os.path.ismount(full_path):
                drives.append(entry)
    return drives


def generate_inventory(source_path, volume_name):
    date_str = datetime.date.today().isoformat()
    filename = f"{volume_name}_Inv_{date_str}.tsv"
    output_path = os.path.join(OUTPUT_DIR, filename)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file_count = 0
    problems = []

    def folder_error(err):
        # Without this, os.walk silently leaves out any folder it cannot open.
        print(f"Warning: Could not open folder {err.filename}, skipping it: {err.strerror}")
        problems.append(err.filename)

    # utf-8 + surrogateescape: names that are not valid UTF-8 are written back
    # byte for byte instead of crashing the run.
    with open(output_path, "w", encoding="utf-8", errors="surrogateescape") as tsv:
        tsv.write("SizeinBytes\tFullFilePath\n")
        for dirpath, dirnames, filenames in os.walk(source_path, onerror=folder_error):
            for fname in filenames:
                full_path = os.path.join(dirpath, fname)
                try:
                    size = os.path.getsize(full_path)
                    relative_path = full_path[len(source_path):]
                    inventory_path = volume_name + relative_path
                    tsv.write(f"{size}\t{inventory_path}\n")
                    file_count += 1
                except OSError:
                    print(f"Warning: Could not read {full_path}, skipping.")
                    problems.append(full_path)
    print(f"Inventory complete. {file_count} files catalogued.")
    if problems:
        print(f"WARNING: {len(problems)} file(s) or folder(s) could not be read and are NOT in the inventory.")
    print(f"Saved to: {output_path}")


def choose_source():
    for arg in sys.argv[1:]:
        a = arg.lower()
        if a in ("lto8", "8"):
            return "lto8"
        if a in ("lto6", "6"):
            return "lto6"
        if a in ("external", "ext", "hdd"):
            return "external"
        print(f"Unknown option: {arg}")
        print(USAGE)
        sys.exit(1)
    print("What would you like to inventory?")
    print("  1. LTO-8 tape (mounted)")
    print("  2. LTO-6 tape (mounted)")
    print("  3. External hard drive")
    choice = input("Enter 1, 2 or 3: ").strip()
    if choice == "1":
        return "lto8"
    if choice == "2":
        return "lto6"
    if choice == "3":
        return "external"
    print("Error: Invalid selection. Please enter 1, 2 or 3.")
    sys.exit(1)


def inventory_tape(kind):
    mount_point = TAPE_MOUNTS[kind]
    label = TAPE_LABELS[kind]
    if not os.path.ismount(mount_point):
        print(f"Error: No {label} tape is currently mounted at {mount_point}")
        print(f"Please run ~/tape-mount.sh mount {kind} first.")
        sys.exit(1)
    volume_name = get_volume_name(mount_point)
    if not volume_name:
        print("Error: Could not read volume name from tape.")
        sys.exit(1)
    print(f"{label} tape volume name: {volume_name}")
    generate_inventory(mount_point, volume_name)


def inventory_external():
    drives = get_external_drives()
    if not drives:
        print("Error: No external drives found.")
        print("Please plug in the drive and try again.")
        sys.exit(1)
    print("Available external drives:")
    for i, drive in enumerate(drives, 1):
        print(f"  {i}. {drive}")
    drive_choice = input("Enter the number of the drive to inventory: ").strip()
    try:
        drive_index = int(drive_choice) - 1
        if drive_index < 0 or drive_index >= len(drives):
            raise ValueError
    except ValueError:
        print("Error: Invalid selection.")
        sys.exit(1)
    selected_drive = drives[drive_index]
    source_path = os.path.join(EXTERNAL_MOUNT_BASE, selected_drive)
    generate_inventory(source_path, selected_drive)


def main():
    source = choose_source()
    if source == "external":
        inventory_external()
    else:
        inventory_tape(source)


if __name__ == "__main__":
    main()
