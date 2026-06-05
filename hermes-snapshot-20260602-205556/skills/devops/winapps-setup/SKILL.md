---
name: winapps-setup
description: Install and configure WinApps — run Windows applications (Office, Adobe) on Linux via Docker-based Windows VM + FreeRDP integration
category: devops
---

# WinApps Setup — Windows Apps on Linux

Run Windows applications on GNU/Linux with KDE Plasma, GNOME, or XFCE, integrated seamlessly as if they were native.

## When to Load

- User says "WinApps" or "winapps" or "Windows 앱 리눅스에서"
- User wants to run Microsoft Office, Adobe Creative Cloud, or other Windows apps on Linux
- User provides a link to `https://github.com/winapps-org/winapps`

## Architecture

```
Linux Desktop (GNOME/KDE)
    ↕ FreeRDP v3 (RDP protocol)
Docker/Podman container → dockur/windows (QEMU + KVM)
    ↕
Windows VM (11 Pro recommended)
```

WinApps works by:
1. Running Windows in a Docker/Podman/libvirt VM (via `dockur/windows` image)
2. Using FreeRDP to seamlessly render Windows app windows alongside native Linux windows
3. Creating `.desktop` shortcuts, MIME type associations, and Nautilus integration

## Prerequisites

```bash
# KVM support required
egrep -c '(vmx|svm)' /proc/cpuinfo  # must be > 0
ls /dev/kvm                          # must exist

# Docker
sudo apt install -y docker.io docker-compose-v2

# WinApps dependencies
sudo apt install -y curl dialog freerdp3-x11 git iproute2 libnotify-bin netcat-openbsd

# Add user to docker group (requires logout/login to take effect)
sudo usermod -aG docker $USER
```

If Docker group doesn't take effect (newgrp only affects current shell), use `sg docker -c "command"` or `sudo` as fallback.

## Step 1: Clone and Configure

```bash
git clone https://github.com/winapps-org/winapps.git /tmp/winapps
cd /tmp/winapps

# Create config directory
mkdir -p ~/.config/winapps
```

Create `~/.config/winapps/winapps.conf`:

```ini
RDP_USER="comage"
RDP_PASS="comage"
RDP_DOMAIN=""
RDP_IP="127.0.0.1"
RDP_PORT="3389"
OPEN_DEFAULT="yes"
```

## Step 2: Start Windows VM (Docker)

```bash
cd ~/.config/winapps

# Copy compose.yaml and OEM directory
cp /tmp/winapps/compose.yaml .
cp -r /tmp/winapps/oem .

# Customize username/password in compose.yaml
sed -i 's/USERNAME: "MyWindowsUser"/USERNAME: "comage"/' compose.yaml
sed -i 's/PASSWORD: "MyWindowsPassword"/PASSWORD: "comage"/' compose.yaml

# Start the container
sudo docker compose up -d
```

Or use `docker run` directly:

```bash
sudo docker run -d --name WinApps \
  --device /dev/kvm --device /dev/net/tun \
  --cap-add NET_ADMIN \
  -p 127.0.0.1:8006:8006 \
  -p 127.0.0.1:3389:3389/tcp \
  -p 127.0.0.1:3389:3389/udp \
  -v winapps_data:/storage \
  -v /home/comage:/shared \
  -v /tmp/winapps/oem:/oem \
  -e VERSION="11" \
  -e RAM_SIZE="4G" -e CPU_CORES="4" -e DISK_SIZE="64G" \
  -e USERNAME="comage" -e PASSWORD=*** \
  --restart on-failure \
  ghcr.io/dockur/windows:latest
```

### Container Status

```bash
sudo docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
sudo docker logs WinApps
```

## Step 3: Windows Installation

The dockur/windows container automatically:
1. Downloads Windows 11 ISO (~5.6GB) from Microsoft servers
2. Extracts and adds VirtIO drivers
3. Runs unattended installation via `win11x64.xml`
4. Creates user account with configured username/password
5. Enables RDP
6. Runs OEM post-install scripts

**Monitor progress:** Browse to `http://127.0.0.1:8006` (noVNC web interface)

**Installation time:** 15-30 minutes total (download + extraction + setup)

**Log output during installation:**
```
❯ Downloading Windows 11...
  32768K ........ ........ ........ ........  0% 7.77M 19m8s
  ... (100%)
❯ Extracting Windows 11 image...
❯ Adding drivers to image...
❯ Adding OEM folder to image...
❯ Booting Windows using QEMU v10.0.8...
❯ Windows started successfully, visit http://127.0.0.1:8006/
```

When Windows Boot Manager loads from hard disk (`BdsDxe: loading Boot0004 "Windows Boot Manager" from HD(...)`), the installation phase is complete and Windows is booting for OOBE.

## Step 4: Run WinApps Setup

**Wait until RDP authentication works before running setup:**

```bash
# Test RDP connection
xfreerdp3 /v:127.0.0.1:3389 /u:comage /p:comage /cert:ignore +auth-only

# Expected: "Authentication only, exit status 0"
```

**Then run setup:**

```bash
cd /tmp/winapps
# Use sg docker if user isn't in docker group yet
sg docker -c "./setup.sh --user"
```

## RDP Troubleshooting

### Symptom: NLA Logon Failure

```
[ERROR][com.winpr.sspi.Kerberos] krb5_parse_name (Configuration file does not specify default realm)
[ERROR][com.freerdp.core] nla_recv_pdu: ERRCONNECT_LOGON_FAILURE
```

