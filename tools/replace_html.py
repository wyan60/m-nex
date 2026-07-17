#!/usr/bin/env python3
"""
指定フォルダ以下の全HTMLファイルに対して、
特定の文字列を一括置換するツール。

使用例:
python3 tools/replace_html.py \
  --root . \
  --old 'https://ecogislab.sfc.keio.ac.jp/wiki/index.php?title=Main_Page'\
  --new '../wiki/' \
  --dry-run

確認後:
python3 tools/replace_html.py \
  --root . \
  --old 'https://ecogislab.sfc.keio.ac.jp/wiki/index.php?title=Main_Page'\
  --new '../wiki/'
"""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="フォルダ以下の全HTMLファイルで文字列を一括置換します。"
    )
    parser.add_argument(
        "--root",
        default=".",
        help="検索対象のルートフォルダ。既定値は現在のフォルダ。",
    )
    parser.add_argument(
        "--old",
        required=True,
        help="置換前の文字列。",
    )
    parser.add_argument(
        "--new",
        required=True,
        help="置換後の文字列。",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="変更せず、対象ファイルと置換件数だけ表示します。",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="変更前のHTMLを .bak ファイルとして保存します。",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()

    if not root.exists() or not root.is_dir():
        print(f"エラー: フォルダが見つかりません: {root}", file=sys.stderr)
        return 1

    total_files = 0
    total_replacements = 0

    for path in sorted(root.rglob("*.html")):
        # Git管理領域やバックアップ領域は除外
        if ".git" in path.parts or "node_modules" in path.parts:
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            print(f"スキップ（UTF-8ではない可能性）: {path}")
            continue
        except OSError as exc:
            print(f"スキップ（読み込み失敗）: {path}: {exc}")
            continue

        count = text.count(args.old)
        if count == 0:
            continue

        total_files += 1
        total_replacements += count
        print(f"{path.relative_to(root)}: {count}件")

        if args.dry_run:
            continue

        if args.backup:
            backup_path = path.with_suffix(path.suffix + ".bak")
            shutil.copy2(path, backup_path)

        updated = text.replace(args.old, args.new)
        path.write_text(updated, encoding="utf-8")

    print()
    if args.dry_run:
        print("ドライラン完了。ファイルは変更していません。")
    else:
        print("置換完了。")

    print(f"対象ファイル数: {total_files}")
    print(f"置換総数: {total_replacements}")

    if total_replacements == 0:
        print("指定した置換前文字列は見つかりませんでした。")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
