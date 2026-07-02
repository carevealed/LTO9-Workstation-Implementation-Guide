# LTO-9 Workstation Implementation Guide

This guide documents the steps we used to implement a Debian-based LTO-9 read/write workstation.  This is not the only way, and it may not even be the best way.  But it worked for us, so it might work for others.

## Why Debian?

Windows lacks native LTO tape driver support and the existing drivers have known compatibility issues with using LTO-8 media in LTO-9 drives.  Debian, on the other hand, provides reliable SCSI tape support out of the box along with a stable LTFS implementation that handles both LTO-8 and LTO-9 tapes cleanly.

## What's Included

- **[Implementation Guide](implementation-guide.md)** — Step-by-step setup instructions covering both standalone Debian and dual boot (Windows + Debian) configurations.
- **[tape-mount.sh](tape-mount.sh)** — Convenience script for mounting, unmounting, and ejecting tapes.
- **[tape-inventory.py](tape-inventory.py)** — Python script for generating TSV file inventories of tape or external drive contents.
- **LTO-9 Workstation Implementation Guide.docx** — Word version of the implementation guide.

## Hardware Used in This Implementation

- ATTO ExpressSAS H1244GT SAS HBA
- Quantum LTO-9 Half-Height SAS tape drive
- MSI B660 motherboard (any compatible board with a PCIe x8 slot should work)

## Contributing

This guide was developed for [California Revealed](https://californiarevealed.org) as a community resource. Contributions and corrections are welcome via pull request.
