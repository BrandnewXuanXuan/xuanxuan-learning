#!/bin/bash
# 發佈前檢查：掃描「將被 commit 的檔案」有沒有可能的隱私資料。有命中就以非 0 結束。
cd "$(dirname "$0")" || exit 2

# commit 作者必須是 GitHub 匿名信箱，避免個人 Email 進入公開的 git 紀錄
case "$(git config user.email)" in
  *@users.noreply.github.com) ;;
  *) echo "⚠️ 這個 repo 的 git user.email 不是 GitHub 匿名信箱，請先設定再 commit"; exit 1 ;;
esac
files=$(git ls-files --cached --others --exclude-standard | grep -v '^check-privacy.sh$')
[ -z "$files" ] && { echo "沒有檔案可檢查"; exit 0; }

pattern='(sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{30,}|-----BEGIN [A-Z ]*PRIVATE KEY|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|/Users/[A-Za-z]|Mobile Documents|iCloud~md~obsidian|ANTHROPIC_AUTH_TOKEN|api[_-]?key[\"'\'' ]*[:=])'

hits=$(echo "$files" | tr '\n' '\0' | xargs -0 grep -nIE "$pattern" 2>/dev/null)
if [ -n "$hits" ]; then
  echo "⚠️ 可能含隱私資料，請確認後再發佈："
  echo "$hits"
  exit 1
fi
echo "✓ 未發現金鑰、Email 或本機路徑"
