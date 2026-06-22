# Printer USB Debugging (Linux)

## Symptom: USB Printer Detected but Not Printing

Zebra ZM600-300dpi ZPL label printer case study.

### Diagnostic Flow

1. **Verify USB detection:**
   ```bash
   lsusb | grep -i zebra
   ```
   If the printer doesn't appear in `lsusb`, it's a physical/connection issue — try different USB port (rear ports often work when front ports don't), different cable, or power cycle the printer.

2. **Check kernel driver binding:**
   ```bash
   sudo cat /sys/kernel/debug/usb/devices | grep -A5 "Zebra" | grep Driver
   ```
   Expected: `Driver=usblp`
   If `Driver=(none)`, the `usblp` module isn't bound to the device.

3. **Force-bind to usblp:**
   ```bash
   # Find the correct device path first
   for d in /sys/bus/usb/devices/*/manufacturer; do
       if grep -q "Zebra" "$d" 2>/dev/null; then
           echo "Device: $(dirname $d)"
       fi
   done
   
   # Unbind from generic USB, bind to usblp
   echo "1-2" > /sys/bus/usb/drivers/usb/unbind 2>/dev/null
   sleep 1
   echo "1-2" > /sys/bus/usb/drivers/usblp/bind 2>/dev/null
   ```
   (Replace `1-2` with the actual device path from the `find` command.)

4. **Verify the lp device:**
   ```bash
   ls -la /dev/usb/lp*
   udevadm info -a -n /dev/usb/lp2 | grep KERNEL
   ```

5. **Direct ZPL test (bypasses CUPS):**
   ```bash
   echo '^XA^FO50,50^ADN,36,20^FDHELLO^FS^XZ' > /dev/usb/lp2
   ```
   If this works but CUPS printing doesn't, the issue is CUPS configuration (wrong driver, missing filter).

6. **CUPS USB backend diagnostics:**
   ```bash
   sudo /usr/lib/cups/backend/usb
   ```
   Shows detected printers with device IDs. The ZM600 should report `COMMAND SET:ZPL` and `PROTOCOLS:IEEE1284.4`.

### Common Root Causes

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `lsusb` shows printer but `Driver=(none)` | usblp module not loaded or not bound | `sudo modprobe usblp` + force-bind |
| Direct ZPL write succeeds (exit 0) but nothing prints | Physical USB issue (port, cable) | Try different USB port (rear), different cable |
| CUPS sees printer but jobs disappear silently | Wrong PPD driver (EPL2 instead of ZPL) | Change driver to `drv:///sample.drv/zebra.ppd` (ZPL) |
| `lpinfo -v` doesn't list USB printer | usblp driver claiming the device but CUPS backend can't access it | Check `/dev/usb/lp*` permissions; restart CUPS |
| Printing worked, then stopped after driver changes | USB device path changed (e.g., lp2 → lp3) | Power cycle printer and restart CUPS |
| `ppdFilterLoadPPDFile` error in CUPS log | PPD file corrupted by manual edits | Regenerate: delete PPD, run `lpadmin -m "drv:///sample.drv/zebra.ppd"` |

### CUPS Driver Selection for ZM600

For ZPL label printers, use:
```bash
lpadmin -p PRINTER_NAME -m "drv:///sample.drv/zebra.ppd"
```

Key PPD details:
- `cupsFilter: "application/vnd.cups-raster 50 rastertolabel"` — converts raster to label format
- Supports custom page sizes up to 576x3600 points (8x50 inches)
- Default resolution: 300dpi (also supports 203dpi, 600dpi)

Don't use `-m raw` for regular document printing — RAW mode sends data unmodified and won't convert PDF/PostScript to ZPL. Use RAW only when sending ZPL directly from an application.

### Page Size Configuration

#### Per-Job Custom Size (temporary)

For 100mm x 60mm labels (283pt x 170pt at 72dpi):
```bash
lp -d PRINTER_NAME -o media=Custom.283x170 my_label.pdf
```

Formula: `points = mm / 25.4 * 72`
- 100mm = 100/25.4*72 = 283.46 ≈ 283pt
- 60mm = 60/25.4*72 = 170.08 ≈ 170pt

#### Persistent Custom Size (PPD modification)

To make custom sizes permanently available (shows up in LibreOffice, Chrome, and IPP client print dialogs), add entries to BOTH the `*PageSize` AND `*PageRegion` sections of the PPD file. **Both sections MUST have matching entries** — a size in `*PageSize` but not `*PageRegion` will NOT appear in application print dialogs (especially Chromium-based browsers).

**PPD location:** `/etc/cups/ppd/PRINTER_NAME.ppd`

**Python script to add a custom size:**

```python
import re

ppd_path = "/etc/cups/ppd/Zebra-Technologies-ZTC-ZM600-300dpi-ZPL.ppd"
with open(ppd_path, 'r') as f:
    content = f.read()

new_sizes = [
    ('*PageSize w283h170/100x60mm', '*PageRegion w283h170/100x60mm',
     '"<</PageSize[283 170]/ImagingBBox null>>setpagedevice"'),
    ('*PageSize w170h283/60x100mm', '*PageRegion w170h283/60x100mm',
     '"<</PageSize[170 283]/ImagingBBox null>>setpagedevice"'),
]

for page_size, page_region, dims in new_sizes:
    name = page_size.split()[-1].split('/')[0]
    if name not in content:
        # Insert after last PageSize line
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith(page_size.split()[0]) and name not in line:
                last_ps = i
        lines.insert(last_ps + 1, f'{page_size}: {dims}')
        # Insert after last PageRegion line
        for i, line in enumerate(lines):
            if line.startswith(page_region.split()[0]) and name not in line:
                last_pr = i
        lines.insert(last_pr + 1, f'{page_region}: {dims}')
        content = '\n'.join(lines)

# Update defaults
content = content.replace('*DefaultPageSize: w288h360', '*DefaultPageSize: w283h170')
content = content.replace('*DefaultPageRegion: w288h360', '*DefaultPageRegion: w283h170')

with open(ppd_path, 'w') as f:
    f.write(content)
```

After editing, restart CUPS:
```bash
sudo systemctl restart cups
```

**⚠️ Important PPD rules:**
- Every `*PageSize` entry MUST have a matching `*PageRegion` entry with the same name
- **Every `*PageSize` entry MUST have a matching `*ImageableArea` entry** — without it, LibreOffice and Chromium show the size as "0x0" and applications cannot select it. Format:
  ```
  *ImageableArea w283h170/100x60mm: "0 0 283 170"
  ```
- `*DefaultPageRegion` MUST match `*DefaultPageSize`
- The PPD `*CustomPageSize` section defines min/max bounds: Width 36-576pt, Height 36-3600pt
- Dimension names follow the pattern: `w<WIDTH>h<HEIGHT>` (e.g., `w283h170`)
- Omitting either section → the size won't appear in Chrome/browser print dialogs
- If you regenerate the PPD via `lpadmin -m`, all custom edits are LOST — re-run the script after regeneration

### Dimension verification in lpoptions:
```bash
lpoptions -p PRINTER_NAME -l | grep "PageSize" | tr ' ' '\n' | grep "283\|170"
# Shows: *w283h170  (asterisk = current default)
#         w170h283
```

### Orientation for Label Printers

Label sizes where width > height (e.g., 100mm x 60mm) are often auto-detected as landscape by applications, causing a 90-degree text rotation on the label.

**Fix:** Force portrait orientation:
```bash
lpadmin -p PRINTER_NAME -o orientation-requested=3
```

`orientation-requested=3` = portrait. The default is `0` (auto), which lets the application decide based on page dimensions.

### Darkness and Print Speed Adjustment

For Zebra ZM600 thermal printers, adjust darkness (print head temperature) and speed via CUPS options:

```bash
# Check available range
lpoptions -p PRINTER_NAME -l | grep -E "Darkness|PrintRate"

# Set darkness (1=light, 30=dark; ZM600 default is ~14)
lpadmin -p PRINTER_NAME -o Darkness=10

# Set print speed (1-12 inches per second)
lpadmin -p PRINTER_NAME -o zePrintRate=5
```

**Darkness too high** → ink bleeds, paper burns, characters look smeared or fall apart on the label.
**Darkness too low** → print is too light to scan.

Start at 10 for thermal transfer on 100x60mm labels, adjust up/down by 2-3 steps until quality is acceptable.

### Docker USB Passthrough

When passing USB printers to Docker containers (e.g., Windows VM via dockur/windows):
```bash
docker run --device /dev/bus/usb ...
```
This makes ALL USB devices visible to the QEMU VM. After power-cycling the printer, restart the container to re-detect the USB device.

### QEMU USB Passthrough Troubleshooting

When QEMU reports `libusb_release_interface: -4 [NO_DEVICE]`:
1. Check that `usblp` is not bound to the device: `ls -la /dev/usb/lp*` should be empty
2. Verify the device path hasn't changed after power-cycle (use `for d in /sys/bus/usb/devices/*/product; do grep -l Zebra $d; done` to find current path)
3. Use `--privileged` flag for the Docker container (needed for libusb access inside the container)
4. Prefer `hostbus=X,hostaddr=Y` addressing over `vendorid,productid` for stability:
   ```
   ARGUMENTS="-device usb-host,hostbus=1,hostaddr=8 -device usb-host,hostbus=5,hostaddr=7"
   ```
5. But for simultaneous access by both Linux and Windows, use CUPS IPP sharing instead (see `cups-ipp-docker.md`)
