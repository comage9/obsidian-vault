# FreeRDP v3 NLA/Kerberos Issues on Ubuntu

## Symptom
```
com.winpr.sspi.Kerberos: krb5_parse_name (Configuration file does not specify default realm)
nla_recv_pdu: ERRCONNECT_LOGON_FAILURE
```

## Root Cause
FreeRDP v3 on Ubuntu prioritizes Kerberos for NLA authentication. Without a configured Kerberos realm (`/etc/krb5.conf`), it falls back to NTLM which can fail if:
- The Windows password is empty
- The password format is incompatible (e.g. dockur/windows base64 encoding bug)

## Diagnosis Commands
```bash
# Test NLA authentication
xfreerdp3 /v:127.0.0.1:3389 /u:user /p:pass /cert:ignore +auth-only

# Test with TLS (if NLA disabled on Windows)
xfreerdp3 /v:127.0.0.1:3389 /u:user /p:pass /cert:ignore /sec:tls +auth-only

# Test with RDP security (no NLA)
xfreerdp3 /v:127.0.0.1:3389 /u:user /p:pass /cert:ignore /sec:rdp +auth-only
```

## Error Codes
| Error | Meaning | Fix |
|-------|---------|-----|
| `ERRCONNECT_LOGON_FAILURE` [0x00020014] | Wrong credentials | Check username/password |
| `ERRCONNECT_ACCOUNT_LOCKED_OUT` [0x00020018] | Account locked | Restart container or wait 30min |
| `ERRCONNECT_ACCOUNT_RESTRICTION` [0x00020017] | Blank password blocked | Set LimitBlankPasswordUse=0 via chntpw |
| `HYBRID_REQUIRED_BY_SERVER` | NLA required | Disable NLA in Windows RDP settings |
| `ERRCONNECT_CONNECT_TRANSPORT_FAILED` [0x0002000D] | Connection reset | Wrong protocol negotiation |

## Workarounds
1. **Disable NLA on Windows** via VNC → Settings → Remote Desktop
2. **Clear/set password** via chntpw SAM editing (see windows-vm-docker skill)
3. **Restart container** to reset lockout counter
