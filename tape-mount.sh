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
