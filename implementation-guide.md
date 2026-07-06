# Debian / LTO-9 Workstation Implementation Guide

This guide documents the steps we used to implement a Debian-based LTO-9 read/write workstation.  This is not the only way, and it may not even be the best way.  But it worked for us, so it might work for others.

Debian is our system of choice because it offers native SCSI-based support for LTO-8/9 tapes and an open source LTFS implementation that is much more reliable than Windows.

Our system dual boots with Windows because that's where we started, but that's completely optional.  If you don't need Windows for any reason, I would omit it.  But I've also included dual-boot instructions for those that are interested.

---

## System Requirements

These are the selections and requirements we used for our workstation.

| Component | Details |
|-----------|---------|
| **Motherboard** | We used an MSI B660 board, but any with the following should work: Intel 600 series or newer (B660 / H670, etc.) / AMD X570 or B550 or newer. At least one PCIe x8 or x16 slot for the SAS card. Make sure your CPU cooler isn't blocking this slot. If using a separate graphics card, you will need a second x16 slot. Onboard graphics are more than sufficient. This guide assumes a UEFI BIOS. Legacy BIOS is certainly possible but it may require different steps. |
| **CPU** | Any compatible Intel i3/i5/i7 / AMD Ryzen 5 or above. If using a separate graphics card on an Intel chipset, you may want to stick with i5+ to ensure you have enough PCIe lanes. |
| **RAM** | At least 16 GB. 8 GB only if you use Debian w/o a user interface (terminal only). |
| **Storage** | 256GB SSD minimum / 500 GB NVMe SSD recommended. SATA SSDs are fine but NVMe SSDs are much more responsive. |

---

## Windows Configuration (Optional)

If you want Windows as well as Debian, the easiest method is to dual boot – this means both on the same hard drive and a boot screen asks which to load when you start the machine.

If you're using a SAS card like we are, most Virtual Machine (VM) software cannot use it without major effort and/or money.  We opted to use the SAS card after running into Thunderbolt's messy compatibility and the drive's tendency to overheat.  But if you figure out a USB/Thunderbolt drive cage that works, you can also use VMs instead of these instructions.

That said, while it seems counterintuitive, dual booting was easier for us.

### Enabling LTO-9 on Windows

An LTO-9 machine on Windows cannot reliably use backwards compatible LTO-8 tapes, but it can still use LTO-9 tapes if it's easier to do something that isn't mission critical.

Here's how we got Windows to use LTO-9 tapes with our setup:

- Download the Quantum LTO Windows software and driver from: <https://quantum.com/en/service-support/downloads-and-firmware/lto-std>

- Install the drivers and reboot.

- Open Device Manager (Windows Key + search for Device Manager).

- Make sure the drive appears under "Tape Drives".

- Go to the following link and create / log into a free IBM account: <https://ibm.com/support/fixcentral>

- Navigate to System Storage -> Tape systems -> Tape drivers and software -> IBM Spectrum Archive SDE -> Windows.

- Download and install the latest version.

- Open the LTFS Configuration software and assign a drive letter (such as T:)

### Shrink the Windows Partition

Before installing Debian, you'll need to make space for it.  These steps assume Windows is already installed, but you can do all this rather easily as part of the Windows installation:

- Open Disk Management (Windows Key + search for Disk Management).

- Right-click the C: partition and select Shrink Volume.

- Enter the amount you want for Debian in MB.  For example, to keep Windows at 300 GB on a 1TB drive, enter "645120" MB.  Note that we will use 8 GB of this for "Swap" later.

- Click Shrink. Leave the "unallocated space" as-is.  Do not create a new partition.

---

## 1 - Create the Debian Installer USB

There are plenty of tutorials and methods for creating boot USBs with Linux distributions online, but for completeness, here are the steps we used on our Windows machine:

- Download the latest Debian 13 netinst ISO from <https://debian.org/download>

- Download Rufus (portable is fine and requires no installation) from <https://rufus.ie>.

