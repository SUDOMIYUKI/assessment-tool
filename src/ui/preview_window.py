import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
import subprocess
import platform

class PreviewWindow(tk.Toplevel):
    def __init__(self, parent, analysis_result, interview_data):
        super().__init__(parent)
        
        self.analysis_result = analysis_result
        self.interview_data = interview_data
        
        self.title("AI分析結果")
        self.geometry("900x700")
        
        self.create_widgets()
    
    def create_widgets(self):
        header_frame = tk.Frame(self, bg="#4A90E2", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame,
            text="📊 AI分析結果",
            font=("游ゴシック", 16, "bold"),
            bg="#4A90E2",
            fg="white"
        )
        title.pack(side="left", padx=20, pady=20)
        
        initials = self.interview_data.get('児童イニシャル', '')
        date_str = self.interview_data['面談実施日'].strftime('%Y/%m/%d')
        supporter = self.interview_data['担当支援員']
        
        info_text = f"児童: {initials} | 面談日: {date_str} | 担当: {supporter}"
        info_label = tk.Label(
            header_frame,
            text=info_text,
            font=("游ゴシック", 10),
            bg="#4A90E2",
            fg="white"
        )
        info_label.pack(side="left", padx=20)
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        assessment_frame = ttk.Frame(self.notebook)
        self.notebook.add(assessment_frame, text="📄 アセスメントシート")
        self.create_assessment_preview(assessment_frame)
        
        report_frame = ttk.Frame(self.notebook)
        self.notebook.add(report_frame, text="📝 報告書テキスト")
        self.create_report_preview(report_frame)
        
        button_frame = tk.Frame(self)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        back_btn = tk.Button(
            button_frame,
            text="🏠 ホームに戻る",
            font=("游ゴシック", 10, "bold"),
            bg="#9b59b6",
            fg="white",
            command=self.return_home,
            padx=20,
            pady=8
        )
        back_btn.pack(side="left", padx=5)
        
        close_btn = tk.Button(
            button_frame,
            text="閉じる",
            command=self.destroy,
            padx=15,
            pady=8
        )
        close_btn.pack(side="right", padx=5)
    
    def create_assessment_preview(self, parent):
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        assessment_data = self.analysis_result['assessment_data']
        
        basic_frame = ttk.LabelFrame(scrollable_frame, text="基本情報", padding=10)
        basic_frame.pack(fill="x", padx=10, pady=5)
        
        basic_text = f"""児童氏名: {self.interview_data['児童氏名']}
保護者氏名: {self.interview_data['保護者氏名']}
学校名: {self.interview_data['学校名']}
学年: {self.interview_data['学年']}年生
性別: {self.interview_data['性別']}"""
        
        tk.Label(basic_frame, text=basic_text, justify="left").pack(anchor="w")
        
        # 医療・支援情報
        medical_frame = ttk.LabelFrame(scrollable_frame, text="医療・支援情報", padding=10)
        medical_frame.pack(fill="x", padx=10, pady=5)
        
        medical_info = self.interview_data.get('通院状況', {})
        medical_text = ""
        
        if medical_info.get('通院あり'):
            hospital_text = medical_info.get('病院名', '不明')
            if medical_info.get('頻度'):
                hospital_text += f"（{medical_info.get('頻度')}）"
            medical_text += f"・通院: {hospital_text}\n"
        
        if medical_info.get('投薬治療'):
            medical_text += f"・投薬治療: {medical_info.get('薬名', '不明')}\n"
        
        if medical_info.get('診断あり'):
            medical_text += f"・診断: {medical_info.get('診断名', '不明')}\n"
        
        if medical_info.get('手帳あり'):
            medical_text += f"・手帳: {medical_info.get('手帳種類', '不明')}\n"
        
        if medical_text.strip():
            tk.Label(medical_frame, text=medical_text.strip(), justify="left", wraplength=800).pack(anchor="w")
        else:
            tk.Label(medical_frame, text="医療・支援情報なし", fg="gray", justify="left").pack(anchor="w")
        
        issues_frame = ttk.LabelFrame(scrollable_frame, text="世帯の具体的な課題", padding=10)
        issues_frame.pack(fill="x", padx=10, pady=5)
        
        for issue_name, issue_data in assessment_data['issues'].items():
            checkbox = "☑" if issue_data.get('該当') else "☐"
            detail = issue_data.get('詳細', '')
            
            issue_text = f"{checkbox} {issue_name}"
            if detail and detail not in ["該当なし", "特に問題なし", "不明"]:
                issue_text += f"\n   {detail}"
            
            tk.Label(
                issues_frame,
                text=issue_text,
                justify="left",
                wraplength=800
            ).pack(anchor="w", pady=2)
        
        plan_frame = ttk.LabelFrame(scrollable_frame, text="支援計画（短期目標）", padding=10)
        plan_frame.pack(fill="x", padx=10, pady=5)
        
        plan = assessment_data['short_term_plan']
        plan_text = f"""課題: {plan.get('課題', '')}

現状: {plan.get('現状', '')}

ニーズ（本人）: {plan.get('ニーズ_本人', '')}
ニーズ（保護者）: {plan.get('ニーズ_保護者', '')}

目標: {plan.get('目標', '')}

具体的な方法: {plan.get('方法', '')}"""
        
        tk.Label(plan_frame, text=plan_text, justify="left", wraplength=800).pack(anchor="w")
        
        # 支援希望セクション
        if self.interview_data.get('支援希望'):
            support_frame = ttk.LabelFrame(scrollable_frame, text="支援への希望", padding=10)
            support_frame.pack(fill="x", padx=10, pady=5)
            
            support_wishes = self.interview_data['支援希望']
            support_text = ""
            
            if support_wishes.get('希望の曜日'):
                support_text += f"希望の曜日: {support_wishes.get('希望の曜日')}\n"
            if support_wishes.get('希望の時間帯'):
                support_text += f"希望の時間帯: {support_wishes.get('希望の時間帯')}\n"
            if support_wishes.get('希望の場所'):
                support_text += f"希望の場所: {support_wishes.get('希望の場所')}\n"
            if support_wishes.get('希望の支援員'):
                support_text += f"希望の支援員: {support_wishes.get('希望の支援員')}\n"
            if support_wishes.get('解決したいこと'):
                support_text += f"解決したいこと:\n{support_wishes.get('解決したいこと')}\n"
            
            if support_text.strip():
                tk.Label(support_frame, text=support_text.strip(), justify="left", wraplength=800).pack(anchor="w")
            else:
                tk.Label(support_frame, text="支援希望は未入力です", fg="gray", justify="left").pack(anchor="w")
        
        if assessment_data.get('missing_info'):
            missing_frame = ttk.LabelFrame(scrollable_frame, text="⚠️ 不足情報", padding=10)
            missing_frame.pack(fill="x", padx=10, pady=5)
            
            for info in assessment_data['missing_info']:
                tk.Label(
                    missing_frame,
                    text=f"・{info}",
                    fg="orange",
                    justify="left"
                ).pack(anchor="w")
        
        output_btn = tk.Button(
            scrollable_frame,
            text="💾 Excelに出力",
            font=("游ゴシック", 12, "bold"),
            bg="#7ED321",
            fg="white",
            command=self.export_assessment,
            padx=20,
            pady=10
        )
        output_btn.pack(pady=20)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_report_preview(self, parent):
        info_frame = tk.Frame(parent, bg="#FFF9E6", height=60)
        info_frame.pack(fill="x", padx=10, pady=10)
        info_frame.pack_propagate(False)
        
        info_label = tk.Label(
            info_frame,
            text="💡 このテキストを報告書Excelにコピー＆貼り付けしてください。",
            bg="#FFF9E6",
            fg="#666",
            wraplength=800
        )
        info_label.pack(padx=10, pady=10)
        
        text_frame = ttk.LabelFrame(parent, text="報告書用テキスト", padding=10)
        text_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.report_text = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            width=80,
            height=25,
            font=("游ゴシック", 11)
        )
        self.report_text.pack(fill="both", expand=True)
        
        report_content = self.analysis_result['report_text']
        self.report_text.insert("1.0", report_content)
        
        char_count = len(report_content)
        page_estimate = "約2ページ" if char_count <= 1500 else "2ページ超過"
        
        stats_label = tk.Label(
            text_frame,
            text=f"文字数: {char_count}文字  |  印刷目安: {page_estimate}",
            fg="gray"
        )
        stats_label.pack(anchor="e", pady=5)
        
        copy_btn = tk.Button(
            text_frame,
            text="📋 全文をコピー",
            font=("游ゴシック", 12, "bold"),
            bg="#4A90E2",
            fg="white",
            command=self.copy_report_text,
            padx=20,
            pady=10
        )
        copy_btn.pack(pady=10)
    
    def export_assessment(self):
        from ..excel.assessment_writer import AssessmentWriter
        
        initials = self.interview_data.get('児童イニシャル', 'XX')
        date_str = self.interview_data['面談実施日'].strftime('%Y%m%d')
        filename = f"アセスメントシート_{initials}_{date_str}.xlsx"
        
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / filename
        
        try:
            writer = AssessmentWriter()
            writer.create_assessment_file(
                self.interview_data,
                self.analysis_result['assessment_data'],
                output_path
            )
            
            messagebox.showinfo(
                "出力完了",
                f"アセスメントシートを作成しました！\n\n{output_path}"
            )
            
            self.open_file(output_path)
        
        except Exception as e:
            messagebox.showerror("エラー", f"出力に失敗しました:\n{str(e)}")
    
    def open_file(self, filepath):
        try:
            system = platform.system()
            if system == 'Windows':
                subprocess.run(['start', '', str(filepath)], shell=True)
            elif system == 'Darwin':
                subprocess.run(['open', str(filepath)])
            else:
                subprocess.run(['xdg-open', str(filepath)])
        except Exception as e:
            print(f"ファイルを開けませんでした: {e}")
    
    def copy_report_text(self):
        self.clipboard_clear()
        self.clipboard_append(self.report_text.get("1.0", tk.END))
        
        messagebox.showinfo(
            "コピー完了",
            "報告書用テキストをクリップボードにコピーしました！\n\n"
            "次のステップ：\n"
            "1. 報告書Excelを開く\n"
            "2. 「面談内容」のセルに貼り付け（Ctrl+V）\n"
            "3. 必要に応じて編集"
        )
    
    def return_home(self):
        """ホーム画面に戻る"""
        # プレビューウィンドウを閉じる
        self.destroy()
        
        # 親ウィンドウのスマートフォームをクリアして、ホーム画面を表示
        if hasattr(self.master, 'smart_form'):
            try:
                self.master.smart_form.destroy()
            except:
                pass
        
        # ホーム画面（モード選択画面）を再表示
        self.master.show_mode_selection()

