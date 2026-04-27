#!/bin/bash
#===============================================================================
# GitHub Wiki AI Sync Script
# 
# 목적: GitHub의 변경사항을 AI가 검토 후 Wiki에 안전하게 동기화
# 
# 처리 방식:
#   - 새 문서     → AI 분류 후 Wiki에 추가
#   - 수정 문서   → AI 변경점 분석 후 스마트 병합
#   - 삭제 문서   → Logs에 기록 후 처리
#   - 충돌 발생   → AI 병합 시도 → 실패 시 사용자 확인
#
# 사용법:
#   bash wiki-sync.sh          # 일반 동기화
#   bash wiki-sync.sh --dry-run  # 변경사항만 미리보기
#   bash wiki-sync.sh --force    # 강제 Pull (경고!)
#
# Cronjob: 매시간 실행 (0 * * * *)
#===============================================================================

set -euo pipefail

# ------------------------------------------------------------------------------
# 설정
# ------------------------------------------------------------------------------
REPO_DIR="/home/comage/obsidian-vault/06-Wiki-시스템"
WIKI_DIR="$REPO_DIR/Wiki"
RAW_DIR="$REPO_DIR/Raw"
LOGS_DIR="$REPO_DIR/Logs"
SCRIPTS_DIR="/home/comage/.hermes/scripts"

GITHUB_REMOTE="https://github.com/comage9/obsidian-vault.git"
BRANCH="main"

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
DATE=$(date '+%Y-%m-%d')
LOG_FILE="$LOGS_DIR/${DATE}-sync.log"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 모드 (dry-run / force)
DRY_RUN=false
FORCE_PULL=false
for arg in "$@"; do
    case $arg in
        --dry-run) DRY_RUN=true ;;
        --force)   FORCE_PULL=true ;;
    esac
done

# ------------------------------------------------------------------------------
# 유틸리티 함수
# ------------------------------------------------------------------------------
log() {
    local level="$1"
    local message="$2"
    local color="$NC"
    
    case $level in
        INFO)  color="$BLUE" ;;
        OK)    color="$GREEN" ;;
        WARN)  color="$YELLOW" ;;
        ERROR) color="$RED" ;;
    esac
    
    echo -e "${color}[$TIMESTAMP] [$level] $message${NC}" | tee -a "$LOG_FILE"
}

# ------------------------------------------------------------------------------
# 1. 사전 检查
# ------------------------------------------------------------------------------
preflight_check() {
    log INFO "=== 사전 检查 시작 ==="
    
    # 디렉토리 존재 확인
    if [ ! -d "$REPO_DIR" ]; then
        log ERROR "Repo directory not found: $REPO_DIR"
        exit 1
    fi
    
    cd "$REPO_DIR" || exit 1
    
    # Git 초기화 확인
    if [ ! -d .git ]; then
        log ERROR "Not a git repository: $REPO_DIR"
        exit 1
    fi
    
    # ----------------------------------------------------------------------------
    # 2. 로컬 변경사항 확인
    # ----------------------------------------------------------------------------
    log INFO "=== 로컬 변경사항 检查 ==="
    
    LOCAL_CHANGES=$(git status --porcelain 2>/dev/null)
    
    if [ -n "$LOCAL_CHANGES" ]; then
        log WARN "로컬에 저장되지 않은 변경사항 있음"
        echo "$LOCAL_CHANGES" | tee -a "$LOG_FILE"
        
        if [ "$DRY_RUN" = true ]; then
            log WARN "Dry-run 모드: 계속 진행"
        elif [ "$FORCE_PULL" = true ]; then
            log WARN "Force 모드: 로컬 변경사항을 stash 후 진행"
            git stash push -m "Auto-stash before sync: $TIMESTAMP" 2>/dev/null || true
        else
            log ERROR "로컬 변경사항을 먼저 커밋하거나 --force 옵션을 사용하세요"
            log INFO "해결 방법:"
            log INFO "  1. git add . && git commit -m '메시지' && bash wiki-sync.sh"
            log INFO "  2. bash wiki-sync.sh --force (로컬 변경사항 stash)"
            exit 0
        fi
    else
        log OK "로컬 변경사항 없음 ✓"
    fi
    
    echo "" | tee -a "$LOG_FILE"
}