- Insert a USB drive of 4GB size or greater.

- Run the downloaded Rufus executable.

- Select the USB drive and choose the downloaded Debian ISO.

- Set the following:

  - Partition Scheme: If using a newer UEFI motherboard, choose "GPT". Otherwise use "MBR"

  - Target System: If using a newer UEFI motherboard, choose "UEFI (non CSM)". Otherwise, choose "BIOS (UEFI-CSM)"

- Click Start.

- When prompted, select "ISO Image" mode.

- Wait for the flash to finish.

---

## 2 - Install Debian

- Check your motherboard manual to learn how to enter the boot menu (typically F11, F10, or DEL) – or confirm in the BIOS that it's set to boot to the USB drive.

- Restart the computer with the USB drive inserted.

- When the motherboard logo appears, repeatedly hit the noted button until you enter the boot menu.

- Select the USB drive.

- At the Debian Installer menu, select "Graphic Install."

### 2.1 - Installer Configuration

- Choose your language, location, and keyboard style.

- Hostname: Enter a name for the workstation.

- Domain name: Leave this on the default of blank or "localdomain" unless you have IT staff that set up a specific domain that the workstation needs to connect to.

- Root Password: This is separate from a user account password and is asked for whenever you try to access privileged resources – which you will do a lot during initial configuration. Best practice is to use a separate strong password.

- User Account: Create an appropriate account name and password for login.

### 2.2a - Partitioning (Dual Boot)

> **Warning**: ONLY use these instructions if using BOTH Windows and Debian on the same drive. Otherwise, see "Partitioning (Debian Only)".

- Select "Manual partitioning" – this is *critical* to avoid touching the Windows partition.

- Locate the FREE SPACE block that should be about the same size as the block you created in Windows earlier.

- Create a new partition – start with the Swap partition

  - Use as: Swap Area

  - Set to 8 GB

- Create a second partition from the rest of the FREE SPACE block – this will be the primary Debian partition.

  - Use as: ext4 journaling file system

  - Mount Point: /

  - Set to the remainder of the FREE SPACE

- Select "Finish partitioning and write the changes to disk" and confirm with "Yes".

### 2.2b - Partitioning (Debian Only)

> **Warning**: ONLY use these instructions if you ONLY want Debian on the workstation. Otherwise, see "Partitioning (Dual Boot)".

- Select "Guided partitioning".

- Select "Use entire disk".

- Select the target drive

- Select "All files in one partition".

- Select "Finish partitioning and write the changes to disk" and confirm with "Yes".

### 2.3 - Package Selection

- Select "No" for the popularity contest. This is just asking to send extra telemetry data.

- On the "Software selection" screen, check these boxes:

  - Debian desktop environment

  - GNOME (if you want the user interface)

  - SSH server

  - Standard system utilities

- Click "Continue". The installation should take about 10 – 30 minutes.

- Choose to install GRUB to "/dev/nvme0n1" when prompted.

- Remove the USB drive when asked to do so. Continue to reboot.

---

## 3 - Fix GRUB Boot Order (Dual Boot Only)

After installation, the system may boot directly into Windows without asking. If this happens, here's how to fix it:

- Go to <https://easyuefi.com>, download, and install the EasyUEFI tool.

- Open EasyUEFI and click "Manage EFI Boot Option".

- Locate the "Debian" entry in the boot list.

- Use the up arrow to move "Debian" above Windows Boot Manager.

- Click Save and reboot. You should now see the GRUB menu on boot, which asks whether to load Debian or Windows.

### 3.1 - Set GRUB Timeout and Default OS

By default, the GRUB boot loader will load Debian if you don't choose anything after a few seconds. To change this, you can do the following:

- Boot into Debian and log in

- Type "Terminal" and hit ENTER or click to open it.

- Type the following command:

```
sudo nano /etc/default/grub
```

- Enter your root password when asked.

