#!/usr/bin/env python3
"""
Convert an image (PNG/JPEG) to ZPL ^GFA (Graphic Field ASCII Hex) commands
and send to a Zebra ZPL printer via CUPS raw queue.

Usage:
    python3 image-to-zpl.py <image_path> [darkness] [printer_name]

    darkness: default 15 (00-30)
    printer_name: default 'Zebra-ZM600'

DPI notes:
    - ZM600-300dpi: 100x60mm = 1181x709 px at 300dpi
    - ZM600-203dpi: 100x60mm =  799x480 px at 203dpi
    - Resize the image to the correct pixel dimensions BEFORE running this script
    - The printer renders ^GFA at 1 pixel = 1 dot (native resolution)
    - To convert PDF to correct size first, use Ghostscript (see zebra-printer-setup skill)
"""

import sys
import subprocess
from PIL import Image


def image_to_zpl(image_path, darkness=15, threshold=128):
    """Convert image to ZPL ^GFA commands."""
    img = Image.open(image_path).convert('L')  # grayscale

    width, height = img.size

    # Convert to 1-bit (black/white) using threshold
    bw = img.point(lambda x: 0 if x < threshold else 255, '1')

    # Get packed bytes: PIL '1' mode uses 0=black, 255=white
    # ZPL uses 1=black, 0=white — MUST invert bits
    raw_bytes = bw.tobytes()
    inverted = bytes(b ^ 0xFF for b in raw_bytes)

    bytes_per_row = (width + 7) // 8
    total_bytes = bytes_per_row * height

    # Convert to ASCII hex, split into lines for printer compatibility
    hex_full = inverted[:total_bytes].hex().upper()
    lines = [hex_full[i:i+100] for i in range(0, len(hex_full), 100)]

    # Build ZPL
    # ^GFA: a=format(A=ASCII hex), b=total bytes, c=total bytes, d=bytes per row
    zpl = '^XA\n'
    zpl += f'~SD{darkness}\n'  # set darkness
    zpl += '^FO0,0\n'  # field origin at top-left
    zpl += f'^GFA,{total_bytes},{total_bytes},{bytes_per_row},'
    zpl += '\n'.join(lines) + '\n'
    zpl += '^XZ\n'

    return zpl


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <image_path> [darkness=15] [printer=Zebra-ZM600]")
        print(f"\nExample: {sys.argv[0]} label.png 15")
        print(f"\nTips:")
        print("  - Image should be pre-sized to printer's native DPI:")
        print("    300dpi: 100x60mm = 1181x709 px")
        print("    203dpi: 100x60mm =  799x480 px")
        print("  - For PDF, convert first with Ghostscript:")
        print("    gs -r300 -dFIXEDMEDIA -dPDFFitPage \\")
        print("      -dDEVICEWIDTHPOINTS=283 -dDEVICEHEIGHTPOINTS=170 \\")
        print("      -sDEVICE=png16m -sOutputFile=label.png input.pdf")
        sys.exit(1)

    image_path = sys.argv[1]
    darkness = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    printer = sys.argv[3] if len(sys.argv) > 3 else 'Zebra-ZM600'

    zpl = image_to_zpl(image_path, darkness)

    # Send to printer via raw queue (bypasses all CUPS filters)
    result = subprocess.run(
        ['lp', '-d', printer, '-o', 'raw'],
        input=zpl,
        capture_output=True,
        text=True
    )

    print(result.stdout.strip())
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    img = Image.open(image_path)
    print(f"Sent {len(zpl):,} bytes ZPL | image: {img.size[0]}x{img.size[1]} px | darkness: {darkness}")
