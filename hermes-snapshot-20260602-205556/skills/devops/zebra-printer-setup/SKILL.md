---
name: zebra-printer-setup
description: Set up Zebra ZPL label printers (ZM600, etc.) on Linux — CUPS driver configuration, RAW vs ZPL mode, USB troubleshooting, and QEMU passthrough for Windows VMs
category: devops
---

# Zebra ZPL Label Printer Setup (Linux)

Set up Zebra ZM600-series and other ZPL label printers on Ubuntu/Debian for use from LibreOffice, Windows VM, or direct ZPL commands.

## Printer Model Detection

Use `lsusb` to identify the printer:
```
Bus 001 Device 008: ID 0a5f:0069 Zebra Technologies ZTC ZM600-300dpi ZPL
```

**CRITICAL: The model name contains the DPI!** `ZM600-300dpi` = 300 DPI print head.
DO NOT assume 203dpi. The ZM600 comes in 203dpi and 300dpi variants.
All pixel-to-mm calculations must use the printer's native DPI:
- 300dpi: 100×60mm = 1181×709 dots, 1 inch = 300 dots
- 203dpi: 100×60mm = 799×480 dots, 1 inch = 203 dots

The USB backend also reports device capabilities:
```bash
sudo /usr/lib/cups/backend/usb
# Look for: COMMAND SET:ZPL, PROTOCOLS:IEEE1284.4
# And MODEL:ZTC ZM600-300dpi ZPL ← DPI is HERE
```

## CUPS Driver Setup

### Required Packages
```bash
sudo apt install -y cups cups-filters printer-driver-gutenprint
sudo cupsctl WebInterface=yes
```

### Available Drivers
| Driver | PPD URI | Notes |
|--------|---------|-------|
| Zebra ZPL | `drv:///sample.drv/zebra.ppd` | Has `rastertolabel` CUPS filter | 
| Zebra EPL2 | `drv:///sample.drv/zebraep2.ppd` | Older language, NOT for ZM600 |
| RAW (no driver) | `raw` | Direct ZPL passthrough only |

### Recommended: ZPL Driver with rastertolabel

```bash
lpadmin -p Zebra-ZM600 -v "usb://Zebra%20Technologies/ZTC%20ZM600-300dpi%20ZPL?serial=JAY409796" \
  -m "drv:///sample.drv/zebra.ppd" -E
```

The `rastertolabel` CUPS filter converts PDF/PostScript documents to raster (bitmap) and then to ZPL commands. This enables direct printing from LibreOffice Writer with correct label dimensions.

### Alternative: RAW Queue (for direct ZPL only)

```bash
lpadmin -p Zebra-ZM600-RAW -v "usb://..." -m raw -E
```

RAW queues are deprecated in CUPS 2.4.7+ but still functional.

## Label Size Configuration

### Step 1: Install printer with ZPL driver

```bash
sudo lpadmin -p Zebra-ZM600 \
  -v "usb://Zebra%20Technologies/ZTC%20ZM600-300dpi%20ZPL?serial=JAY409796" \
  -m "drv:///sample.drv/zebra.ppd" \
  -E
# NOTE: lpadmin -m shows deprecation warning in CUPS 2.4.x — it still works.
```

### Step 2: Add custom label sizes to the generated PPD

The ZPL driver PPD does NOT include w283h170 (100x60mm) or w170h283 (60x100mm).
These MUST be added to `/etc/cups/ppd/Zebra-ZM600.ppd` with PageSize, PageRegion,
AND ImageableArea entries. Also update DefaultPageSize/DefaultPageRegion/DefaultImageableArea.

Use the script: `scripts/add-label-sizes.py` (see references). Or inline Python:

```bash
sudo python3 -c "
ppd = '/etc/cups/ppd/Zebra-ZM600.ppd'
with open(ppd) as f: c = f.read()
# Insert before *CloseUI: *PageSize
c = c.replace('*CloseUI: *PageSize',
  '*PageSize w283h170/w283h170: \"<</PageSize[283 170]/ImagingBBox null>>setpagedevice\"\n'
  '*PageSize w170h283/w170h283: \"<</PageSize[170 283]/ImagingBBox null>>setpagedevice\"\n'
  '*CloseUI: *PageSize')
# Same for PageRegion and ImageableArea
c = c.replace('*CloseUI: *PageRegion',
  '*PageRegion w283h170/w283h170: \"<</PageSize[283 170]/ImagingBBox null>>setpagedevice\"\n'
  '*PageRegion w170h283/w170h283: \"<</PageSize[170 283]/ImagingBBox null>>setpagedevice\"\n'
  '*CloseUI: *PageRegion')
c = c.replace('*CloseUI: *ImageableArea',
  '*ImageableArea w283h170/w283h170: \"0 0 283 170\"\n'
  '*ImageableArea w170h283/w170h283: \"0 0 170 283\"\n'
  '*CloseUI: *ImageableArea')
# Change defaults
c = c.replace('*DefaultPageSize: w288h360', '*DefaultPageSize: w283h170')
c = c.replace('*DefaultPageRegion: w288h360', '*DefaultPageRegion: w283h170')
c = c.replace('*DefaultImageableArea: w288h360', '*DefaultImageableArea: w283h170')
with open(ppd,'w') as f: f.write(c)
"
sudo systemctl restart cups
```

