---
name: zpl-label-printer
description: Configure ZPL label printers (Zebra ZM600 etc.) on Ubuntu with CUPS — driver selection, media sizing, rastertolabel filter chain, and USB binding
tags:
  - printer
  - zebra
  - zpl
  - cups
  - label
  - linux
related_skills:
  - spreadsheet-migration
---

# ZPL Label Printer Setup (Ubuntu)

## Quick Setup

```bash
# 1. Add printer with ZPL driver
lpadmin -p PRINTER_NAME \
  -m "drv:///sample.drv/zebra.ppd" \
  -v "usb://Zebra%20Technologies/ZTC%20ZM600-300dpi%20ZPL?serial=SERIAL" \
  -E

# 2. Set label size (e.g., 100mm x 60mm = 283 x 170 points)
lpadmin -p PRINTER_NAME -o media=Custom.283x170

# 3. Print a test (MUST use -o raw — see pitfall below)
echo '^XA^FO50,50^ADN,36,20^FDHELLO^FS^XZ' | lp -d PRINTER_NAME -o raw
```

## Driver Options

| Driver | PPD URI | Use Case |
|--------|---------|----------|
| ZPL | `drv:///sample.drv/zebra.ppd` | Zebra ZPL language printers (ZM600, ZT series) |
| EPL2 | `drv:///sample.drv/zebraep2.ppd` | Zebra EPL language printers (older models) |
| CPCL | `drv:///sample.drv/zebracpl.ppd` | CPCL language printers |
| RAW | `-m raw` | Direct ZPL passthrough, no CUPS conversion |

## Filter Chain

The ZPL PPD has one CUPS filter:
```
*cupsFilter: "application/vnd.cups-raster 50 rastertolabel"
```

This means:
1. Application sends document → CUPS converts to CUPS raster
2. `rastertolabel` converts raster to ZPL bitmap commands (`^GFA`...)
3. Result sent to printer via USB backend

**CRITICAL: When you send raw ZPL text via `lp` WITHOUT `-o raw`, CUPS treats it as text/plain, feeds it through the rasterizer, and `rastertolabel` produces a solid black bitmap (`^GFA` with all-black pixels) covering the entire label area.** The ZPL commands are not recognized — they're rendered as if they were text characters on a page, and the black-on-white text becomes an all-black bitmap at small label sizes.

**For RAW ZPL commands: ALWAYS use `-o raw`** — this bypasses the entire filter chain and sends your ZPL data directly to the printer backend.

For document printing (LibreOffice, PDF), the normal filter chain with `rastertolabel` works correctly — the document is rendered to a proper raster and then converted to ZPL bitmap commands.

## Media Sizing

Label sizes are defined in the PPD as `w{width}h{height}` in PostScript points (1/72 inch):

| Size name | Points | mm | Example |
|-----------|--------|-----|---------|
| w90h18 | 90×18 | 31.75×6.35 | Small tag |
| w142h227 | 142×227 | 50×80 | 80×50mm label |
| w288h360 | 288×360 | 101.6×127 | 4×5 inch |
| Custom.WIDTHxHEIGHT | any | any | Use for custom sizes |

To calculate: `mm ÷ 25.4 × 72 = points`
- 100mm → 100 ÷ 25.4 × 72 = **283** points
- 60mm → 60 ÷ 25.4 × 72 = **170** points
→ `lp -o media=Custom.283x170`

## CUPS Web Interface

Enable and use:
```bash
sudo cupsctl WebInterface=yes
# Open http://localhost:631
```

Navigate to Printers → Select printer → Administration → Set Default Options.

## USB Driver Binding

If the printer is detected by `lsusb` but `/dev/usb/lp*` doesn't appear:

1. Check kernel module:
```bash
lsmod | grep usblp
sudo modprobe usblp   # load if missing
```

2. Bind the device to `usblp`:
```bash
# Find the device sysfs path
find /sys/bus/usb/devices -name manufacturer -exec grep -l Zebra {} \; -exec dirname {} \;

# The path is typically "1-2" or "5-2". Bind:
echo "1-2" > /sys/bus/usb/drivers/usb/unbind 2>/dev/null
echo "1-2" > /sys/bus/usb/drivers/usblp/bind 2>/dev/null
```

3. Verify:
```bash
ls -la /dev/usb/lp*
# Should show crw-rw---- 1 root lp 180, N
```

**NOTE:** If the device still shows `Driver=(none)` in `/sys/kernel/debug/usb/devices`, power-cycle the printer (unplug USB cable, turn printer off/on). The `usblp` driver should auto-bind on reconnection.

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Print job submitted, no output | Wrong driver (EPL2 instead of ZPL) | Change to ZPL driver |
| Printer not in `lsusb` | USB disconnected or kernel driver issue | Power cycle printer |
| `/dev/usb/lp*` missing | `usblp` not loaded or not bound | `sudo modprobe usblp` |
| Job completes instantly, nothing prints | CUPS filter chain produced empty output | Check `rastertolabel` availability |
| "Printer drivers are deprecated" warning | CUPS 2.4+ deprecation | Safe to ignore; still works |
| LibreOffice → label printer prints garbage | Document being sent as PostScript, label printer needs ZPL | Use RAW queue + direct ZPL |
| Printer detected in `lsusb` but jobs never print | Front USB port signal issue | Connect printer to **rear** USB port on motherboard, not front panel ports |
| `Image()` function returns `#NAME?` in LibreOffice Calc | Excel 365 IMAGE function not supported | Replace with `="" & url` or `HYPERLINK()` — see `libreoffice-migration` skill |
| **ZPL text via `lp` prints completely black** | CUPS `rastertolabel` filter converts ZPL text → raster → black bitmap | **Always use `-o raw`** when sending ZPL commands via `lp`. Without `-o raw`, CUPS feeds the ZPL text through its filter chain: text → CUPS raster → `rastertolabel` → black `^GFA` bitmap covering the whole label |
| **Output rotated 90° from LibreOffice** | PPD default PageSize orientation mismatches document orientation | Check `lpoptions -p PRINTER -l \| grep PageSize`: `*w283h170` = landscape default, `*w170h283` = portrait default. LibreOffice sends portrait documents by default; if printer default is landscape, output rotates 90°. Fix: `lpadmin -p PRINTER -o orientation-requested=3` (portrait) or `=4` (landscape). Also set `-o PageSize=w170h283` if portrait labels needed |
| Darkness/PrintRate settings revert after reboot | `lpadmin -o` writes to `~/.lpoptions` but PPD factory defaults may override | Set via CUPS web interface (http://localhost:631 → Printers → Set Default Options) or write into PPD with `sed` on the `*DefaultDarkness` line |
| Duplicate printer appears with suffix like `_comage_A320M_H` | CUPS browsing / Avahi auto-discovers the shared version of a locally-connected printer | Remove the IPP duplicate: `lpadmin -x Canon_G2010_comage_A320M_H`. The USB-direct queue (`Canon-G2010`) is the real one. Same applies if Zebra gets auto-discovered as a network duplicate

## LibreOffice Workflow

1. Create document at exact label size (Format → Page → Width/Height)
2. Print → Select ZPL printer → Properties → Page Size = Custom
3. Printer driver converts via `rastertolabel`

**Known limitation:** The `rastertolabel` filter renders the entire page as a bitmap and sends it as ZPL `^GFA` command. Fonts may appear different from screen rendering.
