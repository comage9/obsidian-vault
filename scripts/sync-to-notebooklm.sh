#!/bin/bash
# NotebookLM 자동 동기화 스크립트
# 사용법: ./sync-to-notebooklm.sh [파일경로]

NOTEBOOK_ID="461665a7-ed90-4307-8649-650fc6ac3e34"
VAULT_DIR="/tmp/obsidian-vault"

if [ -n "$1" ]; then
  # 특정 파일 업로드
  nlm source add "$NOTEBOOK_ID" --file "$1" --title "$(basename "$1")"
  exit $?
fi

# 오늘 변경된 파일 자동 업로드
TODAY=$(date +%Y-%m-%d)
find "$VAULT_DIR" -name "*.md" -type f ! -path "*/.git/*" -newer "$VAULT_DIR/.last_sync" 2>/dev/null | while read f; do
  rel="${f#$VAULT_DIR/}"
  echo "업로드: $rel"
  nlm source add "$NOTEBOOK_ID" --file "$rel" --title "$(basename "$f")" 2>&1
done

touch "$VAULT_DIR/.last_sync"
echo "동기화 완료"
