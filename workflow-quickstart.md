# Basic Workflow Quickstart

The following are some basic workflow tips and reminders.

## Mounting a Tape

When inserting the tape:

- Do NOT force it.  The drive has mechanisms that will guide it inside.
- Wait until the green light steadies before performing any actions – this may take several minutes.
- If the green light goes away and is replaced by an orange “!” light and a number, refer to the drive’s troubleshooting manual as this is an error code.
- If the green light goes away and is replaced by an orange “C”, then eject the tape and insert the cleaning tape.  Wait for it to run and then eject and resume your task.

Use this terminal command to “mount” the tape so it can be used in Debian.
```
~/tape-mount mount
```

> [!WARNING]
> Do not remove the tape while mounted.

## Reading / Writing Files to Tape

Once mounted, you can use it like any other drive with the “Files” app or terminal commands.

Here are some common terminal commands you can use.  Note this assumes you’re using our default mount script, which mounts to “/media/tape”.
- To copy a from an external hard drive to tape:
   ```
   cp –i -r /media/lto-machine/[DriveName/FolderName/] /media/tape/
   ```
   - Don’t forget the trailing “/” on [DriveName] or [FolderName] – otherwise you’ll get an extra top level folder with the name of the drive or folder.
- To copy a folder from tape:
   ```
   cp –i -r /media/tape/[FolderName] [/destination/path/]
   ```
- To copy a specific file:
   ```
   cp –i [/path/to/file.ext] /media/tape/
   cp –i /media/tape/[FolderName/file.ext] [/destination/path/]
   ```
- To monitor copy progress, open a new terminal tab and enter this command:
   ```
   watch -n 5 df /media/tape
   ```
> [!WARNING]
> Do not unmount a tape until all copy operations are completed and all tape noises have subsided.  If the tape is making noises, it’s doing something important! 

## Generate a Media Inventory
The media inventory script is executed via Python using this terminal command.
```
python3 ~/tape-inventory.py
```

This script will ask whether to inventory a tape (1) or an external drive (2).  If you enter “2”, it will list all connected external hard drives and ask you to select one.

The file can be found with these steps:
1.	Open the “Files” app (use the Windows key to open the app search).
2.	Select “Home” and choose the folder called “Media_Inventories”.
3.	Each inventory file uses this naming convention:
   - “(Drive Name) (Date in ISO format – e.g., YYYY-MM-DD)”

Each inventory file will contain the following information for each file:
- SizeInBytes:  The file size in bytes 
- FullFilePath:  Full path, referencing the tape or hard drive name, such as:  DriveName/folder/subfolder/file.mov

## Unmount and Eject a Tape

> [!WARNING]
> Always unmount the tape before physically removing it. Removing a tape without unmounting can corrupt the LTFS index.

Start by closing any windows that are looking at the tape.  Then run this terminal command:
```
~/tape-mount.sh unmount
```

If successful, the tape will rewind, unmount, and eject automatically.

If it does not eject, use this terminal command to manually eject it.  This will confirm that it is not mounted, and attempt to rewind and eject it again.
```
~/tape-mount.sh eject
```

## Format a Tape
>[!NOTE]
> New LTO-9 tapes require a one-time media optimization on first load that can take up to 2 hours. The drive will be active during this time. This is normal.

New tapes must be LTFS formatted before being mounted.  Use this Terminal command.
```
mkltfs -d /dev/sg1 -f -n [TapeVolumeName]
```

Once complete, the tape can now be mounted and used.