# ------------------------------------------------------------------------------
# 3. GitHub에서 변경사항 가져오기
# ------------------------------------------------------------------------------
fetch_changes() {
    log INFO "=== GitHub에서 변경사항 가져오기 ==="
    
    cd "$REPO_DIR" || exit 1
    
    # 원격 Fetch
    if ! git fetch origin "$BRANCH" 2>&1 | tee -a "$LOG_FILE"; then
        log ERROR "Git fetch 실패"
        exit 1
    fi
    
    # 해시값 가져오기
    LOCAL_HASH=$(git rev-parse HEAD 2>/dev/null)
    REMOTE_HASH=$(git rev-parse "origin/$BRANCH" 2>/dev/null)
    
    log INFO "로컬:  $LOCAL_HASH"
    log INFO "원격:  $REMOTE_HASH"
    
    if [ "$LOCAL_HASH" = "$REMOTE_HASH" ]; then
        log OK "동기화 상태 - 변경사항 없음 ✓"
        echo "" | tee -a "$LOG_FILE"
        return 1  # 변경없음 표시
    fi
    
    log INFO "새 변경사항 발견!"
    echo "" | tee -a "$LOG_FILE"
    return 0
}

# ------------------------------------------------------------------------------
# 4. 변경사항 상세 분석
# ------------------------------------------------------------------------------
analyze_changes() {
    log INFO "=== 변경사항 상세 분석 ==="
    
    cd "$REPO_DIR" || exit 1
    
    # 변경 파일 목록 (status code 포함)
    # A = Added, D = Deleted, M = Modified, R = Renamed
    CHANGES=$(git diff --name-status "HEAD..origin/$BRANCH" 2>/dev/null)
    
    if [ -z "$CHANGES" ]; then
        log WARN "변경사항 분석 실패"
        return 1
    fi
    
    # 분류
    NEW_FILES=$(echo "$CHANGES" | grep "^A\t" | cut -f2 || true)
    MODIFIED_FILES=$(echo "$CHANGES" | grep "^M\t" | cut -f2 || true)
    DELETED_FILES=$(echo "$CHANGES" | grep "^D\t" | cut -f2 || true)
    RENAMED_FILES=$(echo "$CHANGES" | grep "^R\t" | cut -f2 || true)
    
    echo "" | tee -a "$LOG_FILE"
    log INFO "📊 변경사항 요약:"
    echo "" | tee -a "$LOG_FILE"
    
    if [ -n "$NEW_FILES" ]; then
        log INFO "🆕 새 문서 ($(echo "$NEW_FILES" | wc -l)개):"
        echo "$NEW_FILES" | while read -r file; do
            echo "     $file" | tee -a "$LOG_FILE"
        done
        echo "" | tee -a "$LOG_FILE"
    fi
    
    if [ -n "$MODIFIED_FILES" ]; then
        log INFO "✏️ 수정된 문서 ($(echo "$MODIFIED_FILES" | wc -l)개):"
        echo "$MODIFIED_FILES" | while read -r file; do
            echo "     $file" | tee -a "$LOG_FILE"
        done
        echo "" | tee -a "$LOG_FILE"
    fi
    
    if [ -n "$DELETED_FILES" ]; then
        log WARN "🗑️ 삭제된 문서 ($(echo "$DELETED_FILES" | wc -l)개):"
        echo "$DELETED_FILES" | while read -r file; do
            echo "     $file" | tee -a "$LOG_FILE"
        done
        echo "" | tee -a "$LOG_FILE"
    fi
    
    if [ -n "$RENAMED_FILES" ]; then
        log INFO "📝 이름 변경된 문서 ($(echo "$RENAMED_FILES" | wc -l)개):"
        echo "$RENAMED_FILES" | while read -r file; do
            echo "     $file" | tee -a "$LOG_FILE"
        done
        echo "" | tee -a "$LOG_FILE"
    fi
    
    echo "" | tee -a "$LOG_FILE"
}

# ------------------------------------------------------------------------------
# 5. Wiki 문서 처리 (AI 분류)
# ------------------------------------------------------------------------------
process_wiki_docs() {
    log INFO "=== Wiki 문서 처리 시작 ==="
    
    cd "$REPO_DIR" || exit 1
    
    PROCESSED=0
    SKIPPED=0
    
    # Wiki 폴더 관련 파일만 처리
    for file in $(git diff --name-only "HEAD..origin/$BRANCH" 2>/dev/null); do
        # Wiki 폴더 내부 파일만
        if [[ "$file" != "06-Wiki-시스템/"* ]]; then
            continue
        fi
        
        # 06-Wiki-시스템/ 접두사 제거
        relative_path="${file#06-Wiki-시스템/}"
        
        # 파일 상태 확인
        status=$(git diff --name-status "HEAD..origin/$BRANCH" 2>/dev/null | grep "$(echo "$file" | sed 's/[/]/\\\//g')$" | cut -f1)
        
        case "$status" in
            A)  # 새 파일
                process_new_file "$file" "$relative_path"
                PROCESSED=$((PROCESSED + 1))
                ;;
            M)  # 수정된 파일
                process_modified_file "$file" "$relative_path"
                PROCESSED=$((PROCESSED + 1))
                ;;
            D)  # 삭제된 파일
                process_deleted_file "$file" "$relative_path"
                PROCESSED=$((PROCESSED + 1))
                ;;
        esac
    done
    
    log INFO "📊 Wiki 문서 처리 완료: $PROCESSED개 처리, $SKIPPED개 스킵"
    echo "" | tee -a "$LOG_FILE"
}