### Step 3: Set user-level defaults (after PPD edit + CUPS restart)

```bash
# lpadmin -o may only set PPD defaults — use lpoptions for user-level persistence
lpoptions -p Zebra-ZM600 -o PageSize=w283h170 \
  -o orientation-requested=3 -o fitplot=false -o Darkness=15

# Verify
lpoptions -p Zebra-ZM600
```

Available sizes after PPD customization:
- `w283h170` = 100mm x 60mm (landscape label)
- `w170h283` = 60mm x 100mm (portrait label)
- `w288h360` = 4x5 inch (original default)
- `Custom.WIDTHxHEIGHT` = arbitrary (WIDTH, HEIGHT in PostScript points)

### Printing from LibreOffice Writer

1. Format → Page Style → Page → Width=100mm, Height=60mm
2. Design the label layout
3. File → Print → Select Zebra-ZM600 → Properties → Paper: w283h170
4. If content is rotated 90°, check `orientation-requested` setting (3=portrait/no-rotate)

## Printing PDF/Images on Label Stock (ZPL ^GFA Direct Method)

The CUPS `rastertolabel` filter is broken on cups-filters 2.0.0+ (Ubuntu 24.04).
**Use the image-to-ZPL direct method instead** — convert PDF/images to ZPL ^GFA
graphic commands and send via `lp -o raw`. This bypasses the entire CUPS filter chain.

### Quick workflow:

```bash
# 1. Convert PDF to label-sized PNG (use printer's native DPI!)
# For 300dpi ZM600: 100x60mm = 1181x709 px
gs -dNOPAUSE -dBATCH -sDEVICE=png16m -r300 \
  -dFIXEDMEDIA -dPDFFitPage \
  -dDEVICEWIDTHPOINTS=283 -dDEVICEHEIGHTPOINTS=170 \
  -sOutputFile=/tmp/label.png input.pdf

# For 203dpi ZM600: 100x60mm = 799x480 px
gs -dNOPAUSE -dBATCH -sDEVICE=png16m -r203 \
  -dFIXEDMEDIA -dPDFFitPage \
  -dDEVICEWIDTHPOINTS=283 -dDEVICEHEIGHTPOINTS=170 \
  -sOutputFile=/tmp/label.png input.pdf

# 2. Convert to ZPL and print
python3 scripts/image-to-zpl.py /tmp/label.png 15
```

The script (see `scripts/image-to-zpl.py`):
- Converts image to 1-bit monochrome with threshold 128
- Inverts bits (PIL uses 0=black, ZPL uses 1=black)
- Generates `^GFA` hex data split across lines for printer compatibility
- Sends via `lp -d Zebra-ZM600 -o raw` (bypasses all CUPS filters)
- Darkness (`~SDxx`) is embedded in the ZPL, not dependent on CUPS settings

### Key parameters:
- `-dFIXEDMEDIA` — forces Ghostscript to use the specified media size
- `-dPDFFitPage` — scales PDF content to fit the specified media
- `-r300` or `-r203` — MUST match printer's native DPI (check model: ZM600-300dpi vs ZM600-203dpi)
- `-dDEVICEWIDTHPOINTS=283 -dDEVICEHEIGHTPOINTS=170` — 100×60mm in PostScript points (same regardless of DPI, Ghostscript handles DPI separately via -r)

### Image size reference (for ^GFA pixel-perfect rendering):

| Label | 300dpi (dots) | 203dpi (dots) |
|-------|---------------|---------------|
| 100×60mm | 1181×709 | 799×480 |
| 60×100mm | 709×1181 | 480×799 |
| 1 inch² | 300×300 | 203×203 |

## USB Troubleshooting

### Driver Binding Issues

The `usblp` kernel driver can conflict with QEMU USB passthrough. Check binding:

```bash
# Check if usblp claimed the printer
cat /sys/kernel/debug/usb/devices | grep -A5 "Zebra" | grep "Driver"
# Expected: Driver=usblp (for Linux CUPS) or Driver=usbfs (for QEMU passthrough)

# Find the USB device path
for d in /sys/bus/usb/devices/*/product; do
    grep -q "Zebra" "$d" && echo "$(dirname $d | xargs basename)"
done

# Unbind from usblp (before starting QEMU)
echo "1-5" > /sys/bus/usb/drivers/usblp/unbind
```

