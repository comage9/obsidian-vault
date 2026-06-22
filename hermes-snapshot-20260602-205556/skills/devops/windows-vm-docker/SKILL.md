---
name: windows-vm-docker
description: Run Windows VM in Docker (dockur/windows) + WinApps integration for Linux desktop. Covers setup, RDP, NLA troubleshooting, password recovery via chntpw.
category: devops
---

# Windows VM in Docker + WinApps

Run Windows applications (Office, Adobe) seamlessly on Linux using Docker-based Windows VM with WinApps integration.

## Prerequisites
- Linux with KVM support (`/dev/kvm` exists, `egrep -c '(vmx|svm)' /proc/cpuinfo` > 0)
- Docker installed and user in `docker` group
- `freerdp3-x11`, `curl`, `dialog`, `git`, `libnotify-bin`, `netcat-openbsd`
- Windows Pro/Enterprise license (RDP required; Home edition does NOT work)

## Quick Start

```bash
# 1. Clone WinApps
git clone https://github.com/winapps-org/winapps.git ~/winapps

# 2. Install dependencies
sudo apt install -y curl dialog freerdp3-x11 git iproute2 libnotify-bin netcat-openbsd

# 3. Configure Windows VM (Docker)
cp ~/winapps/compose.yaml ~/.config/winapps/
# Edit ~/.config/winapps/compose.yaml to set USERNAME, PASSWORD, VERSION etc.

# 4. Start Windows VM
cd ~/.config/winapps && docker compose up -d

# 5. Access VNC at http://127.0.0.1:8006 to monitor installation
# Windows installation takes 15-30 min after ISO download
```

## Config Files

### `~/.config/winapps/winapps.conf`
```
RDP_USER="comage"
RDP_PASS="comage"
RDP_DOMAIN=""
RDP_IP="127.0.0.1"
RDP_PORT="3389"
OPEN_DEFAULT="yes"
```

