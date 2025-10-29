import tkinter as tk
from tkinter import messagebox
import sys
from pathlib import Path
import threading

sys.path.insert(0, str(Path(__file__).parent))

from src.ui.staff_manager import StaffManagerDialog
from src.database.models import Database
from src.database.history import HistoryManager

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("不登校支援 - 初回アセスメント支援ツール")
        self.geometry("1000x800")
        
        self.db = Database()
        self.history_manager = HistoryManager()
        
        self.create_widgets()
    
    def create_widgets(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ファイル", menu=file_menu)
        file_menu.add_command(label="⚡ 新規面談記録", command=self.new_smart_interview)
        file_menu.add_separator()
        file_menu.add_command(label="📝 手書きシートを生成", command=self.generate_handwriting_sheet)
        file_menu.add_command(label="📷 写真から読み取り", command=self.import_from_photo)
        file_menu.add_separator()
        file_menu.add_command(label="終了", command=self.quit)
        
        # 管理メニュー
        manage_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="管理", menu=manage_menu)
        manage_menu.add_command(label="支援員管理", command=self.open_staff_manager)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ヘルプ", menu=help_menu)
        help_menu.add_command(label="使い方", command=self.show_help)
        help_menu.add_command(label="バージョン情報", command=self.show_about)
        
        # 初期画面（選択ダイアログ）
        self.show_mode_selection()
    
    def show_mode_selection(self):
        """起動時にモード選択画面を表示"""
        selection_frame = tk.Frame(self)
        selection_frame.pack(fill="both", expand=True)
        
        tk.Label(
            selection_frame,
            text="面談記録の入力方法を選択してください",
            font=("游ゴシック", 16, "bold")
        ).pack(pady=30)
        
        # 画面入力モードボタン
        smart_btn = tk.Button(
            selection_frame,
            text="⚡ 画面入力モード\n\n面談しながらチェック\nパソコンで直接入力\nアセスメントが即完成",
            font=("游ゴシック", 12, "bold"),
            bg="#7ED321",
            fg="white",
            width=40,
            height=5,
            command=lambda: self.start_mode(selection_frame, "smart")
        )
        smart_btn.pack(pady=8)
        
        # 写真読み取りモードボタン
        photo_btn = tk.Button(
            selection_frame,
            text="📷 写真読み取りモード\n\n手書きシートを撮影\n写真から自動入力\nOCRで読み取り",
            font=("游ゴシック", 12, "bold"),
            bg="#3498db",
            fg="white",
            width=40,
            height=5,
            command=self.import_from_photo
        )
        photo_btn.pack(pady=8)
        
        # 支援員管理ボタン
        staff_btn = tk.Button(
            selection_frame,
            text="👥 支援員管理\n\n支援員の登録・編集・検索\n面談記録で条件に合う支援員を自動検索",
            font=("游ゴシック", 12, "bold"),
            bg="#9b59b6",
            fg="white",
            width=40,
            height=5,
            command=self.open_staff_manager
        )
        staff_btn.pack(pady=8)
        
        # 使い方ボタン
        help_btn = tk.Button(
            selection_frame,
            text="❓ 使い方\n\nアプリの使い方を確認\nバージョン情報を表示",
            font=("游ゴシック", 12, "bold"),
            bg="#e67e22",
            fg="white",
            width=40,
            height=5,
            command=self.show_help
        )
        help_btn.pack(pady=8)

    def start_mode(self, selection_frame, mode):
        """スマートモードで開始"""
        from src.ui.smart_input_form import SmartInputForm
        self.smart_form = SmartInputForm(self, self.on_smart_complete)
        # ウィンドウが閉じられるまで待機
        self.smart_form.wait_window()


    def new_smart_interview(self):
        """スマートモードで新規面談"""
        from src.ui.smart_input_form import SmartInputForm
        self.smart_form = SmartInputForm(self, self.on_smart_complete)
        # ウィンドウが閉じられるまで待機
        self.smart_form.wait_window()
    
    
    def on_smart_complete(self, interview_data, assessment_data):
        """スマートモード完了処理"""
        # データ保存
        self.history_manager.save_interview(interview_data, assessment_data)
        
        # 新規ケースを未割り当てケースとして登録
        self.save_to_unassigned_cases(interview_data)
        
        # プレビュー表示
        analysis_result = {
            'assessment_data': assessment_data,
            'report_text': '',
            'missing_info': []
        }
        self.show_preview(analysis_result, interview_data)
    
    def save_to_unassigned_cases(self, interview_data):
        """面談データを未割り当てケースとして保存"""
        try:
            from src.database.staff import StaffManager
            staff_manager = StaffManager()
            
            # ケース番号を生成（児童イニシャル + 面談日）
            case_number = interview_data.get('児童イニシャル', 'XX') + '_' + interview_data['面談実施日'].strftime('%Y%m%d')
            
            # 支援希望から情報を取得
            support_wishes = interview_data.get('支援希望', {})
            
            case_data = {
                'case_number': case_number,
                'district': interview_data.get('学校名', ''),
                'child_name': interview_data.get('児童氏名', ''),
                'child_age': interview_data.get('学年', None),
                'child_gender': interview_data.get('性別', ''),
                'preferred_day': support_wishes.get('希望の曜日', ''),
                'preferred_time': support_wishes.get('希望の時間帯', ''),
                'frequency': '未設定',
                'location': support_wishes.get('希望の場所', ''),
                'notes': support_wishes.get('解決したいこと', ''),
                'status': '未割り当て'
            }
            
            # 未割り当てケースとして登録
            staff_manager.add_unassigned_case(case_data)
            
        except Exception as e:
            print(f"未割り当てケース登録エラー: {e}")
    
    def show_preview(self, analysis_result, interview_data):
        """プレビュー表示"""
        from src.ui.preview_window import PreviewWindow
        
        preview = PreviewWindow(self, analysis_result, interview_data)
        preview.wait_window()
    
    def show_help(self):
        help_text = """【使い方 - 2つの入力モード】

📱 画面入力モード（パソコン入力）
1. 「⚡ 画面入力モード」をクリック
2. 面談しながらチェックボックスを選択
3. 支援員を検索・選択（オプション）
4. 「アセスメントシートを生成」をクリック
5. Excelファイルが自動生成されます

📷 写真読み取りモード（手書きシート）
1. 「📷 写真読み取りモード」をクリック
2. 手書きシートの写真を選択
3. OCRで自動読み取り・確認
4. データを修正して保存
5. アセスメントシートが自動生成されます

【特徴】
・面談しながらチェックするだけ
・手書きシートも対応（OCR読み取り）
・アセスメント・報告書が即完成
・オフライン動作
・支援員検索機能付き

【注意事項】
- インターネット接続不要
- 個人情報はイニシャル化されます
- 支援員情報は管理画面で登録できます"""
        
        messagebox.showinfo("使い方", help_text)
    
    def open_staff_manager(self):
        """支援員管理ダイアログを開く"""
        try:
            from src.ui.staff_manager import StaffManagerDialog
            dialog = StaffManagerDialog(self)
            self.wait_window(dialog)
        except ImportError as e:
            messagebox.showerror("エラー", f"支援員管理機能の読み込みに失敗しました：\n{str(e)}")
        except Exception as e:
            messagebox.showerror("エラー", f"支援員管理の起動中にエラーが発生しました：\n{str(e)}")
    
    def show_about(self):
        messagebox.showinfo(
            "バージョン情報",
            "不登校支援 - 初回アセスメント支援ツール\n"
            "Version 3.0.0 (スマートモード搭載)\n\n"
            "機能：\n"
            "⚡ スマートモード（面談中に即完成・オフライン）\n"
            "🔍 データ活用モード（過去データ活用・オフライン）\n"
            "🤖 AI分析モード（Claude AI・オンライン）\n"
            "👥 支援員管理・選択機能"
        )
    
    

    def open_staff_manager(self):
        """支援員管理ダイアログを開く"""
        try:
            dialog = StaffManagerDialog(self)
            dialog.wait_window()  # ダイアログが閉じるまで待機
        except Exception as e:
            messagebox.showerror("エラー", f"支援員管理の表示中にエラーが発生しました:\n{str(e)}")

    def show_help(self):
        """使い方を表示"""
        help_text = """
不登校支援 - 初回アセスメント支援ツール

【2つの入力モード】

📱 画面入力モード（パソコン入力）
1. 「⚡ 画面入力モード」をクリック
2. 面談しながらチェックボックスを選択
3. 支援員を検索・選択（オプション）
4. 「アセスメントシートを生成」をクリック
5. Excelファイルが自動生成されます

📷 写真読み取りモード（手書きシート）
1. ファイルメニュー → 「📝 手書きシートを生成」
2. Wordファイルを印刷して手書き記入
3. 写真を撮影して「📷 写真読み取りモード」をクリック
4. OCRで自動読み取り・確認
5. アセスメントシートが自動生成されます

【特徴】
・面談しながらチェックするだけ
・手書きシートにも対応（OCR読み取り）
・アセスメント・報告書が即完成
・オフライン動作
・支援員検索機能付き

【支援員管理】
- 支援員の登録・編集・削除ができます
- 地域、年齢、性別、勤務日時で検索可能
- 面談記録で条件に合う支援員を自動検索

【ファイルの保存場所】
- データベース: data/records.db
- 出力ファイル: output/フォルダ

【サポート】
何かご不明な点がございましたら、お気軽にお問い合わせください。
        """
        messagebox.showinfo("使い方", help_text)

    def show_about(self):
        """バージョン情報を表示"""
        about_text = """
不登校支援 - 初回アセスメント支援ツール
Version 1.0

美幸AIスクール
        """
        messagebox.showinfo("バージョン情報", about_text)
    
    def generate_handwriting_sheet(self):
        """手書きシートを生成"""
        try:
            from src.utils.handwriting_sheet_generator import create_handwriting_sheet
            from tkinter import filedialog
            
            # 保存先を選択
            output_path = filedialog.asksaveasfilename(
                title="手書きシートの保存先を選択",
                defaultextension=".docx",
                filetypes=[("Wordファイル", "*.docx"), ("すべてのファイル", "*.*")]
            )
            
            if output_path:
                # 手書きシートを生成
                create_handwriting_sheet(output_path)
                
                messagebox.showinfo(
                    "完了",
                    f"手書きシートを作成しました！\n\n{output_path}\n\n"
                    "次のステップ：\n"
                    "1. Wordでシートを開く\n"
                    "2. 手書きで記入\n"
                    "3. 写真を撮影\n"
                    "4. 「写真から読み取り」で自動入力"
                )
        except Exception as e:
            messagebox.showerror("エラー", f"手書きシートの生成に失敗しました:\n{str(e)}")
    
    def import_from_photo(self):
        """写真から読み取り"""
        try:
            # 必要なライブラリのチェック
            try:
                import pytesseract
                import cv2
                from PIL import Image
            except ImportError as ie:
                missing_module = str(ie).split("'")[1] if "'" in str(ie) else "必要なライブラリ"
                messagebox.showerror(
                    "ライブラリエラー",
                    f"必要なライブラリがインストールされていません。\n\n"
                    f"エラー: {missing_module}\n\n"
                    f"以下のコマンドでインストールしてください：\n"
                    f"pip install pytesseract opencv-python Pillow"
                )
                return
            
            from tkinter import filedialog
            from src.utils.ocr_processor import OCRProcessor
            from src.ui.smart_input_form import SmartInputForm
            
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
            try:
                messagebox.showinfo("処理中", "写真から読み取っています...")
                
                processor = OCRProcessor()
                text, confidence = processor.extract_text_from_image(image_path)
                
                if not text.strip():
                    messagebox.showwarning(
                        "警告", 
                        "写真からテキストを読み取れませんでした。\n\n"
                        "対処方法：\n"
                        "1. 写真が鮮明であることを確認\n"
                        "2. 明るい場所で撮影\n"
                        "3. 手書き文字が濃く、はっきり書かれているか確認"
                    )
                    return
                
                # データを解析
                data = processor.parse_handwriting_sheet(text)
                
                if not data:
                    messagebox.showwarning("警告", "データを正しく読み取れませんでした。")
                    return
                
                # 入力フォームを開いてデータを設定
                from src.ui.photo_input_form import PhotoInputForm
                photo_form = PhotoInputForm(self, data, confidence)
                
                # OCRデータを保存するための参照を渡す
                photo_form.parent_app = self
                
                photo_form.wait_window()
                
            except FileNotFoundError:
                messagebox.showerror(
                    "Tesseract OCR未インストール",
                    "Tesseract OCRがインストールされていません。\n\n"
                    "【インストール手順】\n"
                    "1. 下記URLからダウンロード:\n"
                    "   https://github.com/UB-Mannheim/tesseract/wiki\n\n"
                    "2. インストール時に「Additional language data」で\n"
                    "   「Japanese」にチェックを入れてください\n\n"
                    "3. インストール後、アプリを再起動してください"
                )
            except Exception as ocr_error:
                messagebox.showerror(
                    "OCRエラー",
                    f"OCR処理中にエラーが発生しました：\n\n{str(ocr_error)}\n\n"
                    "【対処方法】\n"
                    "1. Tesseractが正しくインストールされているか確認\n"
                    "2. 写真が鮮明で文字がはっきり見えるか確認\n"
                    "3. 明るい場所で撮影された写真か確認"
                )
                import traceback
                traceback.print_exc()
            
        except Exception as e:
            messagebox.showerror("エラー", f"写真読み取りに失敗しました:\n{str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()

