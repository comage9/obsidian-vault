# 옵시디언 정기 유지보수 시스템 설치 가이드

## 🚀 빠른 시작

### 1. 크론 작업 등록
```bash
# 현재 사용자의 크론탭 편집
crontab -e

# 다음 내용 추가:
0 9 * * 1 cd /tmp/obsidian-vault && ./.maintenance/scripts/weekly_index_review.sh
0 18 * * * cd /tmp/obsidian-vault && ./.maintenance/scripts/connection_monitor.sh
```

### 2. 수동 실행 테스트
```bash
# 주간 인덱스 검토 테스트
cd /tmp/obsidian-vault
./.maintenance/scripts/weekly_index_review.sh

# 연결률 모니터링 테스트
./.maintenance/scripts/connection_monitor.sh
```

###
### 3. 자동 인덱싱 활성화 (선택사항)
```bash
# inotify-tools 설치 (파일 감시 도구)
sudo apt-get install inotify-tools

# 백그라운드에서 자동 인덱싱 실행
cd /tmp/obsidian-vault
nohup ./.maintenance/scripts/auto_index_new_files.sh > /dev/null 2>&1 &
```

## 📊 모니터링 접근

### 대시보드 보기
```bash
# 연결률 대시보드
cat /tmp/obsidian-vault/.maintenance/reports/connection_dashboard.md

# 최근 보고서
ls -la /tmp/obsidian-vault/.maintenance/reports/
```

### 로그 확인
```bash
# 주간 검토 로그
tail -f /tmp/obsidian-vault/.maintenance/logs/weekly_*.log

# 자동 인덱싱 로그
tail -f /tmp/obsidian-vault/.maintenance/logs/auto_index_*.log
```

## 🔧 문제 해결

### 일반적인 문제
1. **스크립트 실행 권한 없음**
   ```bash
   chmod +x /tmp/obsidian-vault/.maintenance/scripts/*.sh
   ```

2. **크론 작업 실행 안됨**
   ```bash
   # 크론 로그 확인
   grep CRON /var/log/syslog
   
   # 수동 실행 테스트
   /tmp/obsidian-vault/.maintenance/scripts/weekly_index_review.sh
   ```

3. **연결률 계산 오류**
   ```bash
   # 수동 통계 확인
   cd /tmp/obsidian-vault
   find . -name "*.md" | wc -l
   grep -c "\[\[.*\]\]" index.md
   ```

## 📈 연결률 100% 목표 계획

### 단계별 목표
1. **1단계 (현재 ~ 1주)**: 26% → 50%
2. **2단계 (2주)**: 50% → 75%
3. **3단계 (3주)**: 75% → 100%

### 주간 작업
- 월요일: 주간 인덱스 검토 실행
- 화~금: 신규 파일 자동 인덱싱
- 토요일: 연결률 모니터링 및 보고
- 일요일: 시스템 점검 및 백업

## 🔄 Git 통합

### 변경사항 자동 커밋
```bash
# 인덱스 변경 시 자동 커밋 스크립트 (선택사항)
cd /tmp/obsidian-vault
git add index.md
git commit -m "docs: 인덱스 자동 업데이트 - 연결률 $(grep -c '\[\[.*\]\]' index.md)/$(find . -name '*.md' | wc -l) 파일"
```

## 📞 지원
- **문제 발생**: 로그 파일 확인 후 재실행
- **기능 요청**: 스크립트 수정 또는 확장
- **문의**: 시스템 관리자

---
*시스템 버전: 1.0.0 | 생성일: 2026-04-20*