### Rear USB Port Recommendation

If a Zebra printer is detected by `lsusb` and `lpinfo -v` but **does not print** even via direct ZPL to `/dev/usb/lp*`:
- The USB cable may have signal integrity issues on front/hub ports
- **Move the printer to a rear motherboard USB port** (directly on the motherboard, not via front-panel headers)
- Power-cycle the printer after changing ports
- The ZM600 uses USB 1.1 full-speed (12Mbps) which is more susceptible to signal issues on long front-panel cable runs

### Printer Not Responding to ZPL

```bash
# Send raw ZPL test (MUST use -o raw to bypass rastertolabel filter)
echo '^XA^FO50,50^ADN,36,20^FDHELLO^FS^XZ' | lp -d Zebra-ZM600 -o raw

# If no output: possible USB signal issue (try different port)
# If device not found: check usblp binding
```

## Pitfalls

### CRITICAL: rastertolabel broken on cups-filters 2.0.0 (Ubuntu 24.04+)

On systems with **cups-filters ≥ 2.0.0** (Ubuntu 24.04 Noble+), the `rastertolabel`
filter fails with:

```
E [Job NNN] ppdFilterLoadPPD: Unable to generate CUPS Raster sample header.
```

**Cause:** cups-filters 2.x uses `libppd2` for PPD parsing. The generated PPD from
`drv:///sample.drv/zebra.ppd` lacks standalone `*cupsBitsPerColor`, `*cupsColorOrder`,
`*cupsColorSpace` top-level entries. The Resolution stanzas embed these in PostScript
setpagedevice code, but `libppd2` requires them as top-level PPD keywords.

Even adding these entries directly to the PPD does not fix the issue permanently
because CUPS regenerates PPDs from the driver template on restart/reinstall.

**Symptom:** All PDF/image prints through CUPS filter chain produce solid black
or blank output. ZPL direct commands via `-o raw` still work correctly.

**Workaround: Convert documents to ZPL ^GFA commands and send via raw queue.**
See `scripts/image-to-zpl.py` for a Python script that converts any image
(PNG/JPEG/PDF via Ghostscript) to ZPL ^GFA graphic field commands and sends
via `lp -o raw`.

Key implementation detail: PIL '1' mode uses 0=black, but ZPL uses 1=black.
Bits MUST be inverted (XOR with 0xFF) before hex-encoding for ^GFA.

```bash
# Convert PDF to label-sized image first, then to ZPL
gs -dNOPAUSE -dBATCH -sDEVICE=png16m -r203 \
  -dFIXEDMEDIA -dPDFFitPage \
  -dDEVICEWIDTHPOINTS=283 -dDEVICEHEIGHTPOINTS=170 \
  -sOutputFile=/tmp/label.png input.pdf

python3 scripts/image-to-zpl.py /tmp/label.png 15
```

### rastertolabel black output without -o raw

When sending ZPL commands via `echo '^XA...' | lp`, the `rastertolabel` CUPS filter
converts the text stream into a raster bitmap — the entire label becomes solid black.
**Always use `-o raw` when sending ZPL commands directly.** Omit `-o raw` only when
printing from applications (LibreOffice, Chrome) that produce PDF/PostScript.

### CUPS Darkness/options ignored in raw mode

When `-o raw` is used, CUPS bypasses ALL filters including Darkness, PrintRate, and
orientation settings. The ZPL command itself must include darkness (`~SDxx`) and
other printer settings:

```bash
# WRONG — Darkness=15 ignored, prints at printer's saved default
echo '^XA^FO50,50^ADN,36,20^FDTEST^FS^XZ' | lp -d Zebra-ZM600 -o raw

# CORRECT — darkness embedded in ZPL
echo '^XA~SD15^FO50,50^ADN,36,20^FDTEST^FS^XZ' | lp -d Zebra-ZM600 -o raw
```

ZPL darkness command: `~SDxx` where xx is 00–30. The printer saves this value
to NVRAM and uses it for subsequent non-raw (CUPS-filtered) jobs as well.
After changing darkness via raw ZPL, update the CUPS option to match:
```bash
lpoptions -p Zebra-ZM600 -o Darkness=15
```

### CUPS browsing creates IPP duplicate printers

When `cupsctl --share-printers` is enabled and the Avahi daemon is running, CUPS
auto-discovers its own shared printers and creates IPP duplicates with names like
`Zebra_Technologies_ZTC_ZM600_300dpi_ZPL_comage_HOSTNAME`. These duplicates:

