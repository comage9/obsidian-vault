# winapps-docker-setup.md

## Docker 엔진 설치
```bash
sudo apt install -y docker.io docker-compose-v2
sudo usermod -aG docker $USER
# 그룹 적용: sg docker -c "command" 또는 재로그인
```

## WinApps 클론 및 의존성
```bash
git clone https://github.com/winapps-org/winapps.git
sudo apt install -y curl dialog freerdp3-x11 git iproute2 libnotify-bin netcat-openbsd
```

## Windows VM 실행 (dockur/windows)
```bash
sudo docker run -d --name WinApps \
  --device /dev/kvm \
  --device /dev/net/tun \
  --device /dev/bus/usb \      # USB 패스스루
  --cap-add NET_ADMIN \
  -p 127.0.0.1:8006:8006 \
  -p 127.0.0.1:3389:3389/tcp \
  -p 127.0.0.1:3389:3389/udp \
  -v winapps_data:/storage \
  -v /home/comage:/shared \
  -v /path/to/oem:/oem \
  -e VERSION="11" \
  -e RAM_SIZE="4G" \
  -e CPU_CORES="4" \
  -e DISK_SIZE="64G" \
  -e USERNAME="user" \
  -e PASSWORD="pass" \
  -e ARGUMENTS="-usb -device usb-host,vendorid=0x0a5f,productid=0x0069" \
  --restart on-failure \
  ghcr.io/dockur/windows:latest
```

## WinApps 설정 (config)
~/.config/winapps/winapps.conf:
```
RDP_USER="user"
RDP_PASS="pass"
RDP_DOMAIN=""
RDP_IP="127.0.0.1"
RDP_PORT="3389"
OPEN_DEFAULT="yes"
```

## 설치 실행
```bash
cd /path/to/winapps
sg docker -c "./setup.sh --user"
```

## RDP 문제 해결

### NLA (Kerberos) 실패
- 증상: `ERRCONNECT_LOGON_FAILURE` + Kerberos 오류
- 해결: VNC(http://127.0.0.1:8006)로 Windows 접속 → RDP 설정 → NLA 끄기

### 계정 잠김
- 증상: `ERRCONNECT_ACCOUNT_LOCKED_OUT`
- 해결: `sudo docker restart WinApps` 후 재시도

### 비밀번호 초기화 (SAM)
```bash
sudo docker stop WinApps
sudo apt install -y chntpw qemu-utils
sudo qemu-nbd --connect=/dev/nbd0 /var/lib/docker/volumes/winapps_data/_data/data.img --format=raw
sudo mount /dev/nbd0p3 /mnt/windows
sudo chntpw -u username /mnt/windows/Windows/System32/config/SAM
# 메뉴: 1 (Clear password) → q → y
sudo umount /mnt/windows && sudo qemu-nbd --disconnect /dev/nbd0
sudo docker start WinApps
```

### 빈 비밀번호 RDP 허용 (레지스트리)
```bash
sudo chntpw -e /mnt/windows/Windows/System32/config/SYSTEM << 'EOS'
cd ControlSet001\Control\Lsa
nv 4 LimitBlankPasswordUse 0
q
y
EOS
```

### Windows 시작프로그램에 스크립트 등록
```bash
echo 'net user username "newpassword"' > reset_pw.bat
sudo cp reset_pw.bat "/mnt/windows/Users/username/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/"
```

## USB 패스스루 확인
```bash
# VM 내부에서 장치 확인
lsusb  # 호스트
sudo docker exec WinApps ls /dev/bus/usb/  # 컨테이너
```