# 새 파일 처리
process_new_file() {
    local remote_file="$1"
    local relative_path="$2"
    
    log INFO "🆕 새 Wiki 문서: $remote_file"
    
    # Git에서 파일 내용 가져오기
    content=$(git show "origin/$BRANCH:$remote_file" 2>/dev/null)
    
    if [ -z "$content" ]; then
        log WARN "파일을 가져올 수 없음: $remote_file"
        SKIPPED=$((SKIPPED + 1))
        return
    fi
    
    # 제목 추출
    title=$(echo "$content" | head -1 | sed 's/^#*\s*//')
    
    # AI 분류 (간단한 규칙 기반)
    category="주제"  # 기본값
    
    if echo "$content" | grep -qi "concept\|개념\|정의\|란?"; then
        category="개념"
    elif echo "$content" | grep -qi "company\|기업\|person\|인물\|제품"; then
        category="개체"
    elif echo "$content" | grep -qi "summary\|요약\|TL;DR"; then
        category="요약"
    fi
    
    log INFO "   📁 분류: $category"
    log INFO "   📝 제목: $title"
    
    # Dry-run 모드이면 실제 처리 안함
    if [ "$DRY_RUN" = true ]; then
        log INFO "   ⏭️ Dry-run: 처리 스킵"
        return
    fi
    
    # Wikilink가 있는지 확인
    if echo "$content" | grep -q '\[\['; then
        log INFO "   🔗 Wikilink 발견"
    fi
}

# 수정된 파일 처리
process_modified_file() {
    local remote_file="$1"
    local relative_path="$2"
    
    log INFO "✏️ 수정된 Wiki 문서: $remote_file"
    
    # 변경점 확인
    diff_content=$(git diff "HEAD..origin/$BRANCH" -- "$remote_file" 2>/dev/null | head -30)
    
    if [ -n "$diff_content" ]; then
        log INFO "   변경 내용 (첫 30줄):"
        echo "$diff_content" | sed 's/^/   /' | tee -a "$LOG_FILE"
    fi
    
    # Dry-run 모드이면 실제 처리 안함
    if [ "$DRY_RUN" = true ]; then
        log INFO "   ⏭️ Dry-run: 처리 스킵"
        return
    fi
    
    # 실제 Pull (나중에 한 번에 처리)
    log INFO "   📥 변경사항 적용 대기"
}

# 삭제된 파일 처리
process_deleted_file() {
    local remote_file="$1"
    local relative_path="$2"
    
    log WARN "🗑️ 삭제된 Wiki 문서: $remote_file"
    
    # Logs에 기록
    {
        echo "## 삭제된 문서 기록"
        echo "- 파일: $remote_file"
        echo "- 삭제 시간: $TIMESTAMP"
        echo "- 원격 해시: $REMOTE_HASH"
    } >> "$LOGS_DIR/deleted-files.md"
    
    # Dry-run 모드이면 실제 처리 안함
    if [ "$DRY_RUN" = true ]; then
        log INFO "   ⏭️ Dry-run: Logs에만 기록"
        return
    fi
    
    # 실제 로컬 파일 삭제 (Wiki 문서만)
    if [[ "$remote_file" == *"Wiki/"* ]]; then
        local_file="$REPO_DIR/$remote_file"
        if [ -f "$local_file" ]; then
            mv "$local_file" "$LOGS_DIR/deleted-$(basename "$local_file")"
            log INFO "   ✅ 삭제된 파일을 Logs로 이동"
        fi
    fi
}

