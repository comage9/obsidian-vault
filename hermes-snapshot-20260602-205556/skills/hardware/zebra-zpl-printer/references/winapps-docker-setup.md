# WinApps (dockur/windows) Windows VM Setup

## Quick Start
```bash
docker run -d --name WinApps \
  --device /dev/kvm --device /dev/net/tun --cap-add NET_ADMIN \
  -p 127.0.0.1:8006:8006 -p 127.0.0.1:3389:3389/tcp -p 127.0.0.1:3389:3389/udp \
  -v winapps_data:/storage -v $HOME:/shared \
  -e VERSION="11" -e RAM_SIZE="4G" -e CPU_CORES="4" -e DISK_SIZE="64G" \
  -e USERNAME="comage" -e PASSWORD="yourpassword" \
  --restart on-failure \
  ghcr.io/dockur/windows:latest
```

## Key Parameters
- `USERNAME`/`PASSWORD`: Windows user credentials
- `VERSION`: Windows version ("11", "10", "win11pro", "win10enterprise")
- `DISPLAY`: VNC resolution (e.g., "1920x1080")
- `ARGUMENTS`: Extra QEMU arguments (USB passthrough, etc.)

## Password Issue
The dockur/windows install script appends "Password" to the PASSWORD:
```
pw=$(printf '%s' "${pass}Password" | iconv -f utf-8 -t utf-16le | base64 -w 0)
```
If `PASSWORD=comage`, the actual Windows password becomes `comagePassword`.

## Password Reset (when locked out)
```bash
# Stop container, mount disk
sudo qemu-nbd --connect=/dev/nbd0 /var/lib/docker/volumes/winapps_data/_data/data.img --format=raw
sudo mount /dev/nbd0p3 /mnt/windows
# Clear password
chntpw -u USERNAME /mnt/windows/Windows/System32/config/SAM << EOF
1
q
y
EOF
# Unmount
sudo umount /mnt/windows && sudo qemu-nbd --disconnect /dev/nbd0
# Restart container
```

## RDP Troubleshooting
- NLA (Network Level Authentication) may fail with Kerberos errors
- Fix: Disable NLA in Windows via VNC: `System → Remote Desktop → Require NLA → OFF`
- Or use FreeRDP with `/sec:tls` or `/sec:rdp`
- RDP port: `127.0.0.1:3389`
- VNC web: `http://127.0.0.1:8006`

## Printer Sharing (IPP from Linux CUPS)
Windows VM → Add network printer → IPP → `http://172.17.0.1:631/printers/PRINTER_NAME`