- Use auto-generated IPP Everywhere PPDs (cannot be modified — regenerated on restart)
- Lack Darkness/PrintRate/orientation controls
- Lack custom label sizes (w283h170, w170h283)
- Cause LibreOffice to send jobs to the wrong printer

**Remove IPP duplicates:**
```bash
lpstat -p | grep -i zebra  # check for duplicates
sudo lpadmin -x Zebra_Technologies_ZTC_ZM600_300dpi_ZPL_comage_HOSTNAME
```

Prevent creation by disabling CUPS browsing:
```bash
sudo cupsctl --no-browse-remote-printers
# or disable Avahi: sudo systemctl stop avahi-daemon
```

### lpadmin -o vs lpoptions

Options set during `lpadmin -o` may set PPD defaults but NOT user-level defaults.
After `lpadmin`, always verify with `lpoptions -p NAME` and set missing options:
```bash
lpoptions -p Zebra-ZM600 -o Darkness=15 -o PageSize=w283h170 -o orientation-requested=3
```

### PPD regenerated on reinstall

When reinstalling a printer with `lpadmin -m drv:///sample.drv/zebra.ppd`, CUPS
generates a fresh PPD from the driver template. Any custom sizes (w283h170, etc.)
added to the old PPD are lost. Reapply PPD customizations after every reinstall.

## Complete Reinstall Procedure

When the printer state is corrupted, remove everything and start fresh:

```bash
# 1. Remove printer
sudo lpadmin -x OLD-PRINTER-NAME

# 2. Remove any IPP duplicates
for p in $(lpstat -a 2>/dev/null | grep -i zebra | cut -d' ' -f1); do
    sudo lpadmin -x "$p"
done

# 3. Verify USB detection
sudo /usr/lib/cups/backend/usb 2>&1 | grep -i zebra
# Expected: direct usb://Zebra%20Technologies/... "Zebra Technologies ZTC ZM600..."

# 4. Install fresh
sudo lpadmin -p Zebra-ZM600 \
  -v "usb://Zebra%20Technologies/ZTC%20ZM600-300dpi%20ZPL?serial=SERIAL" \
  -m "drv:///sample.drv/zebra.ppd" -E

# 5. Customize PPD (add w283h170, w170h283 — see Label Size Configuration Step 2)
# 6. Set user options (see Step 3)
# 7. Restart CUPS and test
sudo systemctl restart cups
echo '^XA^FO50,50^ADN,36,20^FDTEST^FS^XZ' | lp -d Zebra-ZM600 -o raw
```

## Dual Access: Linux Mint + Windows VM Simultaneously

USB printers can only be claimed by **one** system at a time. When QEMU has USB passthrough, Linux CUPS can't access the printer, and vice versa.

### Solution: Linux CUPS network sharing + Windows IPP client

```bash
# 1. Remove USB passthrough from Docker container (no --device /dev/bus/usb, no ARGUMENTS)
# 2. Let CUPS claim the printer on Linux
sudo docker rm -f WinApps
sudo docker run -d --name WinApps ... # WITHOUT --device /dev/bus/usb and ARGUMENTS
```

Then enable CUPS sharing:
```bash
sudo cupsctl --share-printers
# CUPS is already listening on 0.0.0.0:631
```

**From Windows VM:**
1. Control Panel → Devices and Printers → Add Printer
2. "The printer that I want isn't listed"
3. "Select a shared printer by name"
4. Enter: `http://172.17.0.1:631/printers/Zebra-ZM600`
   (172.17.0.1 = Docker gateway = Linux host)
5. Install Windows driver when prompted

This works because the Docker container can reach the host via the Docker bridge gateway.
Both Linux and Windows can print simultaneously.

## QEMU USB Passthrough (for Windows VM direct access)

If network sharing is not desired and the printer should be accessible **only** in the Windows VM, use QEMU USB passthrough via dockur/windows:

```bash
# Find current USB addresses
lsusb | grep Zebra  # e.g. Bus 001 Device 008
lsusb | grep Canon  # e.g. Bus 005 Device 007

docker run -d --name WinApps \
  --device /dev/bus/usb \
  --privileged \
  -e ARGUMENTS="-device usb-host,hostbus=1,hostaddr=8 -device usb-host,hostbus=5,hostaddr=7" \
  ...
```

**Critical:** Unbind printers from `usblp` BEFORE starting the container, or QEMU will report `libusb_release_interface: -4 [NO_DEVICE]`.

**Note:** USB addresses (`hostaddr=8`) may change after power-cycling the printer. Use `vendorid=0x0a5f,productid=0x0069` for persistent identification, but this may still fail if `usblp` claims the device first.

## References

- ZPL Programming Guide: `references/zpl-quick-ref.md`
- PPD custom label script: `scripts/add-label-sizes.py`
- dockur/windows USB configuration: https://github.com/dockur/windows