- Terminal will now open a text file and show you the contents. Look for the following and change them as desired:

  - GRUB_DEFAULT: 0 by default – which will boot into Debian. Set to 1 to boot windows on default instead.

  - GRUB_TIMEOUT: Set to the number of seconds until it boots into the default.

- Use CTRL + X to save the file

- Enter the following command to load the change into the GRUB boot loader.

```
sudo update-grub
```

---

## 4 - Configure and Set Up Debian

Great! You now have Debian installed. But it's not ready to go out of the box. You still need to set it up to use your LTO-9 drive and create the workflow for your team. Here's how we configured our machine.

### 4.1 – Add First User to Sudo Group

In Linux/Unix-based OSes like Debian, "sudo" refers to "superuser do" as in "execute this with super user permissions" and is needed to do the things we need to do with an LTO-9 drive.

To run "sudo" commands, a user must be added to the "sudo user group". Debian does not add our initial user to this group by default, so we need to do it now with these steps:

- Boot into Debian and log in

- Type "Terminal" and hit ENTER or click to open it.

- Type the following commands:

```
su -
adduser [YourUserName] sudo
reboot
```

- Once the machine reboots, log back into Debian.

- Open Terminal again and verify sudo works with this command:

```
sudo whoami
```

- You should see the output of "root".

### 4.2 – Update the System and apt Repositories

- Now use this Terminal command to update the "apt" software repository and apply any updates:

```
sudo apt update && sudo apt upgrade -y
```

> **Note:** Its generally good practice to run this command before you start installing any software packages for the day.

### 4.3 - Install Tape Tools & Dependencies

We'll now install several tools and dependencies we will need to interact with tapes, such as:

- mt: Provides basic functions like rewinding, seeking, and ejecting.

- lsscsi: Useful for confirming the drive is connected and which node it's mapped to.

- sg3-utils: A toolkit for interacting with SCSI drives and running diagnostics.

- build-essential / autoconf / automake / libtool: A toolchain required to compile the LTFS package.

- fuse / libfuse / libxml2: FUSE is used by LTFS to show the tape as a file system.

- To install the tools, open "Terminal" and run these commands:

```
sudo apt install -y mt-st mtx tar lsscsi sg3-utils attr build-essential
sudo apt install -y libfuse-dev libfuse3-dev libxml2-dev libicu-dev uuid-dev
sudo apt install -y autoconf automake libtool pkg-config fuse libsnmp-dev uuid git
```

- Now we want to verify the setup. Put a tape in the drive and run this command:

```
lsscsi
```

- You should see the SAS card (ATTO VirtualSES) and  tape drive (QUANTUM ULTRIUM-HH9).

> **Note:** The device paths assigned to your SAS card and tape drive depend on your specific hardware configuration and may differ from the paths shown in this guide. To confirm which device your tape drive is mapped to, run:
> ```
> ltfs -o device_list
> ```
> Use the path shown in this list in place of `/dev/sg1` in any subsequent commands that reference it. The `/dev/st0` path for the tape device is generally consistent across configurations but is also worth verifying with `lsscsi`.

- Now check the status of the tape drive. Make sure to adjust “/dev/st0” as needed based on the device number shown in the command from step 10:

```
sudo mt -f /dev/st0 status
```

- You should see a status of "ONLINE" and the correct density code for the loaded tape (LTO-8 = 0x5e / LTO-9 = 0x5a).

### 4.4 – Build and Install LTFS

LTFS is not in the standard Debian repositories, so we need to compile it from the source:

- Enter this Terminal command to copy the LTFS source code from their git repo:

```
git clone https://github.com/LinearTapeFileSystem/ltfs.git
```

- Now navigate into the cloned copy and initialize the submodules:

```
cd ltfs
git submodule update --init --recursive
```

- When we implemented, the LTFS build script referenced an ICU package name that has a different name on Debian. Update the script using this Terminal command:

```
sed -i '344s/\[icu >= 0.21\]/[icu-uc >= 0.21]/' configure.ac
```

