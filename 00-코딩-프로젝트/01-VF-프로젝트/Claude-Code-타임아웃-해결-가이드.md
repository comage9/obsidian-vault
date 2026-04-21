# Claude Code 타임아웃 문제 해결 가이드

## 문제 발견
- **증상**: Claude Code가 코드 생성 시 자주 타임아웃
- **테스트 결과**: 8초, 15초 타임아웃 → 실패 / 2분, 5분 타임아웃 → 성공
- **원인**: 타임아웃 시간이 너무 짧음

## 해결책

### 1. 환경변수 설정 (영구적)

#### Linux/macOS:
```bash
# ~/.bashrc 또는 ~/.zshrc에 추가
export CLAUDE_CODE_TIMEOUT=300      # 5분 (기본값)
export CLAUDE_TIMEOUT_MS=300000     # 300초 in milliseconds

# 적용
source ~/.bashrc
```

#### Windows (PowerShell):
```powershell
# 시스템 환경변수 설정
[System.Environment]::SetEnvironmentVariable('CLAUDE_CODE_TIMEOUT', '300', 'User')

# 현재 세션
$env:CLAUDE_CODE_TIMEOUT=300
```

#### Windows (CMD):
```batch
:: 사용자 환경변수 설정
setx CLAUDE_CODE_TIMEOUT 300

:: 현재 세션
set CLAUDE_CODE_TIMEOUT=300
```

### 2. 명령어 사용법

#### 기본 사용:
```bash
# 5분 타임아웃
timeout 300 claude --permission-mode bypassPermissions --print "작업 내용"

# 환경변수 활용
timeout $CLAUDE_CODE_TIMEOUT claude --print "작업"
```

#### 작업 복잡도별 타임아웃:
```bash
# 간단한 질문 (30초)
timeout 30 claude --print "정보 확인"

# 일반 코드 생성 (5분)
timeout 300 claude --print "함수 작성"

# 복잡한 컴포넌트 (10분)
timeout 600 claude --print "전체 React 컴포넌트"

# 매우 복잡한 작업 (30분)
timeout 1800 claude --print "프로젝트 구조 설계"
```

### 3. 자동화 스크립트

#### claude-wrapper.sh:
```bash
#!/bin/bash
# Claude Code 래퍼 스크립트

DEFAULT_TIMEOUT=${CLAUDE_CODE_TIMEOUT:-300}  # 기본 5분
PROMPT="$1"

# 복잡도 감지 (간단히 프롬프트 길이로)
if [ ${#PROMPT} -lt 50 ]; then
    TIMEOUT=30  # 간단 질문: 30초
elif [[ "$PROMPT" == *"작성"* ]] || [[ "$PROMPT" == *"코드"* ]]; then
    TIMEOUT=600  # 코드 생성: 10분
else
    TIMEOUT=$DEFAULT_TIMEOUT  # 기본값
fi

echo "⏱️ 타임아웃: ${TIMEOUT}초 | 📝 작업: ${PROMPT:0:50}..."
timeout $TIMEOUT claude --permission-mode bypassPermissions --print "$PROMPT"
```

#### 사용법:
```bash
chmod +x claude-wrapper.sh
./claude-wrapper.sh "TypeScript 함수 작성"
```

## 테스트 결과

### 성공 사례:
1. **2분 타임아웃**: VF outbound 탭 환경변수 처리 코드 생성 성공
2. **5분 타임아웃**: 테스트 console.log 코드 생성 성공
3. **5분 타임아웃**: VF outbound-tabs.tsx 전체 수정 코드 생성 중

### 패턴 발견:
- **간단 응답**: 30초 이내 가능
- **코드 생성**: 2-5분 필요
- **복잡 분석**: 5-10분 권장

## 문제 해결 체크리스트

### Claude Code가 응답하지 않을 때:
1. **타임아웃 확인**: 현재 설정값 확인
   ```bash
   echo $CLAUDE_CODE_TIMEOUT
   ```

2. **기본 테스트**: 간단한 응답 확인
   ```bash
   timeout 30 claude --print "안녕"
   ```

3. **프로세스 확인**: Claude Code 실행 상태
   ```bash
   ps aux | grep claude | grep -v grep
   ```

4. **리소스 확인**: 시스템 부하
   ```bash
   top -p $(pgrep claude)
   ```

### 성능 최적화 팁:

