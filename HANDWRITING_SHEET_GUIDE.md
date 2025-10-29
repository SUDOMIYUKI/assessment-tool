# 手書きシート + OCR機能 実装ガイド

## 📋 概要

このシステムは、手書き支援シートを写真で撮影し、OCRで読み取ってデータ入力を自動化する機能です。

## 🗂️ ファイル構成

```
project/
├── src/
│   ├── utils/
│   │   ├── handwriting_sheet_generator.py  # Word手書きシート生成
│   │   ├── ocr_processor.py                # OCR処理（改善版）
│   │   └── assessment_data_builder.py      # データ変換ヘルパー
│   └── ui/
│       └── photo_input_form.py             # OCRデータ確認・修正フォーム
├── templates/
│   └── （既存のExcelテンプレート）
└── output/
    └── （生成されたファイル）
```

## 📥 ファイル配置手順

### 1. 既存プロジェクトへのファイル配置

以下のファイルを対応するディレクトリに配置してください：

```bash
# 手書きシート生成
src/utils/handwriting_sheet_generator.py

# OCR処理（改善版）
src/utils/ocr_processor.py

# データ変換ヘルパー
src/utils/assessment_data_builder.py

# OCRデータ確認フォーム
src/ui/photo_input_form.py
```

### 2. 依存パッケージのインストール

`requirements.txt`に以下を追加（既にある場合はスキップ）：

```
pytesseract>=0.3.10
Pillow>=10.0.0
opencv-python>=4.8.0
python-docx>=1.1.0
```

インストール：
```bash
pip install -r requirements.txt
```

### 3. Tesseractのインストール