- Now build and install with these commands:

```
./autogen.sh
./configure
make
sudo make install
sudo ldconfig
```

- To verify the install, run these Terminal commands. Both should show 2.4.x or later:

```
ltfs --version
mkltfs --version
```

### 4.5 – Configure Device Permissions

Now we're going to create and assign a "udev" permission rule so that our users don't have to enter a "sudo" password every time they try to interact with the tape.

- Enter this command in Terminal to start the rule:

```
sudo nano /etc/udev/rules.d/99-tape.rules
```

- The rule file now opens directly in Terminal.  Enter these lines into the open file:

```
SUBSYSTEM=="scsi_generic", MODE="0660", GROUP="tape"
SUBSYSTEM=="scsi_tape", MODE="0660", GROUP="tape"
```

- Save the changes by hitting CTRL+X. When prompted, type "y" and hit enter.

- Now reload udev to apply the new rule with these Terminal commands:

```
sudo udevadm control --reload-rules
sudo udevadm trigger
```

- You might have noticed that we added a "tape" permission group in the file above. We now need to add our user to this group with this Terminal command:

```
sudo usermod -aG tape $USER
```

- By default, FUSE (used by LTFS) only permits drive access to the user that mounted the drive. If a drive could be used by multiple users before being unmounted, run this Terminal command:

```
sudo nano /etc/fuse.conf
```

Then remove the "#" character on the line user_allow_other.

Save the file with CTRL+X, Y, ENTER

- We also created a group for “FUSE” because it was necessary for older versions (FUSE2).  FUSE3 handles permissions differently now, but this prevents legacy issues:

```
sudo addgroup fuse
sudo usermod -aG fuse $USER
```

- Log out and back in to apply all group changes.

### 4.6 – Create the Mount Point

- Finally, use these Terminal commands to 1) Create the place where our tape will be mounted, 2) Ensure our user can mount the tape without sudo, and 3) Set permissions so that our user has full control over that mount point:

```
mkdir -p /media/tape
sudo chown $USER:$USER /media/tape
sudo chmod 755 /media/tape
```

### 4.7 – Create Convenient Mount / Unmount Script

To make things a little easier for our team, we created a script that provides a simple command for mounting and unmounting the tape as well as manually ejecting it as needed. This script can be run in three ways from Terminal:

- `~/tape-mount.sh mount` — Automatically mounts the currently inserted tape to the "/media/tape" mount point.

- `~/tape-mount.sh unmount` — Automatically rewinds, unmounts, and ejects the tape.

- `~/tape-mount.sh eject` — Can be used to manually eject the tape as needed. This command ensures the tape is not mounted and manually rewinds and ejects it.

- Start by running this command in Terminal to create the script. Feel free to change the name from "tape-mount" to whatever you want:

```
nano ~/tape-mount.sh
```

- Now paste in the script included below and save it with CTRL+X, Y, then ENTER.

- Once saved, you'll also need to make it executable with this Terminal command. If you changed the name of the script, change it here too:

```
chmod +x ~/tape-mount.sh
```

```bash
#!/bin/bash

case "$1" in
  mount)
    # Replace /dev/sg1 with your tape dev path (ltfs -o device_list)
    ltfs -o devname=/dev/sg1,allow_other /media/tape
    echo "Tape mounted at /media/tape"
    ;;

  unmount)
    if mount | grep -q /media/tape; then
      if umount /media/tape 2>/dev/null; then
        echo "Unmounted successfully, rewinding..."
        mt -f /dev/st0 rewind
        sleep 5
        echo "Ejecting..."
        mt -f /dev/st0 eject
        if [ $? -eq 0 ]; then
          echo "Tape ejected successfully"
        else
          echo "Auto-eject failed. Try: mt -f /dev/st0 eject or press the drive button manually"
        fi
      else
        echo "Error: Could not unmount tape - drive may still be in use. Close any open files or windows and try again."
      fi
    else
      echo "Error: No tape is currently mounted"
    fi
    ;;

  eject)
    echo "Warning: Only use this command if you already ran unmount but the tape did not eject."
    read -p "Do you want to proceed? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
      if mount | grep -q /media/tape; then
        echo "Error: The tape is still mounted. Please run ~/tape-mount.sh unmount first."
      else
        echo "Rewinding..."
        mt -f /dev/st0 rewind
        sleep 5
        echo "Ejecting..."
        mt -f /dev/st0 eject
        if [ $? -eq 0 ]; then
          echo "Tape ejected successfully"
        else
          echo "Auto-eject failed. Press the drive button manually."
        fi
      fi
    else
      echo "Aborted."
    fi
    ;;

  *)
    echo "Usage: tape-mount.sh [mount|unmount|eject]"
    ;;
esac
```

