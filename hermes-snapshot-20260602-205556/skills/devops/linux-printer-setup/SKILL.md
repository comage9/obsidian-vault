---
name: linux-printer-setup
description: Add, configure, and verify USB printers on Ubuntu Linux via CUPS — handle driver selection, auto-detection, duplicates, and verification
category: devops
---

# Linux Printer Setup (CUPS)

## Trigger

Use this skill when the user asks you to:
- Add / install / set up a printer on Linux
- Check what printers are connected or configured
- Install printer drivers
- Fix a printer that isn't showing up or printing
- The user references a blog/guide about printer driver installation

## Diagnostic Flow

### 1. Check Current Printer Status

```bash
# List all printers with their status
lpstat -a
lpstat -t         # verbose: scheduler, device URIs, acceptance
lpstat -s         # system summary
```

### 2. Check USB Devices

```bash
lsusb                           # list all USB devices (look for printer manufacturer/model)
lpinfo -v                       # list all CUPS-visible device URIs
lpinfo -v | grep usb://         # just USB printers
```

The USB device from `lsusb` (e.g. `Canon, Inc. G2010 series`) should match a CUPS device URI (e.g. `usb://Canon/G2010%20series?serial=...`).

### 3. Find Available PPD/Drivers

```bash
# Search for specific model
lpinfo -m | grep -i "<manufacturer>" | grep -i "<model>"

# Example patterns:
lpinfo -m | grep -i "canon" | grep -i "g20"
lpinfo -m | grep -i "zebra" | grep -i "zm600"
```

**Common driver sources:**
- **Gutenprint** (`printer-driver-gutenprint`): Broad support for Canon, Epson, HP, and many others. Usually pre-installed on Ubuntu.
- **Foomatic** (`foomatic-db-*`): Legacy database. Many Canon models available.
- **Manufacturer PPDs**: HP (`printer-driver-hpcups`), Brother, and others may have their own packages.
- **cnijfilter2** (Canon): Proprietary Canon driver. Installable via PPA (`ppa:thierry-f/fork-michael-gruz`) or downloaded from Canon's site.

### 4. Install Driver (if needed)

```bash
# Gutenprint (already installed on most Ubuntu systems)
sudo apt install printer-driver-gutenprint

# Canon cnijfilter2 via PPA (for G2000/G3000/MG series)
sudo add-apt-repository -y ppa:thierry-f/fork-michael-gruz
sudo apt update
sudo apt install cnijfilter2 scangearmp2

# Canon cnijfilter2 direct download (if PPA fails)
wget http://gdlp01.c-wss.com/gds/5/0100006265/01/cnijfilter2-5.00-1-deb.tar.gz
tar xvzf cnijfilter2-5.00-1-deb.tar.gz
cd cnijfilter2-5.00-1-deb
./install.sh
```

### 5. Add the Printer

**Check if user has lpadmin group membership (avoids sudo):**

```bash
groups               # check for 'lpadmin' in output
```

If user is in `lpadmin` group, run `lpadmin` without `sudo`:

```bash
lpadmin -p <printer-name> \
  -v "<device-uri>" \
  -m "<ppd-or-driver-uri>" \
  -E
```

**Example (Canon G2010 via Gutenprint):**

```bash
lpadmin -p Canon-G2010 \
  -v "usb://Canon/G2010%20series?serial=0718AB&interface=1" \
  -m "gutenprint.5.3://bjc-G2000-series/expert" \
  -E
```

If user is NOT in `lpadmin` group, use `sudo` (will need password).

### 6. Handle CUPS Driverless Auto-Detection

Modern CUPS automatically detects IPP Everywhere / AirPrint capable printers and adds them with auto-generated names. This creates **duplicate printers** — one from auto-detection and one from manual addition.

After adding a printer, check:

```bash
lpstat -a
```

If duplicates exist, remove the auto-detected one (usually has the generic model name like `G2010-series`):

```bash
lpadmin -x <auto-detected-name>
```

**Two distinct duplicate patterns:**

1. **Driverless auto-detection** — CUPS discovers the printer via mDNS/Avahi and adds it as an IPP Everywhere queue with a name like `Canon_G2010_series`. The device URI is `dnssd://...` or `ipp://...`. The manually-added USB queue (`usb://...`) is the real one — remove the auto-detected duplicate.

2. **IPP shared-printer loopback** — When CUPS printer sharing is enabled (`cupsctl --share-printers`), Avahi advertises the locally-connected printer on the network. CUPS browsing then re-discovers its own shared printer and adds a **second queue pointing back to itself** with a name like `Canon_G2010_comage_A320M_H` (suffix = hostname). Device URI: `ipps://localhost:631/printers/Canon-G2010`. This is a self-referencing duplicate — remove it: `lpadmin -x Canon_G2010_comage_A320M_H`.

