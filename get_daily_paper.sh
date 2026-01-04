#!/usr/bin/env bash
set -euo pipefail

# 用法：
#   ./run_range.sh 20251201-20260101
#   ./run_range.sh 20251201 20260101
#
# 每天执行：
#   python src/download_daily_papers.py YYYYMMDD

usage() {
  echo "Usage:"
  echo "  $0 YYYYMMDD-YYYYMMDD"
  echo "  $0 YYYYMMDD YYYYMMDD"
  exit 1
}

# 解析输入
if [[ $# -eq 1 ]]; then
  if [[ "$1" =~ ^([0-9]{8})-([0-9]{8})$ ]]; then
    start="${BASH_REMATCH[1]}"
    end="${BASH_REMATCH[2]}"
  else
    usage
  fi
elif [[ $# -eq 2 ]]; then
  if [[ "$1" =~ ^[0-9]{8}$ && "$2" =~ ^[0-9]{8}$ ]]; then
    start="$1"
    end="$2"
  else
    usage
  fi
else
  usage
fi

# 检测 GNU date or BSD date
is_gnu_date() {
  date --version >/dev/null 2>&1
}

to_epoch() {
  local ymd="$1"
  local y="${ymd:0:4}" m="${ymd:4:2}" d="${ymd:6:2}"
  if is_gnu_date; then
    date -d "${y}-${m}-${d}" +%s
  else
    # macOS / BSD date
    date -j -f "%Y-%m-%d" "${y}-${m}-${d}" +%s
  fi
}

from_epoch_ymd() {
  local epoch="$1"
  if is_gnu_date; then
    date -d "@${epoch}" +%Y%m%d
  else
    date -r "${epoch}" +%Y%m%d
  fi
}

start_ts="$(to_epoch "$start")"
end_ts="$(to_epoch "$end")"

if (( start_ts > end_ts )); then
  echo "Error: start date must be <= end date"
  exit 2
fi

one_day=$((24*60*60))

ts="$start_ts"
while (( ts <= end_ts )); do
  ymd="$(from_epoch_ymd "$ts")"
  echo "==> Running for ${ymd}"
  python src/download_daily_papers.py "$ymd"
  ts=$((ts + one_day))
done

python src/daily_papers_abstract_extractor.py


python src/merge.py -o "$start-$end-dailypapers.md"

echo "Done."
