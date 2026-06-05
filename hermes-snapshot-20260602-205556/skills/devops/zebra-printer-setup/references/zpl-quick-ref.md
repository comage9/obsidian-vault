# ZPL Quick Reference (Zebra Programming Language)

## Common Commands

| Command | Description | Example |
|---------|-------------|---------|
| `^XA` | Start label format | `^XA...^XZ` |
| `^XZ` | End label format | `^XA...^XZ` |
| `^FO` | Field origin (x,y) in dots | `^FO50,50` |
| `^AD` | Font (A=scalable, D=font 1) | `^ADN,36,20` |
| `^FD` | Field data (text to print) | `^FDHello World^FS` |
| `^FS` | Field separator (end field) | After every ^FD |
| `^BY` | Bar code field defaults | `^BY2,3,150` |
| `^BXN` | Code 128 bar code | `^BXN,10,200` |
| `^XZ` | Print one label | End of format |
| `^PQ` | Print quantity | `^PQ2` prints 2 copies |
| `^LH` | Label home (origin offset) | `^LH0,0` |
| `^LL` | Label length (dots) | `^LL812` |
| `^LS` | Label shift (vertical) | `^LS0` |
| `^MU` | Set units (dots/mm) | `^MUd2` |
| `^MC` | Mirror image | `^MCY` |
| `^PO` | Print orientation | `^POI` (inverted) |
| `^FW` | Field rotation | `^FWR` (90deg) |
| `^CI` | Character encoding | `^CI28` (UTF-8) |
| `^HH` | Host status request | Returns printer config |

## Resolution Conversion

ZM600-300dpi: 300 dots per inch = 12 dots per mm

```
dots = mm × 11.8  (for 300dpi)
dots = mm × 8     (for 203dpi)

100mm × 60mm at 300dpi = 1180 × 708 dots
```

## Test Label

```
^XA
^FO50,50^ADN,36,20^FDHELLO WORLD^FS
^XZ
```

## Printer Setup Commands\n\n| Command | Description | Example |\n|---------|-------------|---------|\n| `~SD` | Set Darkness (00–30) | `~SD15` |\n| `~JR` | Reset printer | `~JR` |\n| `~JB` | Reboot printer | `~JB` |\n| `^MP` | Print Mode (T=Tear, P=Peel, R=Rewind) | `^MPT` |\n| `^PR` | Print Rate (1–12 ips) | `^PR3` |\n| `^MN` | Media Tracking (N=Continuous, W=Web, M=Mark) | `^MNW` |\n\n**Important:** Setup commands (`~SD`, `^MP`, `^PR`, `^MN`) save to printer NVRAM.\nWhen using `-o raw` with `lp`, CUPS Darkness/PrintRate options are IGNORED —\ninclude `~SDxx` inside the ZPL data itself.

## Status

```
^XA^HH^XZ  (request printer config/status response)
```
