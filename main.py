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
        ).pack(pady=50)
        
        # スマートモードボタン
        smart_btn = tk.Button(
            selection_frame,
            text="⚡ スマート面談記録\n\n面談しながらチェックするだけ\nアセスメント・報告書が即完成\nオフライン動作",
            font=("游ゴシック", 12, "bold"),
            bg="#7ED321",
            fg="white",
            width=40,
            height=6,
            command=lambda: self.start_mode(selection_frame, "smart")
        )
        smart_btn.pack(pady=10)
        
        # 支援員管理ボタン
        staff_btn = tk.Button(
            selection_frame,
            text="👥 支援員管理\n\n支援員の登録・編集・検索\n面談記録で条件に合う支援員を自動検索",
            font=("游ゴシック", 12, "bold"),
            bg="#9b59b6",
            fg="white",
            width=40,
            height=6,
            command=self.open_staff_manager
        )
        staff_btn.pack(pady=10)
        
        # 使い方ボタン
        help_btn = tk.Button(
            selection_frame,
            text="❓ 使い方\n\nアプリの使い方を確認\nバージョン情報を表示",
            font=("游ゴシック", 12, "bold"),
            bg="#e67e22",
            fg="white",
            width=40,
            height=6,
            command=self.show_help
        )
        help_btn.pack(pady=10)

    def start_mode(self, selection_frame, mode):
        """スマートモードで開始"""
        selection_frame.destroy()
        
        from src.ui.smart_input_form import SmartInputForm
        self.smart_form = SmartInputForm(self, self.on_smart_complete)
        self.smart_form.pack(fill="both", expand=True)


    def new_smart_interview(self):
        """スマートモードで新規面談"""
        if hasattr(self, 'input_form'):
            self.input_form.destroy()
        if hasattr(self, 'smart_form'):
            self.smart_form.destroy()
        
        from src.ui.smart_input_form import SmartInputForm
        self.smart_form = SmartInputForm(self, self.on_smart_complete)
        self.smart_form.pack(fill="both", expand=True)
    
    
    def on_smart_complete(self, interview_data, assessment_data):
        """スマートモード完了処理"""
        # データ保存
        self.history_manager.save_interview(interview_data, assessment_data)
        
        # プレビュー表示
        analysis_result = {
            'assessment_data': assessment_data,
            'report_text': '',
            'missing_info': []
        }
        self.show_preview(analysis_result, interview_data)
    
    def show_preview(self, analysis_result, interview_data):
        """プレビュー表示"""
        from src.ui.preview_window import PreviewWindow
        
        preview = PreviewWindow(self, analysis_result, interview_data)
        preview.wait_window()
    
    def show_help(self):
        help_text = """【使い方】

1. 「⚡ スマート面談記録」をクリック
2. 面談しながらチェックボックスを選択
3. 支援員を検索・選択（オプション）
4. 「アセスメントシートを生成」をクリック
5. Excelファイルが自動生成されます

【特徴】
・面談しながらチェックするだけ
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

【基本的な使い方】
1. 「⚡ スマート面談記録」をクリック
2. 面談しながらチェックボックスを選択
3. 支援員を検索・選択（オプション）
4. 「アセスメントシートを生成」をクリック
5. Excelファイルが自動生成されます

【特徴】
・面談しながらチェックするだけ
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


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()