---

## 5 – Setup Media Inventory Workflow

Once all read/write operations on a tape and checksums are done, we use a python script (.py) to automatically generate a media inventory.  This script can inventory a mounted tape or a connected external hard drive as needed.

Specifically, the script performs these steps:
1. Asks the user whether to inventory a tape (1) or an external hard drive (2).
2.	If tape is chosen, the script confirms that it is mounted.  If external hard drive is chosen, it will show all connected external hard drives and ask which to inventory.
3.	Creates an output folder at “~/Media_Inventories/” if it doesn’t already exist.
4.	Creates a tab-separated (TSV) media inventory file with the file name of:  
   - “(Drive Name) (Date in ISO format – e.g., YYYY-MM-DD)”
5.	Fills the media inventory file the following information for each file in the drive, skipping MD5 files and directory entries:
   - Column 1 – SizeinBytes:  Shows the total size of the file in bytes.  For example, a 20 MB file would be listed as 20,971,520 bytes.
   - Column 2 – FullFilePath:  Shows the file name and relative path, including the name of the drive.  For example, “/media/tape/folder1/file.mov” would become “DriveName/folder1/file.mov”.

Start by running this command in Terminal to create the script.  Feel free to change the name from “tape-mount” to whatever you want:

```
nano ~/media-inventory.sh
```

Now paste in the script included below and save it with CTRL+X, Y, then ENTER.  Remember to make it executable after saving this Terminal command.  If you changed the name of the script, change it here too

```
chmod +x ~/media-inventory.sh
```
Once added, you can use this script with the following command:

```
python3 ~/tape-inventory.py
```

```
#!/usr/bin/env python3

import os
import sys
import datetime
import subprocess
Import getpass

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
```

## 6 - Verification and Testing

Run these tests in Terminal to verify the system is working correctly.

### Verify Drive is Visible

```
lsscsi
```
You should see entries for the ATTO HBA (ATTO VirtualSES) and the tape drive (QUANTUM ULTRIUM-HH9).

### Format a New Tape

1. Start by inserting a blank tape.
2. Wait for the green light to settle, then run this command:
```
mkltfs -d /dev/sg1 -f -n "[VolumeName]"
```

### Test a Mount and write

3.	Use the mount/unmount script script you created above to mount the formatted drive.
```
~/tape-mount.sh mount
```
4.	Now create a test file to write.
```
echo 'test' > /media/tape/test.txt
```
5.	Then check that it was written properly.  You should see the word “test”.
```
cat /media/tape/test.txt
```

### Test Media Inventory

6.	Use this command to run the media inventory python script we created earlier.  Feel free to add more files to the tape prior to running this script for more extensive testing.
```
python3 ~/tape-inventory.py
```
7.	Type “1” for tape and hit ENTER to confirm.
8.	Once finished, check for an inventory file in “~/Media_Inventories/” and verify that the file name and contents are accurate.
9.	As desired, plug in an external hard drive and use the “2” option to test it as well.

### Unmount a Drive
10.	When finished testing, unmount the drive using your mount/unmount script and check for any issues or errors.
```
~/tape-mount.sh unmount
```

