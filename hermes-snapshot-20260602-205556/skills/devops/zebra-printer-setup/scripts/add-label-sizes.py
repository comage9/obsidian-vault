#!/usr/bin/env python3
"""Add w283h170 (100x60mm) and w170h283 (60x100mm) to a Zebra ZPL PPD.
Usage: sudo python3 add-label-sizes.py /etc/cups/ppd/Zebra-ZM600.ppd
Then: sudo systemctl restart cups
"""

import sys

def add_sizes(ppd_path):
    with open(ppd_path) as f:
        c = f.read()

    # Add PageSize entries
    insert_ps = (
        "*PageSize w283h170/w283h170: \"<</PageSize[283 170]/ImagingBBox null>>setpagedevice\"\n"
        "*PageSize w170h283/w170h283: \"<</PageSize[170 283]/ImagingBBox null>>setpagedevice\"\n"
    )
    if "w283h170" not in c:
        c = c.replace("*CloseUI: *PageSize", insert_ps + "*CloseUI: *PageSize")

    # Add PageRegion entries
    insert_pr = (
        "*PageRegion w283h170/w283h170: \"<</PageSize[283 170]/ImagingBBox null>>setpagedevice\"\n"
        "*PageRegion w170h283/w170h283: \"<</PageSize[170 283]/ImagingBBox null>>setpagedevice\"\n"
    )
    if "w283h170" not in c.split("*CloseUI: *PageRegion")[0]:
        c = c.replace("*CloseUI: *PageRegion", insert_pr + "*CloseUI: *PageRegion")

    # Add ImageableArea entries
    insert_ia = (
        "*ImageableArea w283h170/w283h170: \"0 0 283 170\"\n"
        "*ImageableArea w170h283/w170h283: \"0 0 170 283\"\n"
    )
    if "w283h170" not in c.split("*CloseUI: *ImageableArea")[0]:
        c = c.replace("*CloseUI: *ImageableArea", insert_ia + "*CloseUI: *ImageableArea")

    # Change defaults to w283h170
    for section in ["PageSize", "PageRegion", "ImageableArea"]:
        c = c.replace(f"*Default{section}: w288h360", f"*Default{section}: w283h170")

    with open(ppd_path, "w") as f:
        f.write(c)

    print(f"Updated: {ppd_path}")
    print("Added: w283h170, w170h283 (PageSize + PageRegion + ImageableArea)")
    print("DefaultPageSize changed: w288h360 -> w283h170")
    print("Run: sudo systemctl restart cups")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: sudo python3 {sys.argv[0]} /etc/cups/ppd/PRINTER-NAME.ppd")
        sys.exit(1)
    add_sizes(sys.argv[1])
