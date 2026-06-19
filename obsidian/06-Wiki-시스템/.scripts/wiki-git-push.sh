#!/usr/bin/env bash
# Wiki Git Auto-Sync — GitHub 자동 백업
# 실행: bash .scripts/wiki-git-push.sh
set -euo pipefail

VAULT="/home/comtop/workspace/Wiki"
WIKI_DIR="obsidian/06-Wiki-시스템"
LOG="$VAULT/$WIKI_DIR/Wiki/log.md"
DATE=$(date '+%Y-%m-%d %H:%M')

cd "$VAULT"

# 변경사항 확인
CHANGES=$(git status --porcelain -- "$WIKI_DIR/Wiki/" 2>/dev/null || true)
if [ -z "$CHANGES" ]; then
    echo "[$DATE] Git-Sync: 변경사항 없음"
    exit 0
fi

# 변경 파일 수
COUNT=$(echo "$CHANGES" | grep -c . || true)
echo "[$DATE] Git-Sync: ${COUNT}개 파일 변경"

# Stage → Commit
git add "$WIKI_DIR/Wiki/" 2>/dev/null
git commit -m "Wiki auto-sync: $(date '+%Y-%m-%d %H:%M')" 2>/dev/null || {
    echo "  ⚠️  commit 실패 (변경 없음?)"
    exit 0
}

# Push (재시도: rebase on reject)
if git push origin master 2>/dev/null; then
    echo "  ✅ Push 성공"
else
    echo "  ⚠️  Push 실패 — rebase 후 재시도"
    sleep 2
    git pull --rebase origin master 2>/dev/null || {
        echo "  ❌ Rebase 실패 — 수동 확인 필요"
        exit 1
    }
    if git push origin master 2>/dev/null; then
        echo "  ✅ Push 성공 (rebase 후)"
    else
        echo "  ❌ Push 실패 — 수동 확인 필요"
        exit 1
    fi
fi

# 로그 기록
echo "" >> "$LOG"
echo "### $DATE — Git Auto-Sync: ${COUNT}개 파일 → GitHub" >> "$LOG"
echo "[$DATE] Git-Sync 완료"
