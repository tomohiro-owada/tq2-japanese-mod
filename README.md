# Titan Quest 2 日本語化MOD

## 概要
Titan Quest IIのゲーム内テキストを日本語に翻訳するMOD。
TQ2はゲームフォルダ内のCSVファイルでテキスト管理しているため、CSVのSourceString列を直接日本語に書き換える方式。

## ファイル構成
- `translate_csv.py` — 翻訳スクリプト（claude -p 5並列）
- `.claude/skills/tq2-jp/SKILL.md` — Claude Codeスキル（スラッシュコマンド）
- `translated_csv/` — 翻訳済みCSVファイル（82ファイル、gitignore対象）
- `backup_text/` — 元の英語CSVバックアップ（gitignore対象）

## 手順

### 1. 元テキストのバックアップ
以下のフォルダを丸ごとコピーして保存する。

```
Titan Quest II/TQ2/Content/TQ2/Data/Text/
```

82個のCSVファイル（約7,800行）が入っている。

### 2. CSVの翻訳
各CSVの構造は `Key, SourceString, DevComment`。`SourceString`列を日本語に置き換える。

```bash
python translate_csv.py
```

`claude -p`を5並列で呼び出し、JSON形式で翻訳してCSVに書き戻す。
翻訳済みファイルは `translated_csv/` に出力され、完了後自動でゲームフォルダに上書きコピーされる。

### 3. ゲーム起動
言語設定は **English** のまま起動する。CSVを直接書き換えているのでそのまま日本語が表示される。

## 元に戻す方法
`backup_text/Text/` の中身を `Titan Quest II/TQ2/Content/TQ2/Data/Text/` に上書きコピーする。

## Claude Codeスキル

このリポジトリにはClaude Code用のスラッシュコマンドが含まれている。

| コマンド | 説明 |
|---------|------|
| `/tq2-jp` | 全CSVを翻訳してゲームに適用 |
| `/tq2-jp restore` | 英語に戻す |
| `/tq2-jp check` | 日本語化の状態を確認 |
| `/tq2-jp update` | ゲームアプデ後の差分翻訳 |

## 前提条件
- [Claude Code](https://claude.ai/claude-code) がインストール済みであること
- Python 3.10+

## 補足
- ゲームログ（`AppData/Local/TQ2/Saved/Logs/TQ2.log`）の `LogCSLocTools` でCSVの読み込みを確認できる
- TQ2はlocresではなくCSVベースのローカライズのため、locresやlocmetaの編集は不要
