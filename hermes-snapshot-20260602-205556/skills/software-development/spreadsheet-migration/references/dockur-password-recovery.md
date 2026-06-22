# Dockur/Windows Password Encoding and SAM Recovery

## The Password Encoding Bug

Dockur/windows sets the Windows user password via `install.sh`, which modifies an `autounattend.xml` template with `sed`. The encoding has two issues:

### Bug 1: "Password" Suffix

The script appends the literal string "Password" to whatever password value you provide:

```bash
pass="$PASSWORD"  # e.g., "comage"
pw=$(printf '%s' "${pass}Password" | iconv -f utf-8 -t utf-16le | base64 -w 0)
# pw = base64(UTF16LE("comagePassword"))
```

The resulting Windows password becomes `{PASSWORD_VALUE}Password` — e.g., `comagePassword`, not `comage`.

### Bug 2: sed Pattern Mismatch

The sed that inserts the password into autounattend.xml uses a fixed 11-dot pattern:

```bash
sed -i -z "s|<Password>...........<Value \\/>|<Password>\\n          <Value>$pw<\\/Value>|g" "$asset"
```

But the actual XML template has this format:
```xml
<Password>\n              <Value />
              <PlainText>true</PlainText>
```

The 11 dots don't match the actual whitespace (1 newline + 14 spaces = 15 chars), so the sed silently fails. The password remains `<Value />` (empty), and the user must log in with an empty password.

### Workaround

When `PASSWORD` is set and the account is created but login fails with the expected password:
1. Try `{password}Password` (e.g., for `PASSWORD=comage`, try `comagePassword`)
2. Try empty password (the fallback when the sed fails)
3. If both fail, use chntpw to clear/reset the password (see SAM Recovery below)

## SAM Registry Password Recovery

### Prerequisites
```bash
sudo apt install -y chntpw qemu-utils
```

### Recover from a Running Docker Container (read-only)
```bash
# Mount the QEMU disk image via nbd
sudo modprobe nbd max_part=8
sudo qemu-nbd --connect=/dev/nbd0 -r /var/lib/docker/volumes/winapps_data/_data/data.img
sudo mount /dev/nbd0p3 /mnt/windows   # p3 is the Windows system partition

# View users
sudo chntpw -l /mnt/windows/Windows/System32/config/SAM
```

### Clear Password (container stopped)
```bash
# Must stop container first for write access
sudo docker stop WinApps

# Mount read-write (no -r flag)
sudo qemu-nbd --connect=/dev/nbd0 /var/lib/docker/volumes/winapps_data/_data/data.img
sudo mount /dev/nbd0p3 /mnt/windows

# Clear password (interactive)
sudo bash -c 'printf "1\nq\ny\n" | chntpw -u comage /mnt/windows/Windows/System32/config/SAM'

# Also allow blank passwords for RDP (optional)
sudo bash -c 'printf "cd ControlSet001\\\\Control\\\\Lsa\nnv 4 LimitBlankPasswordUse 0\nq\ny\n" | chntpw -e /mnt/windows/Windows/System32/config/SYSTEM'

# Clean up
sudo umount /mnt/windows
sudo qemu-nbd --disconnect /dev/nbd0
sudo docker start WinApps
```

### Inject Password-Reset Startup Script
Can also place a `.bat` file in the Windows startup folder:
```bash
echo 'net user comage "comage"' > /tmp/reset_pw.bat
sudo cp /tmp/reset_pw.bat "/mnt/windows/Users/comage/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/"
```

On next Windows boot + login, the script resets the password. User must log in once via VNC (blank password if cleared) for the script to execute.

## Windows Disk Partition Layout (QEMU raw image)

| Partition | Size | Content |
|-----------|------|---------|
| /dev/nbd0p1 | 128MB | EFI System |
| /dev/nbd0p2 | 128MB | MS Reserved |
| /dev/nbd0p3 | ~63GB | Windows (C:\) — contains SAM at `Windows/System32/config/SAM` |
| /dev/nbd0p4 | ~784MB | Windows Recovery Environment |

## NLA and FreeRDP Issues

On Ubuntu, FreeRDP v3 (`xfreerdp3`) has Kerberos NLA authentication issues:
```
nla_recv_pdu: ERRCONNECT_LOGON_FAILURE
kerberos_AcquireCredentialsHandleA: krb5_parse_name (Configuration file does not specify default realm)
```

### Solutions (in order of preference):
1. **Disable NLA on Windows** via VNC → Settings → Remote Desktop → Require NLA → OFF
2. **Use `/sec:tls`** after NLA is disabled on the Windows side
3. **Accept the account lockout** — reset via SAM recovery
  
After disabling NLA on Windows, the connection works with `/sec:tls` but NOT with default NLA negotiation.
