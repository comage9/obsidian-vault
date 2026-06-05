#!/bin/bash
# NotebookLM 자동 업로드 파이프라인
# 매일 23:00 크론 실행

NOTEBOOK_ID="461665a7-ed90-4307-8649-650fc6ac3e34"
VAULT_DIR="/tmp/obsidian-vault"
LOG_FILE="$VAULT_DIR/logs/notebooklm_sync.log"
MAX_RETRIES=3

mkdir -p "$VAULT_DIR/logs"
echo "========================================" >> "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 자동 업로드 시작" >> "$LOG_FILE"

# 최근 24시간 내 수정된 .md 파일
CHANGED_FILES=$(find "$VAULT_DIR" -type f -name "*.md" -not -path "*/.git/*" -not -path "*/.obsidian/*" -mtime -1)

if [ -z "$CHANGED_FILES" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 변경된 파일 없음" >> "$LOG_FILE"
    exit 0
fi

UPLOADED=0
FAILED=0

for file in $CHANGED_FILES; do
    rel="${file#$VAULT_DIR/}"
    success=0
    for (( i=1; i<=MAX_RETRIES; i++ )); do
        output=$(cd "$VAULT_DIR" && nlm source add "$NOTEBOOK_ID" --file "$rel" --title "$(basename "$file")" 2>&1)
        if [ $? -eq 0 ]; then
            echo "[$(date '+%H:%M:%S')] ✅ $rel" >> "$LOG_FILE"
            success=1
            UPLOADED=$((UPLOADED+1))
            break
        else
            echo "[$(date '+%H:%M:%S')] ⚠️ $rel 실패 ($i/$MAX_RETRIES)" >> "$LOG_FILE"
            sleep 5
        fi
    done
    if [ $success -eq 0 ]; then
        echo "[$(date '+%H:%M:%S')] ❌ $rel 최종 실패" >> "$LOG_FILE"
        FAILED=$((FAILED+1))
    fi
    sleep 0.5
done

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 완료: 성공 $UPLOADED, 실패 $FAILED" >> "$LOG_FILE"
