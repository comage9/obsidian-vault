# VF 체크인 자동화

> **MS Forms 데일리 체크인을 매일 13:00에 자동 제출한다.**

## 한 줄 요약

| 항목 | 값 |
|------|-----|
| 프로젝트 | `E:\coding\vf-checkin\` |
| 폼 | MS Forms (VF 출고 운영 일일 체크인) |
| 센터 | VF67 |
| 이름 | 김주현 |
| 연락처 | **010-6563-2242** (2026-06-27 변경) |
| 출고 운영 시간 | 14:00~01:00 |
| 근무 인원 | 3 |
| 시설 피해 | 없음 |
| 트리거 | 매일 **오후 1:00** (SYSTEM 권한) |
| 실제 실행 | 13:00 ~ 13:59 사이 무작위 (0~59분 랜덤) |
| 스킬 | `vf-checkin-msforms` v1.0.0 |

## 동작 방식

1. 작업 스케줄러가 매일 13:00에 `node vf-checkin.js` 트리거
2. 스크립트 내부에서 **0~59분 무작위 대기** → 사람처럼 보이기 위함
3. `playwright-cli` 헤드리스 브라우저로 폼 열기 (1920×1080)
4. 정의된 값 자동 입력 → **스크린샷 3장** 저장
   - `before1`: 입력 후 상단
   - `before2`: 시설피해 선택 후 하단
   - `after`: 제출 후
5. 30일 지난 스크린샷 자동 삭제

## 즉시 실행

```bash
cd E:\coding\vf-checkin
node vf-checkin.js --now
```

`--now` 플래그 → 랜덤 대기 건너뛰고 즉시 실행. 테스트용.

## 데이터 변경 방법

`vf-checkin.js`의 `DATA` 객체 수정:

```javascript
const DATA = {
    center: 'VF67',
    name: '김주현',
    phone: '010-NEW-NUMBER',  // ← 여기
    workTime: '14:00~01:00',
    workerCount: '3',
    facilityDamage: '없음'
};
```

스케줄러는 그대로 둬도 됨 (다음 트리거 시 자동 반영).

## 스케줄러 관리

```powershell
# 상태 확인
Get-ScheduledTask -TaskName 'VF-Checkin' | Get-ScheduledTaskInfo

# 수동 실행
Start-ScheduledTask -TaskName 'VF-Checkin'

# 재등록 (트리거/액션 변경 시)
powershell -ExecutionPolicy Bypass -File E:\coding\vf-checkin\create-task.ps1

# 제거
Unregister-ScheduledTask -TaskName 'VF-Checkin' -Confirm:$false
```

## ⚠️ 주의사항

### 1. MS Forms ref ID 함정
스크립트는 `e68`, `e84` 같은 **ephemeral ref ID**를 직접 참조.
- 폼 페이지 구조가 바뀌면 ID 변경 → 입력 실패
- **증상**: 콘솔에는 입력 성공 메시지, 실제 폼은 빈 상태
- **검증**: `screenshots/before1_*.png` 를 vision으로 확인
- **수정**: `playwright-cli snapshot` 으로 새 selector 수집

### 2. 데일리 1회 vs 수동 실행 충돌
`--now` 수동 실행 시 같은 날 자동 트리거까지 두 번 제출될 수 있음.
폼 정책상 중복 허용 여부 확인.

### 3. SYSTEM 권한 + 헤드드 브라우저
SYSTEM 계정 headed 모드 → 로그인된 세션 필요. PC 절전 모드 해제 권장.

## 변경 이력

| 날짜 | 변경 |
|------|------|
| 2026-06-27 | 연락처 010-4725-2242 → 010-6563-2242, 스킬화 v1.0.0 |
| ~ | 초기 작성 (ref ID 하드코딩) |

## 관련 링크

- 스킬: `~/.local/share/hermes/skills/dogfood/vf-checkin-msforms/SKILL.md`
- 스크립트: `E:\coding\vf-checkin\vf-checkin.js`
- 스크린샷: `E:\coding\vf-checkin\screenshots\`
- GitHub: https://github.com/comage9/obsidian-vault (이 문서)
