# WinApps RDP Troubleshooting Session (2026-06-01)

## Environment
- Host: Ubuntu 24.04 Noble
- LibreOffice: 24.2.7.2 → 26.2.2.2 (upgraded via ppa:libreoffice/ppa)
- FreeRDP: 3.5.1+dfsg1 (from Ubuntu repos)
- Docker: 24.0.7 (from Ubuntu repos)
- Kernel: 6.17.0-35-generic
- CPU: AMD Ryzen 7 2700X (8 cores, KVM enabled)
- User: comage

## Container Setup
- Image: `ghcr.io/dockur/windows:latest` (v5.15)
- Version: Windows 11 (VERSION="11")
- RAM: 4G, CPU: 4 cores, Disk: 64GB
- NoVNC: http://127.0.0.1:8006
- RDP: 127.0.0.1:3389
- User: comage / Password: comage

## Installation Sequence

| Time | Event |
|------|-------|
| T+0s | Container starts |
| T+0s | ISO download begins from Microsoft servers |
| T+12min | Download completes (5.6GB at ~8MB/s) |
| T+13min | Image extraction + driver injection |
| T+14min | OEM folder added + win11x64.xml applied |
| T+15min | QEMU boots from DVD (UEFI) |
| T+20min | Windows installation automated via XML |
| T+25min | Windows Boot Manager loads from HD |
| T+30min | Windows OOBE executes (automated) |
| T+33min | RDP port 3389 opens |
| T+33min+ | RDP auth works but NLA fails |

## Error Diagnosis Chain

```
Test 1: xfreerdp3 /v:127.0.0.1:3389 /u:comage /p:comage /cert:ignore +auth-only
→ Exit 0 (NLA errors but auth-only returns 0)

Test 2: xfreerdp3 /v:... /u:... /p:... /sec:tls +auth-only
→ Exit 0 (TLS works for auth-only)

Test 3: xfreerdp3 /v:... /u:... /p:... /sec:rdp /app:program:"cmd.exe",cmd:"/C echo test"
→ BIO_read error 104 (Connection reset by peer)

Test 4: xfreerdp3 /v:... /u:... /p:... -authentication
→ Timeout waiting for activation (Windows at login screen)

Test 5: xfreerdp3 /v:... /u:... /p:... /sec:nla /auth-pkg-list:ntlm
→ ERRCONNECT_LOGON_FAILURE (NLA still fails)

WinApps setup internal test:
→ HYBRID_REQUIRED_BY_SERVER after forcing /sec:tls
→ ERRCONNECT_LOGON_FAILURE with default NLA
```

## Root Cause

FreeRDP v3.5.1 on Ubuntu 24.04 has a Kerberos integration issue: `krb5_parse_name (Configuration file does not specify default realm)`. This prevents NLA (Network Level Authentication) from working with RDP credentials. Windows requires NLA by default.

The Kerberos error occurs in `kerberos_AcquireCredentialsHandleA` before the actual NTLM fallback has a chance to work. The `auth-pkg-list:ntlm` flag does NOT prevent the Kerberos attempt — it still fails first.

## Fix Applied (Documented)

The confirmed fix path was not completed in this session. Next steps:

1. Open http://127.0.0.1:8006 (noVNC)
2. Log into Windows desktop with comage/comage
3. Settings → Remote Desktop → Disable "Require NLA"
4. Log out
5. Re-run `./setup.sh --user` via `sg docker`

### Alternative Workaround (not tested)

Create a `/etc/krb5.conf` or `/etc/krb5.conf.d/` snippet defining a default realm:
```
[libdefaults]
default_realm = WORKGROUP
```
