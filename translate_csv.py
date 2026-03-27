#!/usr/bin/env python
"""
Titan Quest 2 CSV直接翻訳スクリプト
ゲームのCSV String TableのSourceStringを日本語に翻訳する
"""

import csv
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

WORK_DIR = Path(__file__).parent
TEXT_DIR = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Titan Quest II\TQ2\Content\TQ2\Data\Text")
OUTPUT_DIR = WORK_DIR / "translated_csv"
MAX_WORKERS = 5

CLAUDE_CMD = r"C:\Users\abalol\AppData\Roaming\npm\claude.cmd"


def collect_csv_files():
    """全CSVファイルを収集"""
    files = []
    for csv_file in TEXT_DIR.rglob("*.csv"):
        files.append(csv_file)
    return sorted(files)


def read_csv_file(path):
    """CSVを読み込み"""
    rows = []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if len(row) >= 2:
                rows.append(row)
    return header, rows


def translate_csv_file(csv_file: Path) -> bool:
    """1つのCSVファイルをclaude -pで翻訳"""
    rel_path = csv_file.relative_to(TEXT_DIR)
    output_file = OUTPUT_DIR / rel_path
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # 既に翻訳済みならスキップ
    if output_file.exists():
        print(f"  [SKIP] {rel_path}")
        return True

    header, rows = read_csv_file(csv_file)
    if not rows:
        # 空ファイルはそのままコピー
        import shutil
        shutil.copy2(csv_file, output_file)
        print(f"  [COPY] {rel_path} (empty)")
        return True

    # 翻訳対象のテキストを抽出 (Key -> SourceString)
    texts = {}
    for row in rows:
        key = row[0]
        source = row[1]
        if source.strip():
            texts[key] = source

    if not texts:
        import shutil
        shutil.copy2(csv_file, output_file)
        print(f"  [COPY] {rel_path} (no text)")
        return True

    # プロンプト作成
    prompt = f"""Translate these Titan Quest II game texts from English to Japanese.
This is from file: {rel_path}
Return ONLY a valid JSON object with the same keys and Japanese translations as values. No markdown fences, no explanation.
Keep formatting tokens like {{0}}, {{1}}, <b>, </b>, <i>, </i>, etc unchanged.
For proper nouns (character names, place names), use katakana.
Keep translations concise for UI elements.

{json.dumps(texts, ensure_ascii=False)}"""

    prompt_file = WORK_DIR / "csv_prompts" / f"{rel_path.stem}_prompt.txt"
    prompt_file.parent.mkdir(parents=True, exist_ok=True)
    with open(prompt_file, "w", encoding="utf-8") as f:
        f.write(prompt)

    max_retries = 3
    for attempt in range(max_retries):
        try:
            with open(prompt_file, "r", encoding="utf-8") as pf:
                result = subprocess.run(
                    [CLAUDE_CMD, "-p", "--output-format", "json"],
                    stdin=pf,
                    capture_output=True,
                    timeout=300,
                    shell=True
                )

            stdout = result.stdout.decode("utf-8", errors="replace").strip()
            if not stdout:
                print(f"  [WARN] {rel_path} empty response (attempt {attempt + 1})")
                continue

            # Parse response
            response_text = stdout
            try:
                wrapper = json.loads(response_text)
                if isinstance(wrapper, dict) and "result" in wrapper:
                    response_text = wrapper["result"]
            except json.JSONDecodeError:
                pass

            if isinstance(response_text, str):
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0]
                elif "```" in response_text:
                    parts = response_text.split("```")
                    if len(parts) >= 3:
                        response_text = parts[1]
                translated = json.loads(response_text.strip())
            else:
                translated = response_text

            # CSV書き出し
            with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(header)
                for row in rows:
                    key = row[0]
                    if key in translated and translated[key]:
                        new_row = list(row)
                        new_row[1] = translated[key]
                        writer.writerow(new_row)
                    else:
                        writer.writerow(row)

            print(f"  [OK] {rel_path}: {len(translated)}/{len(texts)} translated")
            return True

        except subprocess.TimeoutExpired:
            print(f"  [TIMEOUT] {rel_path} (attempt {attempt + 1})")
        except json.JSONDecodeError as e:
            print(f"  [JSON ERR] {rel_path} (attempt {attempt + 1}): {e}")
            debug_file = WORK_DIR / "csv_prompts" / f"{rel_path.stem}_raw.txt"
            with open(debug_file, "w", encoding="utf-8") as f:
                f.write(response_text if isinstance(response_text, str) else str(response_text))
        except Exception as e:
            print(f"  [ERR] {rel_path} (attempt {attempt + 1}): {e}")

        time.sleep(2)

    print(f"  [FAIL] {rel_path}: all retries exhausted")
    return False


def install_translations():
    """翻訳済みCSVをゲームフォルダにコピー"""
    count = 0
    for csv_file in OUTPUT_DIR.rglob("*.csv"):
        rel_path = csv_file.relative_to(OUTPUT_DIR)
        dest = TEXT_DIR / rel_path
        import shutil
        shutil.copy2(csv_file, dest)
        count += 1
    print(f"\nInstalled {count} translated CSV files to game folder")


def main():
    print("=== Titan Quest 2 CSV直接翻訳 ===\n")

    csv_files = collect_csv_files()
    print(f"Found {len(csv_files)} CSV files\n")

    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"Translating with {MAX_WORKERS} parallel workers...\n")

    success = 0
    fail = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(translate_csv_file, f): f for f in csv_files}
        for future in as_completed(futures):
            if future.result():
                success += 1
            else:
                fail += 1

    print(f"\nTranslation complete: {success} OK, {fail} failed")

    if fail == 0:
        print("\nInstalling to game folder...")
        install_translations()
    else:
        print(f"\n{fail} files failed. Fix and re-run, or install manually.")
        print("To install anyway, run: python translate_csv.py --install")

    if len(sys.argv) > 1 and sys.argv[1] == "--install":
        install_translations()


if __name__ == "__main__":
    main()