1. **프롬프트 최적화**:
   ```bash
   # 안 좋은 예 (너무 장황)
   timeout 300 claude --print "저는 React와 TypeScript를 사용하는 개발자입니다. 현재 VF 프로젝트의 outbound 탭에서 구글 시트 연결 문제가 발생하고 있습니다. 환경변수 OUTBOUND_GOOGLE_SHEET_URL이 설정되지 않았다는 에러가 나오는데, 이 문제를 해결하기 위한 코드를 작성해 주세요. 가능하다면 에러 처리와 로컬 폴백도 포함해 주세요."
   
   # 좋은 예 (간결)
   timeout 300 claude --print "outbound-tabs.tsx 수정: 환경변수 없을 때 로컬 JSON 사용, 에러 처리 포함"
   ```

2. **작업 분할**:
   ```bash
   # 한 번에 너무 많은 작업 X
   timeout 300 claude --print "1. 환경변수 읽기 2. 로컬 폴백 3. 에러 처리 4. 타입 정의"
   
   # 작업 분할 O
   timeout 300 claude --print "1. 환경변수 읽기 함수"
   timeout 300 claude --print "2. 로컬 JSON 폴백 함수"
   ```

3. **캐시 활용**:
   ```bash
   # 자주 사용하는 코드 템플릿 저장
   mkdir -p ~/.claude-templates
   echo "// 환경변수 읽기 템플릿" > ~/.claude-templates/env-read.ts
   ```

## 모니터링

### 로그 확인:
```bash
# Claude Code 실행 로그
claude --permission-mode bypassPermissions --debug --print "테스트" 2>&1 | tail -20

# 타임아웃 발생 시
timeout 10 claude --print "테스트" 2>&1 | grep -i "timeout\|terminated"
```

### 성능 메트릭:
```bash
# 응답 시간 측정
time timeout 300 claude --print "간단 코드 생성"

# 메모리 사용량
pmap $(pgrep claude) | tail -1
```

## 문제 예방

### 정기 점검:
1. **주간**: Claude Code 버전 확인
   ```bash
   claude --version
   ```

2. **월간**: 환경변수 및 설정 점검
   ```bash
   env | grep CLAUDE
   ```

3. **분기별**: 성능 벤치마크
   ```bash
   ./claude-benchmark.sh
   ```

### 백업 계획:
1. **대체 도구**: GitHub Copilot, Codeium 등 평가
2. **로컬 템플릿**: 자주 사용하는 코드 패턴 저장
3. **문서화**: 문제 해결 과정 체계적 기록

## 적용 사례: VF 프로젝트

### 문제:
- VF outbound 탭 구글 시트 연결 에러
- `OUTBOUND_GOOGLE_SHEET_URL is not set`

### 해결 과정:
1. **초기 실패**: 15초 타임아웃 → 타임아웃
2. **원인 분석**: 타임아웃 시간 부족
3. **해결 적용**: 5분 타임아웃 설정
4. **결과**: Claude Code 정상 코드 생성

### 적용 코드 예시:
```bash
# VF outbound 탭 수정 코드 생성
timeout 300 claude --print "outbound-tabs.tsx handleSync 함수 수정: 환경변수 없으면 로컬 JSON 사용"

# 환경변수 설정 가이드
timeout 180 claude --print "Windows .env 파일 설정 방법과 서버 재시작 스크립트"
```

## 결론

### 핵심 요약:
1. **문제**: 타임아웃 시간 부족
2. **해결**: 5-10분 타임아웃 설정
3. **결과**: Claude Code 정상 작동
4. **유지**: 환경변수 영구 설정

### 권장 설정:
```bash
# ~/.bashrc 또는 시스템 환경변수
export CLAUDE_CODE_TIMEOUT=300      # 기본 5분
export CLAUDE_TIMEOUT_MS=300000     # 밀리초 변환

# 프로젝트별 오버라이드 (선택)
# export VF_PROJECT_TIMEOUT=600      # VF 프로젝트는 10분
```

### 최종 확인:
```bash
# 설정 확인
echo "타임아웃: $CLAUDE_CODE_TIMEOUT초"

# 기능 테스트
timeout $CLAUDE_CODE_TIMEOUT claude --print "간단한 TypeScript 인터페이스 작성"
```

---
*이 가이드는 2026-04-16 Claude Code 타임아웃 문제 해결 과정을 문서화한 것입니다.*