To tell them apart, check device URIs:
```bash
lpstat -v
# usb://...           → real printer (keep)
# ipps://localhost:631/printers/... → self-referencing duplicate (remove)
# ipp://... or dnssd://...  → auto-detected duplicate (remove)
```

### 7. Verify

```bash
# List all printers
lpstat -a

# Show printer capabilities
lpoptions -p <printer-name> -l

# Print test page
lp -d <printer-name> /usr/share/cups/data/testprint.ps

# Check print queue
lpq -P <printer-name>
```

## Canon-Specific Notes

- **Model mapping:** Canon G2010 works with the `G2000 series` Gutenprint driver. Canon G2910/G2900 similarly use the G2000 or MG2900 series driver.
- **cnijfilter2** provides superior quality but is proprietary. Gutenprint offers broader compatibility without PPA.
- The blog's PPA (`ppa:thierry-f/fork-michael-gruz`) is an unofficial fork providing cnijfilter2 for modern Ubuntu versions.
- Canon PIXMA models also follow this pattern (e.g., PIXMA G2000 → `bjc-PIXMA-G2000` driver).
- **Scanner support:** `scangearmp2` package provides scanner driver for Canon G-series. Install separately if scanning is needed.

## Zebra ZM600 / ZPL Label Printer Notes

### Driver Selection
Zebra ZM600 supports both **ZPL** (Zebra Programming Language) and **EPL** (Eltron). Use ZPL.

```bash
# Available Zebra drivers:
lpinfo -m | grep -i "zebra"
# drv:///sample.drv/zebra.ppd    → Zebra ZPL Label Printer (correct for ZM600)
# drv:///sample.drv/zebraep2.ppd → Zebra EPL2 Label Printer (wrong for ZPL)
```

**Install the ZPL driver:**
```bash
lpadmin -p <printer-name> -m "drv:///sample.drv/zebra.ppd"
```

### CUPS Filter Chain
The ZPL PPD uses `rastertolabel` filter:
```
*cupsFilter: "application/vnd.cups-raster 50 rastertolabel"
```
This filter converts CUPS raster data to the printer's native format (ZPL bitmap commands like `^GFA`).

### Custom Page Size (e.g. 100mm × 60mm)
The PPD page sizes are in **PostScript points** (1pt = 1/72 inch):
- 100mm = 100 / 25.4 × 72 = **283 pt**
- 60mm = 60 / 25.4 × 72 = **170 pt**

Available predefined sizes include `wXXXhYYY` format (XXX × YYY points):
```bash
lpoptions -p <printer-name> -l | grep PageSize
```

Set custom size:
```bash
lpadmin -p <printer-name> -o media=Custom.283x170
# Or per-job:
lp -d <printer-name> -o media=Custom.283x170 <file>
```

### Direct USB ZPL Test (Bypass CUPS)
To verify the printer is responding at the hardware level:
```bash
# Find the USB lp device
ls -la /dev/usb/lp*
# Should show /dev/usb/lpN (N = 0, 1, 2...)

# Send raw ZPL
echo '^XA^FO50,50^ADN,36,20^FDHELLO^FS^XZ' | sudo tee /dev/usb/lpN
```
- **Prints** → Printer HW + USB OK; problem is CUPS configuration
- **Doesn't print** → Printer/USB issue (check cable, power, driver)

### Printing from LibreOffice
1. Create document with page size 100mm × 60mm (Format → Page Style → Page → Width/Height)
2. File → Print → Select the ZPL-named printer
3. The `rastertolabel` filter converts the rendered page to printer commands

### Pitfalls

- **`lpadmin` may need sudo** unless user is in `lpadmin` group. Check with `groups` first.
- **Driverless auto-detection creates duplicate printers** with generic names. Always clean up after manual addition.
- **Printer may be at a different name than expected.** Canon G2010 may show as "G2010 series" in lsusb but needs a G2000 series driver.
- **Never delete auto-detected printer before confirming** it's a duplicate (compare device URIs with `lpstat -t`).
- **Verification with curl won't work** — printers are managed via CUPS (IPP on localhost:631), not HTTP APIs. Use `lpstat` and `lpq`.
- **If `lpadmin -E` fails**, check that CUPS scheduler is running: `systemctl status cups`.
- **If `lpinfo -m` shows no matching driver**, try `apt search <manufacturer>` for available driver packages.
