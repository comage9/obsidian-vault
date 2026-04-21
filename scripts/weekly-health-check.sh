#!/bin/bash
# 주간 헬스체크 + NotebookLM 자동 자문
# 매주 월요일 08:00 크론 실행

NOTEBOOK_ID="461665a7-ed90-4307-8649-650fc6ac3e34"
VAULT_DIR="/tmp/obsidian-vault"
TODAY=$(date +%Y-%m-%d)
REPORT="$VAULT_DIR/reports/weekly_${TODAY}.md"

mkdir -p "$VAULT_DIR/reports"

echo "# 주간 헬스체크 - $TODAY" > "$REPORT"
echo "" >> "$REPORT"

# 1. 헬스체크 실행
echo "## 위키 헬스체크" >> "$REPORT"
bash "$VAULT_DIR/scripts/health-check.sh" >> "$REPORT" 2>&1
echo "" >> "$REPORT"

# 2. 파일 통계
TOTAL=$(find "$VAULT_DIR" -name "*.md" -type f ! -path "*/.git/*" | wc -l)
echo "## 통계" >> "$REPORT"
echo "- 전체 파일: $TOTAL" >> "$REPORT"
echo "- 날짜: $TODAY" >> "$REPORT"
echo "" >> "$REPORT"

# 3. NotebookLM 자문
echo "## NotebookLM 주간 분석" >> "$REPORT"
QUERY="지난주 작업을 분석해줘:
1. 주요 성과 (VF/키/시스템)
2. 미해결 작업
3. 모순/오래된 정보
4. 이번 주 최우선 작업"

NLM_RESPONSE=$(cd "$VAULT_DIR" && nlm notebook query "$NOTEBOOK_ID" "$QUERY" 2>&1 | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('answer', '응답 없음'))
except:
    print('NotebookLM 응답 실패')
")

echo "$NLM_RESPONSE" >> "$REPORT"

# 4. Git 커밋
cd "$VAULT_DIR"
git add -A
git commit -m "weekly: 주간 헬스체크 $TODAY" 2>/dev/null
git push origin master 2>/dev/null

echo "✅ 주간 보고서 생성: $REPORT"