**Root cause:** FreeRDP v3 on Ubuntu has Kerberos configuration issues that prevent NLA (Network Level Authentication). Windows requires NLA by default.

**Solutions (try in order):**

1. **VNC into Windows and disable NLA requirement:**
   - Browse to `http://127.0.0.1:8006`
   - Log into Windows (user/pass from compose.yaml)
   - Settings → System → Remote Desktop → Advanced
   - Uncheck "Require Network Level Authentication"
   - Log out of Windows
   - Retry WinApps setup

2. **Use `/sec:tls` or `/sec:rdp` flags** (only works if Windows NLA requirement is disabled):

### Symptom: Connection Reset

```
BIO_read returned system error 104: Connection reset by peer
```

**Cause:** Windows accepted TCP connection but immediately closed it — typical when Windows is still in OOBE/setup phase.

**Fix:** Wait for installation to complete. Check VNC screen at http://127.0.0.1:8006.

### Symptom: HYBRID_REQUIRED_BY_SERVER

```
HYBRID_REQUIRED_BY_SERVER — Protocol Security Negotiation Failure
```

**Cause:** Windows requires NLA but FreeRDP was configured to use TLS/standard RDP security.

**Fix:** Remove `/sec:tls` or `/sec:rdp` flags from config. Windows NLA requirement must be disabled on Windows side first.

### Symptom: Certificate Change

```
The host key for 127.0.0.1:3389 has changed
Host key verification failed
```

**Cause:** Container restart generated a new RDP certificate.

**Fix:** Remove the old certificate:
```bash
rm ~/.config/freerdp/server/127.0.0.1_3389.pem
```

### Authentication Tests Reference

| Command | Behavior |
|---------|----------|
| `xfreerdp3 /v:127.0.0.1:3389 /u:user /p:pass +auth-only` | Tests initial handshake. May show NLA errors but return exit 0. |
| `xfreerdp3 /sec:rdp /v:... /u:user /p:pass +auth-only` | Forces RDP security (no NLA). Works if Windows allows non-NLA. |
| `xfreerdp3 /v:... /u:user /p:pass -authentication` | Disables auth entirely. "Timeout waiting for activation" = Windows at login screen. |
| Full app launch: `xfreerdp3 /v:... /u:user /p:pass /app:program:"cmd.exe",cmd:"/C echo test > test.txt"` | Requires NLA — fails if Windows requires NLA and FreeRDP NLA is broken. |

## Pitfalls

- **Docker group changes require new login** — `sudo usermod -aG docker $USER` takes effect on next login. For immediate use: `sg docker -c "command"` or use `sudo`.
- **NoVNC does not auto-connect** — The noVNC interface at http://127.0.0.1:8006 requires clicking "Connect" in the browser. The canvas is only populated after connection.
- **Windows 11 Home does NOT support RDP** — RDP (required by WinApps) is only available on Pro, Enterprise, or Server editions.
- **Windows license required** — Without a product key, Windows installs in evaluation mode with limited activation period. Use `VERSION` env var or the automated XML to pass a key.
- **QEMU v10+ required** — dockur/windows uses QEMU v10. If the host kernel is older, performance may suffer. The nested KVM must be enabled.
- **iptables modules needed** — `lsmod | grep ip_tables` and `lsmod | grep iptable_nat` must be non-empty for `+home-drive` (host folder sharing) to work.
- **FreeRDP v3.9+ requires password** — Without a password set, RDP connections may be rejected. Always configure `RDP_PASS` in `winapps.conf`.
- **FreeRDP `+auth-only` exit code is unreliable** — The command may return exit 0 even when NLA authentication fails. Always check the log output for `ERRCONNECT_LOGON_FAILURE`.
- **Container host key changes on restart** — After `docker compose down` + `up`, the RDP certificate changes. Remove the old `.pem` file from `~/.config/freerdp/server/` before reconnecting.
- **dockur/windows password encoding quirk** — The install.sh script appends the literal string `"Password"` to the PASSWORD env value before base64-encoding it for the autounattend.xml. If you set `PASSWORD=*** the actual Windows password becomes `comagePassword`. Try password with and without the `Password` suffix if login fails.
- **Password SED pattern may fail on newer templates** — The SED pattern `|<Password>...........<Value />|` (11 dots) is fragile across template versions. If the pattern doesn't match, password stays empty. **Dx:** `chntpw -u comage /path/to/SAM` to check blank hash.
- **Account lockout recovery** — Too many failed RDP attempts lock the Windows account (`ERRCONNECT_ACCOUNT_LOCKED_OUT`). Recover: `sudo docker restart WinApps` resets the counter.

## Verification

```bash
# Container running
sudo docker ps | grep WinApps

# RDP port open
timeout 3 bash -c 'echo | nc -w 2 127.0.0.1 3389' && echo "RDP open"

# RDP authentication
xfreerdp3 /v:127.0.0.1:3389 /u:comage /p:comage /cert:ignore +auth-only

# WinApps installed
ls ~/.local/bin/winapps 2>/dev/null || echo "Run setup.sh first"

# Check windows app available
winapps list 2>/dev/null || ~/.local/bin/winapps-src/bin/winapps list
```

## References

- GitHub: https://github.com/winapps-org/winapps
- dockur/windows: https://github.com/dockur/windows
- WinApps Launcher widget: https://github.com/winapps-org/WinApps-Launcher
