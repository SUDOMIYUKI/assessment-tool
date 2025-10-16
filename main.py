import tkinter as tk
from tkinter import messagebox
import sys
from pathlib import Path
import threading

sys.path.insert(0, str(Path(__file__).parent))

from src.ui.input_form import InputForm
from src.ui.preview_window import PreviewWindow
from src.ui.mode_selector import ModeSelectorDialog
from src.ui.quick_mode_dialog import QuickModeDialog
from src.ui.data_mode_dialog import DataModeDialog
from src.ai.analyzer import AIAnalyzer
from src.ai.quick_mode import QuickModeAnalyzer
from src.ai.privacy import PrivacyProtector
from src.database.models import Database
from src.database.templates import TemplateManager
from src.database.history import HistoryManager
from config import CLAUDE_API_KEY

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("不登校支援 - 初回アセスメント支援ツール")
        self.geometry("1000x800")
        
        if not CLAUDE_API_KEY:
            messagebox.showerror(
                "エラー",
                "Claude APIキーが設定されていません。\n\n"
                ".envファイルを作成し、以下の内容を記載してください：\n"
                "CLAUDE_API_KEY=your_api_key_here"
            )
            self.quit()
            return
        
        self.analyzer = AIAnalyzer(CLAUDE_API_KEY)
        self.quick_analyzer = QuickModeAnalyzer()
        self.privacy = PrivacyProtector()
        self.db = Database()
        self.template_manager = TemplateManager()
        self.history_manager = HistoryManager()
        
        self.create_widgets()
    
    def create_widgets(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ファイル", menu=file_menu)
        file_menu.add_command(label="新規面談（従来版）", command=self.new_interview)
        file_menu.add_command(label="⚡ 新規面談（スマートモード）", command=self.new_smart_interview)
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
            text="⚡ スマートモード（推奨）\n\n面談しながらチェックするだけ\nアセスメント・報告書が即完成\nオフライン動作",
            font=("游ゴシック", 12, "bold"),
            bg="#7ED321",
            fg="white",
            width=40,
            height=6,
            command=lambda: self.start_mode(selection_frame, "smart")
        )
        smart_btn.pack(pady=10)
        
        # 従来モードボタン
        traditional_btn = tk.Button(
            selection_frame,
            text="📝 従来モード\n\n自由記述で面談メモ作成\nAI分析で高品質な結果\nオンライン必須",
            font=("游ゴシック", 11),
            bg="#4A90E2",
            fg="white",
            width=40,
            height=6,
            command=lambda: self.start_mode(selection_frame, "traditional")
        )
        traditional_btn.pack(pady=10)

    def start_mode(self, selection_frame, mode):
        """選択されたモードで開始"""
        selection_frame.destroy()
        
        if mode == "smart":
            from src.ui.smart_input_form import SmartInputForm
            self.smart_form = SmartInputForm(self, self.on_smart_complete)
            self.smart_form.pack(fill="both", expand=True)
        else:
            self.input_form = InputForm(self, self.on_analyze)
            self.input_form.pack(fill="both", expand=True)

    def new_interview(self):
        """従来モードで新規面談"""
        if hasattr(self, 'input_form'):
            self.input_form.destroy()
        if hasattr(self, 'smart_form'):
            self.smart_form.destroy()
        
        self.input_form = InputForm(self, self.on_analyze)
        self.input_form.pack(fill="both", expand=True)

    def new_smart_interview(self):
        """スマートモードで新規面談"""
        if hasattr(self, 'input_form'):
            self.input_form.destroy()
        if hasattr(self, 'smart_form'):
            self.smart_form.destroy()
        
        from src.ui.smart_input_form import SmartInputForm
        self.smart_form = SmartInputForm(self, self.on_smart_complete)
        self.smart_form.pack(fill="both", expand=True)
    
    def on_analyze(self, interview_data):
        # イニシャル生成
        initials = self.privacy.get_initials(interview_data['児童氏名'])
        interview_data['児童イニシャル'] = initials
        
        # モード選択ダイアログを表示
        history_count = self.history_manager.get_history_count()
        mode_dialog = ModeSelectorDialog(self, history_count)
        self.wait_window(mode_dialog)
        
        selected_mode = mode_dialog.get_selected_mode()
        
        if not selected_mode:
            return  # キャンセルされた
        
        if selected_mode == 'quick':
            self.process_quick_mode(interview_data)
        elif selected_mode == 'data':
            self.process_data_mode(interview_data)
        elif selected_mode == 'ai':
            self.process_ai_mode(interview_data)
        elif selected_mode == 'integrated':
            self.process_integrated_mode(interview_data)
    
    def process_quick_mode(self, interview_data):
        """クイックモード処理"""
        # テンプレート選択ダイアログ
        quick_dialog = QuickModeDialog(self, interview_data)
        self.wait_window(quick_dialog)
        
        selected_templates = quick_dialog.get_selected_templates()
        
        if not selected_templates or not selected_templates.get('issues'):
            messagebox.showwarning("警告", "テンプレートを選択してください")
            return
        
        # アセスメントデータ生成
        assessment_data = self.quick_analyzer.create_from_template(selected_templates)
        
        # 簡易報告書生成
        report_text = self.quick_analyzer.generate_simple_report(interview_data, assessment_data)
        
        analysis_result = {
            'assessment_data': assessment_data,
            'report_text': report_text,
            'missing_info': []
        }
        
        # データ保存
        self.history_manager.save_interview(interview_data, assessment_data)
        
        # プレビュー表示
        self.show_preview(analysis_result, interview_data)
    
    def process_data_mode(self, interview_data):
        """データ活用モード処理"""
        # 類似ケース検索ダイアログ
        data_dialog = DataModeDialog(self, interview_data)
        self.wait_window(data_dialog)
        
        selected_case = data_dialog.get_selected_case()
        
        if not selected_case:
            messagebox.showinfo("情報", "ケースが選択されませんでした")
            return
        
        # 選択されたケースのデータを使用
        assessment_data = {
            'issues': selected_case.get('issues', {}),
            'short_term_plan': selected_case.get('short_term_plan', {}),
            'long_term_plan': {},
            'future_path': {'type': '不明', 'detail': ''},
            'missing_info': ['過去データを参考にしています。必要に応じて修正してください。']
        }
        
        # 簡易報告書生成
        report_text = self.quick_analyzer.generate_simple_report(interview_data, assessment_data)
        
        analysis_result = {
            'assessment_data': assessment_data,
            'report_text': report_text,
            'missing_info': assessment_data['missing_info']
        }
        
        # データ保存
        self.history_manager.save_interview(interview_data, assessment_data)
        
        # プレビュー表示
        self.show_preview(analysis_result, interview_data)
    
    def process_ai_mode(self, interview_data):
        """AI分析モード処理（従来通り）"""
        loading = tk.Toplevel(self)
        loading.title("AI分析中")
        loading.geometry("400x200")
        loading.transient(self)
        loading.grab_set()
        
        tk.Label(
            loading,
            text="⏳ Claude AIが分析中です...",
            font=("游ゴシック", 14)
        ).pack(pady=30)
        
        progress_label = tk.Label(loading, text="", fg="gray")
        progress_label.pack()
        
        def analyze_thread():
            try:
                self.after(0, lambda: progress_label.config(text="✓ 個人情報を保護しました"))
                self.after(0, lambda: progress_label.config(text="⏳ AI分析中..."))
                
                analysis_result = self.analyzer.analyze_interview(interview_data)
                
                # デバッグ出力
                print(f"🔧 デバッグ: AI分析結果の構造: {type(analysis_result)}")
                print(f"🔧 デバッグ: analysis_result keys: {analysis_result.keys() if isinstance(analysis_result, dict) else 'Not a dict'}")
                
                # データ保存
                if 'assessment_data' in analysis_result:
                    self.history_manager.save_interview(interview_data, analysis_result['assessment_data'])
                else:
                    print("⚠️ 警告: assessment_dataが見つかりません")
                
                self.after(0, lambda: progress_label.config(text="✓ 分析完了"))
                self.after(0, loading.destroy)
                self.after(0, lambda: self.show_preview(analysis_result, interview_data))
            
            except Exception as e:
                error_msg = str(e)
                error_type = type(e).__name__
                print(f"❌ AI分析エラー: {error_msg}")
                print(f"❌ エラータイプ: {error_type}")
                import traceback
                print(f"❌ スタックトレース: {traceback.format_exc()}")
                
                self.after(0, loading.destroy)
                
                # APIクレジット不足の特別な処理
                if "credit balance is too low" in error_msg.lower() or "insufficient credits" in error_msg.lower():
                    self.after(0, lambda: messagebox.showerror(
                        "APIクレジット不足",
                        "Anthropic APIのクレジットが不足しています。\n\n"
                        "🔧 解決方法：\n"
                        "1. Anthropicのウェブサイトにアクセス\n"
                        "2. アカウントの「Plans & Billing」に移動\n"
                        "3. クレジットを購入またはプランをアップグレード\n\n"
                        "💡 一時的な解決策：\n"
                        "データ活用モード（オフライン）をご利用ください。"
                    ))
                else:
                    self.after(0, lambda: messagebox.showerror(
                        "エラー",
                        f"AI分析中にエラーが発生しました:\n\n{error_msg}\n\n"
                        "APIキーとインターネット接続を確認してください。\n"
                        "詳細はコンソールを確認してください。"
                    ))
        
        thread = threading.Thread(target=analyze_thread, daemon=True)
        thread.start()
    
    def show_preview(self, analysis_result, interview_data):
        preview = PreviewWindow(self, analysis_result, interview_data)
        preview.transient(self)
    
    def show_help(self):
        help_text = """【使い方】

1. 基本情報を入力
2. 通院状況を入力（該当する場合）
3. 面談メモを自由に入力
4. 「AI分析を実行」をクリック
5. 分析モードを選択
   ⚡ クイックモード - テンプレートで即作成（オフライン）
   🔍 データ活用モード - 過去データを活用（オフライン）
   🤖 AI分析モード - Claude AIで詳細分析（オンライン）
6. 結果を確認・出力

【3つのモード】
・クイックモード：3分で完成、ネット不要
・データ活用モード：過去の実績活用、ネット不要
・AI分析モード：最高品質、ネット接続必要

【注意事項】
- AI分析モードのみインターネット接続が必要です
- 個人情報はイニシャル化されます
- 使うほどデータ活用モードが便利になります"""
        
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
    
    def process_integrated_mode(self, interview_data):
        """統合モード処理"""
        from src.ui.integrated_mode_dialog import IntegratedModeDialog
        
        # 統合モードダイアログ
        integrated_dialog = IntegratedModeDialog(self, interview_data)
        self.wait_window(integrated_dialog)
    
    def on_integrated_mode_result(self, interview_data, assessment_data):
        """統合モードの結果処理"""
        try:
            # アセスメントデータを整形
            formatted_data = self.format_assessment_data(assessment_data)
            
            # 履歴に保存
            self.history_manager.save_interview(interview_data, formatted_data)
            
            # テンプレートを更新
            self.template_manager.import_from_history()
            
            # 結果を表示
            preview_window = PreviewWindow(self, interview_data, formatted_data)
            self.wait_window(preview_window)
            
        except Exception as e:
            messagebox.showerror("エラー", f"アセスメント処理中にエラーが発生しました：\n{str(e)}")
    
    def on_smart_complete(self, interview_data, assessment_data):
        """スマートモード完成時の処理"""
        # イニシャル生成
        initials = self.privacy.get_initials(interview_data['児童氏名'])
        interview_data['児童イニシャル'] = initials
        
        # 簡易報告書生成
        report_text = self.generate_simple_report(interview_data, assessment_data)
        
        analysis_result = {
            'assessment_data': assessment_data,
            'report_text': report_text,
            'missing_info': []
        }
        
        # データ保存
        self.history_manager.save_interview(interview_data, assessment_data)
        
        # プレビュー表示
        self.show_preview(analysis_result, interview_data)

    def generate_simple_report(self, interview_data, assessment_data):
        """簡易報告書を生成"""
        date_str = interview_data['面談実施日'].strftime('%Y年%m月%d日')
        
        # 課題リスト作成
        issues_list = [k for k, v in assessment_data['issues'].items() if v.get('該当', False)]
        issues_text = "、".join(issues_list) if issues_list else "特になし"
        
        # 報告書テキスト
        report = f"""【時間】
{interview_data.get('面談時間', '未記録')}

【支援内容】
初回アセスメント面談

【面談内容】
◎当日の様子
{interview_data['メモ']}

【近況】
・登校状況：{assessment_data['issues'].get('不登校', {}).get('詳細', '不明')}
・生活リズム：{assessment_data['issues'].get('生活リズム', {}).get('詳細', '不明')}
・対人関係：{assessment_data['issues'].get('対人緊張の高さ', {}).get('詳細', '不明')}

【確認された課題】
{issues_text}

【本人のニーズ】
{assessment_data['short_term_plan'].get('ニーズ_本人', '')}

【保護者のニーズ】
{assessment_data['short_term_plan'].get('ニーズ_保護者', '')}

【希望する進路】
{assessment_data['future_path']['type']}：{assessment_data['future_path']['detail']}

【本人情報】
・{interview_data['学校名']} {interview_data['学年']}年生
・性別：{interview_data['性別']}
・通院状況：{'あり' if interview_data['通院状況'].get('通院あり') else 'なし'}

【次回の予定】
（次回面談日時を記入）
"""
        
        return report

    def format_assessment_data(self, data):
        """アセスメントデータを整形"""
        return {
            'issues': data.get('issues', {}),
            'short_term_plan': {
                'ニーズ_本人': data.get('needs', {}).get('本人のニーズ', ''),
                'ニーズ_保護者': data.get('needs', {}).get('保護者のニーズ', ''),
                '目標': data.get('needs', {}).get('短期目標', ''),
                '方法': data.get('support', {}).get('支援方法', '')
            },
            'long_term_plan': {
                '目標': data.get('needs', {}).get('長期目標', ''),
                '方法': data.get('support', {}).get('継続支援', '')
            },
            'future_path': data.get('path', {})
        }

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()