### `~/.config/winapps/compose.yaml`
Based on [dockur/windows](https://github.com/dockur/windows). Key env vars:
- `VERSION`: "11" (default), "10", "2025" (Server), or a product key
- `USERNAME`, `PASSWORD`: Windows local account
- `RAM_SIZE`, `CPU_CORES`, `DISK_SIZE`: Resource allocation

## Running WinApps Setup

```bash
cd ~/winapps
sg docker -c "./setup.sh --user"
```

## Troubleshooting

### RDP Fails: ERRCONNECT_LOGON_FAILURE / NLA Kerberos Errors

**Symptom:** FreeRDP v3 on Ubuntu fails with:
```
krb5_parse_name (Configuration file does not specify default realm)
nla_recv_pdu: ERRCONNECT_LOGON_FAILURE
```

**Root cause:** FreeRDP v3 prioritizes Kerberos for NLA, and without a realm configuration it falls back to NTLM which may not match Windows credentials.

**Fix options (try in order):**
1. **Disable NLA on Windows** (if VNC accessible):
   - Open http://127.0.0.1:8006 in browser
   - Log into Windows → Settings → System → Remote Desktop → Disable "Network Level Authentication"

2. **If password is unknown/invalid** (dockur/windows XML password encoding bug):
   - Stop container: `docker stop WinApps`
   - Mount disk via qemu-nbd:
     ```bash
     sudo modprobe nbd
     sudo apt install -y qemu-utils chntpw
     sudo qemu-nbd --connect=/dev/nbd0 /var/lib/docker/volumes/winapps_data/_data/data.img
     sudo mount /dev/nbd0p3 /mnt/windows
     ```
   - Clear password: `sudo chntpw -u <username> /mnt/windows/Windows/System32/config/SAM`
     (select option 1 "Clear password", then q, then y)
   - Allow blank RDP password:
     ```bash
     sudo chntpw -e /mnt/windows/Windows/System32/config/SYSTEM
     > cd ControlSet001\Control\Lsa
     > nv 4 LimitBlankPasswordUse 0
     > q
     > y
     ```
   - Inject startup script:
     ```bash
     echo 'net user <username> "<new-password>"' | sudo tee "/mnt/windows/Users/<username>/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/reset_pw.bat"
     ```
   - Cleanup: `sudo umount /mnt/windows && sudo qemu-nbd --disconnect /dev/nbd0`
   - Restart: `docker start WinApps`
   - Login via VNC with blank password; startup script sets new password

3. **Recreate from scratch:**
   ```bash
   docker compose down --rmi=all --volumes
   # Then restart Quick Start steps
   ```

### Docker Permission Denied
```bash
sudo usermod -aG docker $USER
# Logout/login required for group change to take effect
# Workaround for current session: `sg docker -c "command"`
```

### Port Already in Use
```bash
fuser -k 3000/tcp  # or use a different port
```

## Container Lifecycle
```bash
docker compose start   # Power on
docker compose stop    # Graceful shutdown
docker compose pause   # Pause
docker compose unpause # Resume
docker compose kill    # Force shutdown
docker compose down    # Remove container (data preserved in volume)
docker compose down --volumes  # Full cleanup including disk image
```

## Windows Password Encoding (dockur/windows bug)

The install script (`/run/install.sh` inside container) encodes password as:
```bash
pw=$(printf '%s' "${pass}Password" | iconv -f utf-8 -t utf-16le | base64 -w 0)
```

But the sed pattern to insert it into `autounattend.xml` may fail due to whitespace mismatch, leaving the password as `<Value />` (blank). Workaround: always verify password works via VNC first, or use chntpw to set it directly.

## References
- [WinApps GitHub](https://github.com/winapps-org/winapps)
- [dockur/windows GitHub](https://github.com/dockur/windows)
- [FreeRDP v3 NLA Kerberos issues](references/freerdp-nla-kerberos.md)

## USB Passthrough to QEMU VM

To make USB devices (printers, scanners, barcode readers) available **inside** the Windows VM:

### Step 1: Recreate container with USB access

**IMPORTANT:** The container needs `--privileged` for QEMU to access USB host devices. Without this, `-device usb-host` inside `ARGUMENTS` silently fails.

```bash
sudo docker rm -f WinApps
sudo docker run -d --name WinApps \
  --privileged \                       # <-- REQUIRED for USB host passthrough
  --device /dev/kvm \
  --device /dev/net/tun \
  --device /dev/bus/usb \              # <-- grants access to ALL USB devices
  --cap-add NET_ADMIN \
  -p 127.0.0.1:8006:8006 \
  ... (other ports and env vars) \
  -e ARGUMENTS="-usb -device usb-host,vendorid=0xVID,productid=0xPID" \
  ghcr.io/dockur/windows:latest
```

The `vendorid` and `productid` come from `lsusb` output:
```
Bus 001 Device 006: ID 0a5f:0069 Zebra Technologies ZTC ZM600-300dpi ZPL
                                     ^^^^ ^^^^
                               vendorid  productid
```

### Step 2: Install Windows drivers
After the VM boots:
1. Open http://127.0.0.1:8006
2. Log into Windows
3. Device Manager should show the USB device
4. Install manufacturer's Windows driver (e.g. Zebra Setup Utilities for label printers)

### IPP Network Printing (alternative to USB Passthrough)

When USB passthrough fails or you need Linux+Windows **simultaneously**, route through CUPS:

1. Linux CUPS owns the printer via USB (normal CUPS setup, share enabled)
2. Windows VM adds printer as IPP network printer:
   ```
   http://172.17.0.1:631/printers/PRINTER_NAME
   ```
   (Docker gateway `172.17.0.1` = host; verify via `docker network inspect bridge | grep Gateway`)

3. **Prerequisites:**
   ```bash
   sudo cupsctl --share-printers
   ```
   CUPS must be on `0.0.0.0:631` (check: `ss -tlnp | grep 631`)

### VERIFICATION PRINCIPLE (user requirement)
This user explicitly requires **verify-before-reporting** for all hardware/device tasks:
- Never say "it works" or "done" without actual tool output proving it
- If you cannot verify (headless environment, no GUI), say so — don't extrapolate from config files alone
- Print a test page and confirm the physical result, or report the blocker
- Corrections to printer/device configuration are not complete until verified with a real print job

## Name Collision Note

There are two `winapps-setup` entries (one in `devops/`, one referenced in `productivity/libreoffice-migration/references/`). Use the categorized path when loading: `devops/windows-vm-docker` for VM management, or check `devops/winapps-setup` for the WinApps CLI tool setup skill.
