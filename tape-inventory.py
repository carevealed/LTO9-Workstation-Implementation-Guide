#!/usr/bin/env python3

import os
import sys
import datetime
import subprocess
import getpass

MOUNT_POINT = "/media/tape"
EXTERNAL_MOUNT_BASE = f"/media/{getpass.getuser()}"
OUTPUT_DIR = os.path.expanduser("~/Media_Inventories")

def get_volume_name():
    try:
        result = subprocess.run(
            ["attr", "-g", "ltfs.volumeName", MOUNT_POINT],
            capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            line = line.strip()
            if line and not line.startswith("Attribute"):
                return line
    except Exception:
        pass
    return None

def check_mounted():
    with open("/proc/mounts", "r") as f:
        for line in f:
            if MOUNT_POINT in line:
                return True
    return False

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
    with open(output_path, "w") as tsv:
        tsv.write("SizeinBytes\tFullFilePath\n")
        for dirpath, dirnames, filenames in os.walk(source_path):
            for fname in filenames:
                if fname.endswith(".md5"):
                    continue
                full_path = os.path.join(dirpath, fname)
                try:
                    size = os.path.getsize(full_path)
                    relative_path = full_path[len(source_path):]
                    inventory_path = volume_name + relative_path
                    tsv.write(f"{size}\t{inventory_path}\n")
                    file_count += 1
                except OSError:
                    print(f"Warning: Could not read {full_path}, skipping.")
    print(f"Inventory complete. {file_count} files catalogued.")
    print(f"Saved to: {output_path}")

def main():
    print("What would you like to inventory?")
    print("  1. Mounted tape drive")
    print("  2. External hard drive")
    choice = input("Enter 1 or 2: ").strip()
    if choice == "1":
        if not check_mounted():
            print("Error: No tape is currently mounted at " + MOUNT_POINT)
            print("Please run ~/tape-mount.sh mount first.")
            sys.exit(1)
        volume_name = get_volume_name()
        if not volume_name:
            print("Error: Could not read volume name from tape.")
            sys.exit(1)
        print(f"Tape volume name: {volume_name}")
        generate_inventory(MOUNT_POINT, volume_name)
    elif choice == "2":
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
    else:
        print("Error: Invalid selection. Please enter 1 or 2.")
        sys.exit(1)

if __name__ == "__main__":
    main()