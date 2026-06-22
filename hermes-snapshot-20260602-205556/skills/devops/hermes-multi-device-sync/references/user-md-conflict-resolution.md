# USER.md / SOUL.md 파일 충돌 및 교차 플랫폼 동기화

## 증상

Syncthing UI에 '동기화 미완료 항목'이 1개 표시되며 파일 크기가 0 B:
```
동기화 미완료 항목: USER.md 0 B ... 수정 기기: DESKTOP-B12F6DJ
```
Windows `dir`에선 파일이 보이지 않거나 0 B 파일로 존재.

## 원인

- 양방향(sendreceive) 모드에서 양쪽에서 동시에 같은 파일이 생성/수정됨
- Windows에 빈 파일(0 B)이 먼저 생성되고 Syncthing이 충돌로 인식
- Syncthing DB에 0 B 레코드가 고정되어 UI에 계속 표시

## 해결 순서

1. Linux 측에서 파일 `touch`로 갱신:
   ```bash
   touch /opt/hermes/memories/USER.md
   ```
2. Syncthing 웹 UI → **"모두 재탐색"**
3. 그래도 해결 안 되면 Windows 탐색기에서 해당 파일 삭제 후 재탐색
4. Syncthing이 Linux 쪽 정상 파일을 재전송

**절대 금지:**
- Windows에서 "Override Changes" 선택
- Windows에서 빈 파일을 수동 편집

## 예방: USER.md / SOUL.md 교차 플랫폼 관리

두 Hermes 인스턴스(Linux / Windows)가 동시에 USER.md와 SOUL.md를 수정하면
항상 충돌 위험이 있다. 해결 전략:

### 1. 마스터 기기에서만 USER.md/SOUL.md 관리
- USER.md와 SOUL.md의 **쓰기 작업**은 Linux 서버에서만 수행
- Windows Hermes는 읽기 전용으로 사용
- USER.md가 Windows Hermes에 의해 예기치 않게 수정되지 않도록
  `.stignore`에 `USER.md`를 추가하는 것도 방법

### 2. SOUL.md 단일 복사본 유지
- SOUL.md는 Hermes Agent의 정체성 정의 파일 (`~/.hermes/SOUL.md`)
- Linux와 Windows가 동일한 SOUL.md를 공유해야 같은 성격/어조 유지
- Syncthing 공유 폴더 범위 밖이므로, 다음 방법 중 선택:
  - (가장 간단) 양쪽에 같은 내용 복사-붙여넣기
  - (고급) 링크 걸기: Windows `%USERPROFILE%\.hermes\SOUL.md` →
    `E:\hermes-backup\memories\SOUL.md`

### 3. USER.md/SOUL.md 템플릿 차이 고려
USER.md는 각 기기마다 일부 내용이 다를 수 있음:
- Linux: `agent-runner.sh`, `Reasonix ACP` 등 Linux 특화 정보
- Windows: `PYTHONRECURSIONLIMIT`, Windows 경로 등

공통 부분만 Syncthing으로 공유하고 기기별 차이는 각 로컬 USER.md에 추가.

## Windows Hermes SOUL.md 설정 명령어

```powershell
# 내용 확인
type %USERPROFILE%\.hermes\SOUL.md

# 편집
notepad %USERPROFILE%\.hermes\SOUL.md

# 적용
hermes gateway restart
```
