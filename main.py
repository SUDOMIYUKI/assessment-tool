import tkinter as tk
from tkinter import messagebox
import sys
from pathlib import Path
import threading
import time
import os

sys.path.insert(0, str(Path(__file__).parent))

from src.ui.staff_manager import StaffManagerDialog
from src.database.models import Database
from src.database.history import HistoryManager

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("不登校支援 - 初回アセスメント支援ツール")
        self.geometry("1000x800")
        
        # Dropbox同期状態を確認
        self.check_dropbox_sync()
        
        # バージョンチェック（起動時のみ、非同期）
        if getattr(sys, 'frozen', False):  # 実行ファイルの場合のみ
            threading.Thread(target=self.check_for_updates, daemon=True).start()
        
        self.db = Database()
        self.history_manager = HistoryManager()
        
        self.create_widgets()
    
    def check_dropbox_sync(self):
        """Dropboxの同期状態を確認"""
        try:
            import config
            if not config.USE_DROPBOX:
                return
            
            db_path = config.DATABASE_PATH
            
            # Dropboxフォルダ内かチェック
            dropbox_path = config.get_dropbox_path()
            if dropbox_path and str(db_path).startswith(str(dropbox_path)):
                # データベースファイルが存在する場合、同期状態を確認
                if db_path.exists():
                    # ファイルの最終更新時刻を取得
                    local_mtime = db_path.stat().st_mtime
                    current_time = time.time()
                    
                    # 5分以内に更新されていれば同期中と判断
                    if current_time - local_mtime < 300:
                        # データベースがロックされていないか確認
                        if self.is_database_locked(db_path):
                            messagebox.showwarning(
                                "データベースロック",
                                "データベースが他のPCで使用中の可能性があります。\n"
                                "しばらく待ってから再度お試しください。"
                            )
                else:
                    # データベースが存在しない場合は新規作成
                    db_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Dropbox同期チェックエラー: {e}")
    
    def is_database_locked(self, db_path):
        """データベースがロックされているか確認"""
        try:
            import sqlite3
            # 読み取り専用で接続を試みる
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=1.0)
            conn.close()
            return False
        except sqlite3.OperationalError:
            return True
        except Exception:
            return False
    
    def check_for_updates(self):
        """更新をチェック（非同期）"""
        try:
            import config
            if not config.UPDATE_CHECK_ENABLED or not config.UPDATE_SOURCE_PATH:
                return
            
            update_path = config.UPDATE_SOURCE_PATH
            if update_path and update_path.exists():
                # 更新ファイルの更新日時を確認
                update_mtime = update_path.stat().st_mtime
                current_exe = Path(sys.executable)
                
                if current_exe.exists():
                    current_mtime = current_exe.stat().st_mtime
                    
                    # 更新日時が新しい、またはファイルサイズが異なる場合は更新ありと判断
                    update_size = update_path.stat().st_size
                    current_size = current_exe.stat().st_size
                    
                    if (update_mtime > current_mtime) or (update_size != current_size):
                        # 少し待ってから通知（起動直後の処理が落ち着いてから）
                        import time
                        time.sleep(3)
                        # 更新があることを通知（メインスレッドで実行）
                        self.after(0, lambda: self.show_update_notification(update_path))
        except Exception as e:
            print(f"更新チェックエラー: {e}")
    
    def show_update_notification(self, update_path):
        """更新通知を表示"""
        try:
            import config
            version_info = f"Version {config.APP_VERSION}"
        except:
            version_info = ""
        
        result = messagebox.askyesno(
            "更新のお知らせ",
            f"新しいバージョンが利用可能です。\n\n"
            f"{version_info}\n\n"
            f"更新ファイル: {update_path.name}\n\n"
            "今すぐ更新しますか？\n"
            "（アプリを終了し、自動的に更新されます）"
        )
        if result:
            self.perform_update(update_path)
    
    def perform_update(self, update_path):
        """更新を実行"""
        import subprocess
        import shutil
        import tempfile
        
        try:
            current_exe = Path(sys.executable)
            exe_dir = current_exe.parent
            exe_name = current_exe.name
            
            # バックアップパス
            backup_path = exe_dir / f"{current_exe.stem}_old{current_exe.suffix}"
            
            # 一時バッチファイルを作成
            temp_dir = Path(tempfile.gettempdir())
            batch_file = temp_dir / "update_app.bat"
            
            # バッチファイルの内容
            batch_content = f"""@echo off
chcp 65001 > nul
echo 更新を実行しています...
timeout /t 2 /nobreak > nul

REM 現在のexeをバックアップ
if exist "{current_exe}" (
    if exist "{backup_path}" del /f /q "{backup_path}"
    copy /y "{current_exe}" "{backup_path}" > nul
)

REM 更新ファイルをコピー
copy /y "{update_path}" "{current_exe}" > nul

if exist "{current_exe}" (
    echo 更新が完了しました。
    echo アプリを起動します...
    timeout /t 1 /nobreak > nul
    start "" "{current_exe}"
    
    REM バッチファイルを削除
    del /f /q "%~f0"
) else (
    echo 更新に失敗しました。バックアップから復元します...
    if exist "{backup_path}" (
        copy /y "{backup_path}" "{current_exe}" > nul
    )
    pause
    del /f /q "%~f0"
)
"""
            
            # バッチファイルを作成
            with open(batch_file, 'w', encoding='utf-8') as f:
                f.write(batch_content)
            
            # バッチファイルを実行（非同期）
            subprocess.Popen(
                [str(batch_file)],
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            messagebox.showinfo(
                "更新を開始します",
                "アプリを終了して更新を実行します。\n\n"
                "更新が完了すると、自動的にアプリが再起動されます。"
            )
            
            # アプリを終了
            self.quit()
            
        except Exception as e:
            messagebox.showerror(
                "更新エラー",
                f"更新の準備中にエラーが発生しました：\n{str(e)}\n\n"
                f"手動で更新してください：\n{update_path}"
            )
    
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
        ).pack(pady=30)
        
        # 画面入力モードボタン
        smart_btn = tk.Button(
            selection_frame,
            text="⚡ スマート面談\n\n面談しながらチェック\nパソコンで直接入力\nアセスメントが即完成",
            font=("游ゴシック", 12, "bold"),
            bg="#7ED321",
            fg="white",
            width=40,
            height=5,
            command=lambda: self.start_mode(selection_frame, "smart")
        )
        smart_btn.pack(pady=8)
        
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
    

    def show_help(self):
        """使い方を表示"""
        help_text = """
不登校支援 - 初回アセスメント支援ツール

【スマート面談モード】

1. 「⚡ スマート面談」をクリック
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
        try:
            import config
            version = config.APP_VERSION
        except:
            version = "1.1.0"
        
        about_text = f"""
不登校支援 - 初回アセスメント支援ツール
Version {version}

【主な機能】
・データベースをDropboxで共有
・自動マイグレーション対応
・起動時に同期状態を確認

美幸AIスクール
        """
        messagebox.showinfo("バージョン情報", about_text)


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()

