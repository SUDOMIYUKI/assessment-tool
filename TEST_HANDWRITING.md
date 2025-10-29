# 手書きシート + OCR機能 テスト手順

## ✅ 手書きシート生成テスト - 成功！

ファイルが正しく生成されました：
```
output/手書き支援シート_1ページ版.docx (38KB)
```

## 🚀 次のテスト手順

### オプション1: アプリを起動してUIをテスト

```bash
python main.py
```

**テスト手順：**
1. アプリが起動
2. 「ファイル」メニューをクリック
3. 「📝 手書きシートを生成」をクリック
4. 保存先を選択（新しいファイル名で）
5. 生成されたWordファイルを開く
6. 確認：全セクションが正しく表示されているか

### オプション2: OCR機能のテスト（サンプル画像付き）

#### ステップ1: Wordファイルを開く
- `output/手書き支援シート_1ページ版.docx`を開く
- サンプルデータを記入

#### ステップ2: 写真を撮影
- スマホまたはカメラで撮影
- 明るい場所で真上から撮影

#### ステップ3: OCR読み取りをテスト
```bash
# Pythonで直接OCRをテスト
python test_ocr_simple.py
```

## 📋 簡単なOCRテストスクリプト

以下を実行：

```python
# test_ocr_simple.py
from src.utils.ocr_processor import OCRProcessor
from pathlib import Path

processor = OCRProcessor()

# テスト用画像パスを指定
image_path = 'test_image.jpg'

if Path(image_path).exists():
    print("🔍 OCR処理を開始...")
    text, confidence = processor.extract_text_from_image(image_path)
    
    print(f"\n📊 信頼度: {confidence:.1f}%")
    print(f"\n📝 抽出されたテキスト:\n{text}")
    
    # データ解析
    data = processor.parse_handwriting_sheet(text)
    
    print(f"\n✅ 解析完了!")
    print(f"児童氏名: {data.get('child_name', '未検出')}")
    print(f"学校名: {data.get('school_name', '未検出')}")
else:
    print(f"❌ 画像ファイルが見つかりません: {image_path}")
    print("\n手順:")
    print("1. Wordファイルを印刷または手書き記入")
    print("2. 写真を撮影して test_image.jpg として保存")
    print("3. このスクリプトを再実行")
```

## 🎯 テスト項目チェックリスト

### ✅ テスト完了項目
- [x] 手書きシート生成機能
- [x] ファイル保存機能

### ⏳ テスト待ち項目
- [ ] アプリUIからの手書きシート生成
- [ ] OCR読み取り機能
- [ ] PhotoInputFormの表示
- [ ] データ確認・修正機能
- [ ] アセスメントシート自動生成

## 🧪 クイックテスト

### アプリを起動するだけ

最も簡単なテスト方法：

```bash
python main.py
```

**動作確認：**
1. アプリが起動する
2. 3つのボタンが表示される
3. 「⚡ スマート面談記録」で入力フォームが開く
4. 「📝 手書きシートを生成」メニューが表示される（ファイルメニュー）
5. 「📷 写真から読み取り」メニューが表示される（ファイルメニュー）

## 💡 トラブル時の確認

### エラーが出る場合

1. **Importエラー**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Tesseractエラー**:
   - Tesseractがインストールされているか確認
   - 日本語データパックがインストールされているか確認

3. **ファイルが見つからない**:
   - `output`フォルダが存在するか確認
   - パスの確認

## 🎉 成功時の次のステップ

テストが成功したら：
1. 実際の手書きデータでさらにテスト
2. OCR精度を改善（画像前処理の調整）
3. ユーザーフィードバックを収集
4. 本番環境で使用開始
