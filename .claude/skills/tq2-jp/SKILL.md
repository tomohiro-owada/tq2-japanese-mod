---
name: tq2-jp
description: Titan Quest 2の日本語化MODを作成・更新する。ゲームのCSVテキストを翻訳してゲームフォルダに適用する。
disable-model-invocation: true
argument-hint: [translate|restore|check]
---

# Titan Quest 2 日本語化スキル

Titan Quest IIのゲーム内テキストを日本語に翻訳するMODを作成・管理する。

## パス定義

- ゲームテキスト: `C:\Program Files (x86)\Steam\steamapps\common\Titan Quest II\TQ2\Content\TQ2\Data\Text\`
- 作業ディレクトリ: `C:\Users\abalol\tq2_jp_mod\`
- バックアップ: `C:\Users\abalol\tq2_jp_mod\backup_text\`
- 翻訳済みCSV: `C:\Users\abalol\tq2_jp_mod\translated_csv\`
- 翻訳スクリプト: `C:\Users\abalol\tq2_jp_mod\translate_csv.py`

## TQ2のローカライズ仕組み

TQ2はlocresではなく、ゲームフォルダ内のCSVファイル（`TQ2/Content/TQ2/Data/Text/`）でテキスト管理している。
CSVの構造は `Key, SourceString, DevComment`。`SourceString`列を日本語に書き換えることで日本語化できる。
言語設定はEnglishのまま使用する。

## コマンド

### `$ARGUMENTS` が `translate` または空の場合

1. ゲームの `Text/` フォルダのバックアップがなければ取る
2. `translate_csv.py` を実行して全CSVを翻訳（claude -p 5並列）
3. 翻訳済みCSVをゲームフォルダに自動インストール
4. 完了を報告

### `$ARGUMENTS` が `restore` の場合

`backup_text/` からゲームフォルダの `Text/` にCSVを復元して英語に戻す。

### `$ARGUMENTS` が `check` の場合

現在のゲームフォルダのCSVが日本語化されているか確認する。いくつかのCSVをサンプルで読んで状態を報告する。

### `$ARGUMENTS` が `update` の場合

ゲームアップデート後の差分翻訳を行う：
1. バックアップと現在のゲームCSVを比較して差分を検出
2. 新規・変更された行だけを翻訳
3. 翻訳済みCSVにマージしてゲームフォルダに適用

## 翻訳ルール

- 固有名詞（キャラクター名、地名）はカタカナ
- ゲーム用語は統一する（Damage=ダメージ, Health=体力, Energy=エネルギー, Armor=防御力, Resistance=耐性）
- フォーマットトークン（{0}, {1}, <b>, </b>等）はそのまま維持
- UI要素の翻訳は簡潔にする
