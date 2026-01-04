import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

FILENAME_RE = re.compile(r"^daily_papers_summary_(\d{8})\.md$")


def parse_ymd(s: str) -> datetime:
    """Parse YYYYMMDD string to datetime."""
    return datetime.strptime(s, "%Y%m%d")


def parse_date_range(args: List[str]) -> Optional[Tuple[datetime, datetime]]:
    """
    Accept:
      - None
      - ["YYYYMMDD-YYYYMMDD"]
      - ["YYYYMMDD", "YYYYMMDD"]
    Return (start_dt, end_dt) inclusive.
    """
    if not args:
        return None

    if len(args) == 1:
        m = re.fullmatch(r"(\d{8})-(\d{8})", args[0])
        if not m:
            raise ValueError(
                "date range must be YYYYMMDD-YYYYMMDD or provide two args YYYYMMDD YYYYMMDD"
            )
        start_s, end_s = m.group(1), m.group(2)
    elif len(args) == 2:
        if not (re.fullmatch(r"\d{8}", args[0]) and re.fullmatch(r"\d{8}", args[1])):
            raise ValueError(
                "date range must be YYYYMMDD-YYYYMMDD or provide two args YYYYMMDD YYYYMMDD"
            )
        start_s, end_s = args[0], args[1]
    else:
        raise ValueError(
            "date range accepts either 1 arg (YYYYMMDD-YYYYMMDD) or 2 args (YYYYMMDD YYYYMMDD)"
        )

    start_dt = parse_ymd(start_s)
    end_dt = parse_ymd(end_s)
    if start_dt > end_dt:
        raise ValueError("start date must be <= end date")
    return start_dt, end_dt


def in_range(day: datetime, dr: Optional[Tuple[datetime, datetime]]) -> bool:
    if dr is None:
        return True
    start_dt, end_dt = dr
    return start_dt <= day <= end_dt


def collect_md_files(
    input_dir: Path, dr: Optional[Tuple[datetime, datetime]]
) -> List[Tuple[datetime, Path]]:
    """
    Return list of (date, path) for files matching daily_papers_summary_YYYYMMDD.md in range.
    """
    results: List[Tuple[datetime, Path]] = []
    for p in input_dir.glob("*.md"):
        m = FILENAME_RE.match(p.name)
        if not m:
            continue
        day = parse_ymd(m.group(1))
        if in_range(day, dr):
            results.append((day, p))

    results.sort(key=lambda x: x[0])
    return results


def merge_files(pairs: List[Tuple[datetime, Path]]) -> str:
    """
    Merge file contents with a header separator for each date.
    """
    chunks: List[str] = []
    for day, path in pairs:
        content = path.read_text(encoding="utf-8", errors="replace").strip()
        content = content.replace("# Daily Papers Summary", "").strip()
        # 分隔头：你也可以改成更简单的 "---"
        header = f"\n\n## {day.strftime('%Y-%m-%d')} ({path.name})\n\n"
        chunks.append(header + content + "\n")
    merged = "".join(chunks).lstrip()
    return merged


def main():
    ap = argparse.ArgumentParser(
        description="Merge daily_papers_summary_YYYYMMDD.md files in data/output into one markdown file."
    )
    ap.add_argument(
        "-i",
        "--input-dir",
        default="data/output",
        help="Input directory containing md files (default: data/output)",
    )
    ap.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output markdown filename to write (e.g. merged.md)",
    )
    ap.add_argument(
        "date_range",
        nargs="*",
        help="Optional date range: YYYYMMDD-YYYYMMDD or 'YYYYMMDD YYYYMMDD' (inclusive)",
    )
    args = ap.parse_args()

    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        raise SystemExit(f"Input dir not found: {input_dir}")

    try:
        dr = parse_date_range(args.date_range)
    except ValueError as e:
        raise SystemExit(f"Invalid date range: {e}")

    pairs = collect_md_files(input_dir, dr)
    if not pairs:
        range_info = ""
        if dr:
            range_info = (
                f" in range {dr[0].strftime('%Y%m%d')}-{dr[1].strftime('%Y%m%d')}"
            )
        raise SystemExit(f"No matching md files found under {input_dir}{range_info}")

    merged = merge_files(pairs)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(merged, encoding="utf-8")

    print(f"✅ Merged {len(pairs)} files into: {out_path}")
    print(f"First: {pairs[0][1].name}")
    print(f"Last : {pairs[-1][1].name}")


if __name__ == "__main__":
    main()