#### Windows:
1. [Tesseract公式サイト](https://github.com/UB-Mannheim/tesseract/wiki)からインストーラーをダウンロード
2. インストール時に「Japanese」言語パックを選択
3. 環境変数`PATH`に`C:\Program Files\Tesseract-OCR`を追加

#### Mac:
```bash
brew install tesseract tesseract-lang
```

#### Linux:
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-jpn
```

## 🚀 使い方

### ステップ1: 手書きシートを生成

メインアプリケーションの「ファイル」メニューから：
1. 「📝 手書きシートを生成」をクリック
2. 保存先を選択
3. Wordファイルが生成される

### ステップ2: 手書きで記入

1. 生成されたWordファイルを印刷
2. 手書きで記入（チェックボックスは`■`または`✓`でマーク）
3. スマホやスキャナーで写真撮影

### ステップ3: 写真から読み取り

メインアプリケーションの「ファイル」メニューから：
1. 「📷 写真から読み取り」をクリック
2. 撮影した画像を選択
3. OCR処理が自動実行される
4. 確認画面が表示される

### ステップ4: データ確認・修正

1. 黄色ハイライトされた項目を重点的に確認
2. 必要に応じて手動修正
3. 「確認完了・データを保存」ボタンをクリック

### ステップ5: アセスメントシート生成

1. プレビュー画面が表示される
2. 「Excelに出力」ボタンでアセスメントシートを生成

## ⚙️ main.pyへの統合

既存の`main.py`の`import_from_photo()`メソッドは以下のように実装されています：

```python
def import_from_photo(self):
    """写真から読み取り"""
    try:
        from tkinter import filedialog
        from src.utils.ocr_processor import OCRProcessor
        from src.ui.photo_input_form import PhotoInputForm
        
        # 画像ファイルを選択
        image_path = filedialog.askopenfilename(
            title="手書きシートの写真を選択",
            filetypes=[
                ("画像ファイル", "*.jpg *.jpeg *.png *.bmp"),
                ("すべてのファイル", "*.*")
            ]
        )
        
        if not image_path:
            return
        
        # OCR処理
        messagebox.showinfo("処理中", "写真から読み取っています...")
        
        processor = OCRProcessor()
        text, confidence = processor.extract_text_from_image(image_path)
        
        if not text.strip():
            messagebox.showwarning("警告", "写真からテキストを読み取れませんでした。")
            return
        
        # データを解析
        data = processor.parse_handwriting_sheet(text)
        
        # 入力フォームを開いてデータを設定
        photo_form = PhotoInputForm(self, data, confidence)
        photo_form.wait_window()
        
    except Exception as e:
        messagebox.showerror("エラー", f"写真読み取りに失敗しました:\n{str(e)}")
        import traceback
        traceback.print_exc()
```

## 🎯 機能詳細

### 手書きシート生成（handwriting_sheet_generator.py）

**特徴:**
- 1ページA4サイズに全項目を凝縮
- 2カラムレイアウト
- ジェノグラム記入欄
- OCR認識に最適化されたレイアウト

**生成される内容:**
- 基本情報（上部バー）
- 家族関係・ジェノグラム
- 登校状況
- 生活状況
- 学習状況
- 対人関係
- 発達特性・医療情報
- 家庭環境
- ニーズ・目標（短期・長期）
- 支援への希望
- 当日の様子・メモ

### OCR処理（ocr_processor.py）

**画像前処理:**
- グレースケール化
- ノイズ除去（fastNlMeansDenoising）
- コントラスト調整（CLAHE）
- 二値化（Otsu's法）
- シャープネス強化

**チェックボックス認識:**
- チェック済み: `■`, `☑`, `✓`, `✔`, `×`, `レ`
- 未チェック: `□`, `口`

**信頼度スコア:**
- Tesseractの信頼度データを活用
- 平均信頼度を計算
- 低信頼度項目のハイライト表示

### データ確認フォーム（photo_input_form.py）

**特徴:**
- 全項目を網羅したスクロール可能なフォーム
- 信頼度表示（ヘッダー）
- 低信頼度項目の黄色ハイライト
- チェックボックス、ラジオボタン、テキストフィールド
- smart_input_form.pyと同じデータ形式

**セクション:**
1. 基本情報
2. 家族関係・ジェノグラム
3. 登校状況
4. 生活状況
5. 学習状況
6. 対人関係
7. 発達特性・医療情報
8. 家庭環境
9. ニーズ・目標
10. 支援への希望
11. 当日の様子

## 🔧 トラブルシューティング

### OCRで日本語が認識されない

**原因:** Tesseractの日本語言語パックがインストールされていない

**解決策:**
```bash
# Windows: インストーラーで日本語を選択
# Mac:
brew install tesseract-lang
# Linux:
sudo apt-get install tesseract-ocr-jpn
```

### 画像認識精度が低い

**対策:**
1. 明るい場所で撮影
2. 真上から撮影（斜めにならないように）
3. 影が入らないように注意
4. 高解像度で撮影
5. 手書き文字を大きく、はっきりと書く

### チェックボックスが認識されない

**対策:**
1. チェックボックスは`■`または`✓`で明確にマーク
2. 薄い鉛筆ではなく、濃いペンを使用
3. チェックマークを大きく書く

### モジュールが見つからない

**エラー:** `ModuleNotFoundError: No module named 'cv2'`

**解決策:**
```bash
pip install opencv-python
```

## 📊 パフォーマンス

**想定処理時間:**
- 手書きシート生成: 1秒以内
- OCR処理（画像前処理込み）: 5-10秒
- データ確認・修正: ユーザー操作次第

**推奨環境:**
- CPU: 2コア以上
- RAM: 4GB以上
- ストレージ: 100MB以上の空き容量

## 🎉 完成！

これで手書きシート + OCR機能の実装が完了しました。

ワークフローは以下の通りです：
1. 手書きシート生成 → 印刷
2. 手書き記入
3. 写真撮影
4. OCR読み取り
5. データ確認・修正
6. アセスメントシート自動生成

**質問や問題がある場合は、お気軽にお問い合わせください！**