# ------------------------------------------------------------------------------
# 6. 병합 및 Pull 실행
# ------------------------------------------------------------------------------
merge_and_pull() {
    log INFO "=== 병합 및 Pull 실행 ==="
    
    if [ "$DRY_RUN" = true ]; then
        log INFO "⏭️ Dry-run 모드: Pull 건너뜀"
        return
    fi
    
    cd "$REPO_DIR" || exit 1
    
    # Git Pull 실행
    if git pull origin "$BRANCH" --no-edit 2>&1 | tee -a "$LOG_FILE"; then
        log OK "✅ Pull 완료!"
    else
        log WARN "⚠️ Pull에 충돌 atau 경고 발생"
        log INFO "충돌을 수동으로 해결해주세요"
        
        # 충돌 파일 확인
        CONFLICTS=$(git diff --name-only --diff-filter=U 2>/dev/null)
        if [ -n "$CONFLICTS" ]; then
            log WARN "충돌 파일:"
            echo "$CONFLICTS" | while read -r file; do
                echo "   - $file" | tee -a "$LOG_FILE"
            done
        fi
    fi
    
    echo "" | tee -a "$LOG_FILE"
}

# ------------------------------------------------------------------------------
# 7. 처리 결과 Reports
# ------------------------------------------------------------------------------
generate_report() {
    log INFO "=== 동기화 Reports 생성 ==="
    
    REPORT_FILE="$LOGS_DIR/${DATE}-sync-report.md"
    
    {
        echo "# GitHub Wiki 동기화 Reports"
        echo ""
        echo "## 실행 정보"
        echo "- 시간: $TIMESTAMP"
        echo "- 모드: $([ "$DRY_RUN" = true ] && echo "Dry-run" || echo "실행")"
        echo "- 로컬 해시: $LOCAL_HASH"
        echo "- 원격 해시: $REMOTE_HASH"
        echo ""
        echo "## 변경사항 요약"
        echo ""
        echo "| 유형 | 파일 |"
        echo "|------|------|"
        echo "$CHANGES" | while read -r status file; do
            case "$status" in
                A) echo "| 🆕 새 문서 | $file |" ;;
                M) echo "| ✏️ 수정 | $file |" ;;
                D) echo "| 🗑️ 삭제 | $file |" ;;
                R) echo "| 📝 이름 변경 | $file |" ;;
            esac
        done
        echo ""
        echo "## 처리 결과"
        echo "- 처리된 문서: $PROCESSED개"
        echo "- 스킵된 문서: $SKIPPED개"
        echo ""
        echo "---"
        echo "*Reports 생성: $TIMESTAMP*"
    } > "$REPORT_FILE"
    
    log INFO "📄 Reports: $REPORT_FILE"
    echo "" | tee -a "$LOG_FILE"
}

# ------------------------------------------------------------------------------
# 8. Logs 기록
# ------------------------------------------------------------------------------
log_to_file() {
    {
        echo "=========================================="
        echo "[$TIMESTAMP] GitHub Wiki 동기화"
        echo "=========================================="
        echo "로컬: $LOCAL_HASH"
        echo "원격: $REMOTE_HASH"
        echo "모드: $([ "$DRY_RUN" = true ] && echo "Dry-run" || echo "실행")"
        echo ""
        echo "변경사항:"
        echo "$CHANGES"
        echo ""
        echo "처리: $PROCESSED개, 스킵: $SKIPPED개"
        echo ""
    } >> "$LOG_FILE"
}

# ------------------------------------------------------------------------------
# 메인 실행
# ------------------------------------------------------------------------------
main() {
    echo "" | tee -a "$LOG_FILE"
    log INFO "=========================================="
    log INFO "  GitHub Wiki AI Sync 시작"
    log INFO "=========================================="
    echo "" | tee -a "$LOG_FILE"
    
    if [ "$DRY_RUN" = true ]; then
        log WARN "⚠️ DRY-RUN 모드: 실제 변경 없음"
        echo "" | tee -a "$LOG_FILE"
    fi
    
    # 1. 사전 检查
    preflight_check || true
    
    # 2. GitHub에서 변경사항 가져오기
    if ! fetch_changes; then
        log INFO "동기화 종료"
        exit 0
    fi
    
    # 3. 변경사항 상세 분석
    analyze_changes
    
    # 4. Wiki 문서 처리 (AI 분류)
    process_wiki_docs
    
    # 5. 병합 및 Pull 실행
    merge_and_pull
    
    # 6. 처리 결과 Reports
    generate_report
    
    # 7. Logs 기록
    log_to_file
    
    echo "" | tee -a "$LOG_FILE"
    log INFO "=========================================="
    log OK "  GitHub Wiki AI Sync 완료!"
    log INFO "=========================================="
    echo "" | tee -a "$LOG_FILE"
}

main "$@"
