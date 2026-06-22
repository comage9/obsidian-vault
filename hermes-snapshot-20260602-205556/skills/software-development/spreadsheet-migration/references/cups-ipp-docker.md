# CUPS Network Printing to Docker Windows VM (IPP)

## Problem

USB printers connected to the Linux host can only be used by ONE system at a time. When a Docker Windows VM (dockur/windows) claims the USB device via QEMU passthrough, Linux CUPS loses access. Both systems need simultaneous access.

## Solution: CUPS IPP Network Sharing

Instead of USB passthrough to the Windows VM, share printers via CUPS's built-in IPP (Internet Printing Protocol) server.

### Architecture

Printer (USB) → Linux CUPS → IPP (port 631) → Docker bridge (172.17.0.1) → Windows VM

### Setup

**1. Enable CUPS sharing:**
sudo cupsctl --share-printers
CUPS listens on 0.0.0.0:631 by default. Check /etc/cups/cupsd.conf: Port 631

**2. No USB passthrough needed in Docker.**
Remove --device /dev/bus/usb and ARGUMENTS="-device usb-host,..." from docker run.

**3. Find Docker gateway (Windows VM's route to host):**
docker exec WinApps ip route
# Default via 172.17.0.1 dev eth0

**4. In Windows VM, add printer as IPP network printer:**
Control Panel → Devices and Printers → Add Printer → The printer I want isn't listed → Select a shared printer by name → enter:
http://172.17.0.1:631/printers/Canon-G2010

Follow prompts to install driver. Repeat for ZM600:
http://172.17.0.1:631/printers/Zebra-Technologies-ZTC-ZM600-300dpi-ZPL

### Verification
Windows test page → goes through Linux CUPS → USB printer.

### Recovering from USB Passthrough
If previously used --device /dev/bus/usb, after removing it:
1. Power-cycle the printer
2. Verify CUPS sees it: sudo /usr/lib/cups/backend/usb | grep Printer
3. Check: lpinfo -v | grep -i zebra

### Why Not QEMU USB Passthrough?
- Linux CUPS loses access (QEMU holds the USB device)
- Device addresses change on power-cycle
- Needs kernel-mode Windows drivers for every device

| Approach | Linux Access | Windows Access | Stability |
|----------|-------------|----------------|-----------|
| QEMU USB Passthrough | No | Yes | Low (address changes) |
| CUPS IPP Network | Yes | Yes | High |

### Troubleshooting
Windows can't find printer: docker exec WinApps curl -s http://172.17.0.1:631/
CUPS not on bridge: ss -tlnp | grep 631 (should show 0.0.0.0:631)

## LibreOffice Printing with Custom Label Sizes

ZM600 100mm x 60mm labels:
lp -d Zebra-Technologies-ZTC-ZM600-300dpi-ZPL \
  -o media=Custom.283x170 \
  my_label.pdf

283pt = 100mm, 170pt = 60mm (1pt = 1/72 inch)
PPD supports CustomPageSize: Width 36-576pt, Height 36-3600pt.
