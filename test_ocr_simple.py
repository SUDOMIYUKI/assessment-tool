"""
簡単なOCRテストスクリプト
- 画像ファイルを選択してOCR処理をテスト
- 結果をターミナルに表示
"""

import sys
from pathlib import Path
from tkinter import filedialog, messagebox
import tkinter as tk

def test_ocr():
    """OCR機能をテスト"""
    
    # ルートウィンドウを作成（非表示）
    root = tk.Tk()
    root.withdraw()
    
    print("=" * 60)
    print("🧪 手書きシート OCR機能テスト")
    print("=" * 60)
    print()
    
    # 画像ファイルを選択
    image_path = filedialog.askopenfilename(
        title="手書きシートの写真を選択",
        filetypes=[
            ("画像ファイル", "*.jpg *.jpeg *.png *.bmp"),
            ("すべてのファイル", "*.*")
        ]
    )
    
    if not image_path:
        print("❌ 画像が選択されませんでした")
        return
    
    print(f"📁 選択されたファイル: {image_path}")
    print()
    
    try:
        # OCR処理をインポート
        from src.utils.ocr_processor import OCRProcessor
        
        print("🔍 OCR処理を開始...")
        processor = OCRProcessor()
        
        # テキスト抽出
        text, confidence = processor.extract_text_from_image(image_path)
        
        print()
        print("=" * 60)
        print("📊 結果")
        print("=" * 60)
        print(f"信頼度: {confidence:.1f}%")
        print()
        
        # 抽出されたテキストを表示
        print("📝 抽出されたテキスト（最初の500文字）:")
        print("-" * 60)
        print(text[:500])
        if len(text) > 500:
            print("...（省略）...")
        print()
        
        # データ解析
        print("🔧 データ解析中...")
        print("-" * 60)
        
        data = processor.parse_handwriting_sheet(text)
        
        print()
        print("=" * 60)
        print("✅ 解析結果")
        print("=" * 60)
        
        # 基本情報
        if data.get('child_name'):
            print(f"✓ 児童氏名: {data['child_name']}")
        if data.get('guardian_name'):
            print(f"✓ 保護者氏名: {data['guardian_name']}")
        if data.get('school_name'):
            print(f"✓ 学校名: {data['school_name']}")
        if data.get('grade'):
            print(f"✓ 学年: {data['grade']}")
        if data.get('gender'):
            print(f"✓ 性別: {data['gender']}")
        
        # 登校状況
        attendance = data.get('attendance', {})
        if attendance:
            print(f"✓ 登校頻度: {attendance.get('frequency', '未検出')}")
            if attendance.get('truancy'):
                print(f"✓ 不登校該当: はい")
        
        # 課題
        if data.get('life_rhythm'):
            print(f"✓ 生活リズム課題: {', '.join(data['life_rhythm'])}")
        if data.get('study_issues'):
            print(f"✓ 学習課題: {', '.join(data['study_issues'])}")
        
        print()
        print("=" * 60)
        print("✨ テスト完了！")
        print("=" * 60)
        
        # 結果の確認
        result = messagebox.askyesno(
            "テスト完了",
            f"OCR処理が完了しました。\n\n"
            f"信頼度: {confidence:.1f}%\n\n"
            f"結果を確認しますか？"
        )
        
        if result:
            # 詳細を表示
            import json
            print("\n📋 完全な解析データ:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ エラーが発生しました")
        print("=" * 60)
        print(f"エラー内容: {str(e)}")
        print()
        import traceback
        traceback.print_exc()
        
        messagebox.showerror("エラー", f"OCR処理中にエラーが発生しました:\n{str(e)}")

if __name__ == '__main__':
    test_ocr()

