# Titan Quest 2 日本語化MOD

## 概要
Titan Quest IIのゲーム内テキストを日本語に翻訳するMOD。
TQ2はゲームフォルダ内のCSVファイルでテキスト管理しているため、CSVのSourceString列を直接日本語に書き換える方式。

## ファイル構成
- `translate_csv.py` — 翻訳スクリプト（claude -p 5並列）
- `translated_csv/` — 翻訳済みCSVファイル（82ファイル）
- `backup_text/` — 元の英語CSVバックアップ

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

## 補足
- ゲームログ（`AppData/Local/TQ2/Saved/Logs/TQ2.log`）の `LogCSLocTools` でCSVの読み込みを確認できる
- TQ2はlocresではなくCSVベースのローカライズのため、locresやlocmetaの編集は不要
