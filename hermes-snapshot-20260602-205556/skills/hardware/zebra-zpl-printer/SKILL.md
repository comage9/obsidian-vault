---
name: zebra-zpl-printer
description: Zebra ZPL label printer setup on Linux CUPS — driver selection, USB troubleshooting, custom paper sizes, network sharing (IPP), QEMU Windows VM passthrough
category: hardware
---

# Zebra ZPL Printer (Linux + Windows VM)

Set up Zebra ZPL label printers (ZM600, ZM400, GK420, etc.) on Linux CUPS and share with Docker Windows VM.

## Driver Selection

| Type | Command | Use Case |
|------|---------|----------|
| **ZPL Driver** | `lpadmin -p PRINTER -m "drv:///sample.drv/zebra.ppd"` | Printing from LibreOffice/regular apps (uses rastertolabel filter) |
| **RAW Queue** | `lpadmin -p PRINTER -m raw` | Direct ZPL passthrough (custom apps that generate ZPL) |
| **EPL Driver** | `drv:///sample.drv/zebraep2.ppd` | Avoid — EPL ≠ ZPL; ZM600 uses ZPL |

**Always use ZPL driver for Zebra ZM600.** EPL2 driver sends wrong printer language.

## USB Troubleshooting

### Port Selection
- **Use rear USB ports** — front panel ports may show signal issues (printer detected but won't print)
- Verify: `lsusb | grep Zebra`

### Kernel Driver Conflict
QEMU (Docker Windows VM) and usblp cannot share the same USB printer simultaneously.

**Fix when QEMU can't access printer (NO_DEVICE):**
```bash
# Find USB path
for d in /sys/bus/usb/devices/*/product; do
    grep -q "Zebra\|ZM600" "$d" 2>/dev/null && echo "$(dirname $d | xargs basename)"
done
# Unbind from usblp
echo "1-5" > /sys/bus/usb/drivers/usblp/unbind 2>/dev/null
```

**Fix when CUPS can't access printer (usblp status: check with `ls /dev/usb/lp*`):**
Stop the Docker container, which releases the USB device:
```bash
sudo docker stop WinApps
# CUPS can now access the printer directly
```

### Simultaneous Linux + Windows VM Access
USB can only be used by ONE system at a time. Solution: **IPP Network Sharing**

1. Linux CUPS owns the USB printer
2. Windows VM connects via IPP:
   ```
   http://172.17.0.1:631/printers/PRINTER_NAME
   ```
3. Docker gateway IP: `172.17.0.1` (check with `docker network inspect bridge`)

### QEMU USB Passthrough (when needed)
```bash
docker run ... \
  --device /dev/bus/usb \
  --privileged \
  -e ARGUMENTS="-device usb-host,hostbus=1,hostaddr=8" \
  ...
```
Use `hostbus,hostaddr` (not `vendorid,productid`) for more reliable detection. Note: USB addresses change on reconnect.

## Custom Paper Size (100x60mm)

1 point = 1/72 inch. 100mm = 283pt, 60mm = 170pt.

### Add to PPD (persistent)
Edit `/etc/cups/ppd/PRINTER.ppd`:
```
*PageSize w283h170/100x60mm: "<</PageSize[283 170]/ImagingBBox null>>setpagedevice"
*DefaultPageSize: w283h170
```

### Via lpadmin (per-job)
```bash
lp -d PRINTER -o media=Custom.283x170 file.pdf
```

### PPD CRITICAL: Must include ImageableArea
Adding `*PageSize` alone causes LibreOffice to show **"0x0"** — the entry is invisible.
**ALL THREE** entries are required for a working custom page size:
```
*PageSize w283h170/100x60mm: "<</PageSize[283 170]/ImagingBBox null>>setpagedevice"
*PageRegion w283h170/100x60mm: "<</PageSize[283 170]/ImagingBBox null>>setpagedevice"
*DefaultPageRegion: w283h170
*ImageableArea w283h170/100x60mm: "0 0 283 170"
```
Missing `*ImageableArea` → LibreOffice shows "0x0".
Missing `*PageRegion` → Chromium/GTK apps can't see the size.
Mismatched `*DefaultPageRegion` vs `*DefaultPageSize` → unpredictable defaults.

### Media Tracking (label feed type)
| Setting | Label type |
|---------|-----------|
| `Web` | Die-cut labels with gaps (most common) |
| `Continuous` | No gaps, continuous roll |
| `Mark` | Black mark on back of label |
```bash
lpadmin -p PRINTER -o zeMediaTracking=Web
```

### Scale Prevention
`fitplot=true` (default with some drivers) scales content to fit the page size, distorting label output. **Always disable:**
```bash
lpadmin -p PRINTER -o fitplot=false
```

### VERIFY BEFORE REPORTING
**This user requires physical verification. Never say "done" or "added" without confirming:**
1. `lpoptions -p PRINTER -l | grep PageSize` — shows size in CUPS?
2. Open a real application (LibreOffice Writer) → Print dialog → Page Size dropdown — see the custom size?
3. If you can't verify in the GUI (headless), SAY SO. Don't claim it works based on PPD content alone.
4. Print a test label — does it actually come out right size?

### Warning
`lpadmin -m "drv:///..."` regenerates the PPD from scratch, **overwriting** all custom page sizes, ImageableArea, and PageRegion entries. Re-apply ALL THREE after any driver change.

## Printer Sharing Checklist

1. `sudo cupsctl --share-printers`
2. CUPS listening on `0.0.0.0:631` (check: `ss -tlnp | grep 631`)
3. Docker container can reach host at `172.17.0.1` (or default gateway)
4. Windows VM add printer → IPP → `http://172.17.0.1:631/printers/NAME`

## Windows VM Notes (dockur/windows)
- Default password encoding bug: compose.yaml password has "Password" appended internally
- Use `chntpw` on SAM hive if password doesn't work
- SAM path: `Windows/System32/config/SAM` on mounted image
```bash
# Clear password
chntpw -u USERNAME /path/to/SAM << EOF
1
q
y
EOF
```
