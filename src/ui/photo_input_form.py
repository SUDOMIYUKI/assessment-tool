"""
写真入力フォーム
- OCRで読み取ったデータを表示
- 信頼度が低い項目をハイライト
- 手動修正可能なUI
- smart_input_form.pyと同じデータ形式で保存
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from typing import Dict


class PhotoInputForm(tk.Toplevel):
    """写真から読み取ったデータの確認・修正フォーム"""
    
    def __init__(self, parent, ocr_data: Dict, confidence: float = 0.0):
        super().__init__(parent)
        
        self.parent = parent
        self.ocr_data = ocr_data
        self.confidence = confidence
        
        self.title("📷 写真から読み取ったデータの確認")
        self.geometry("1000x800")
        
        # 中央に配置
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f'+{x}+{y}')
        
        # モーダル設定
        self.transient(parent)
        self.grab_set()
        
        # 入力フィールドの辞書
        self.fields = {}
        
        self.create_widgets()
        self.populate_data()
    
    def create_widgets(self):
        """ウィジェットを作成"""
        # ヘッダー
        header_frame = tk.Frame(self, bg="#e67e22", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame,
            text="📷 写真から読み取ったデータの確認・修正",
            font=("游ゴシック", 16, "bold"),
            bg="#e67e22",
            fg="white"
        )
        title.pack(side="left", padx=20, pady=20)
        
        # 信頼度表示
        confidence_text = f"OCR信頼度: {self.confidence:.1f}%"
        confidence_color = "#27ae60" if self.confidence >= 80 else "#f39c12" if self.confidence >= 60 else "#e74c3c"
        
        confidence_label = tk.Label(
            header_frame,
            text=confidence_text,
            font=("游ゴシック", 12, "bold"),
            bg="#e67e22",
            fg="white"
        )
        confidence_label.pack(side="right", padx=20)
        
        # 警告メッセージ
        warning_frame = tk.Frame(self, bg="#fff3cd", height=40)
        warning_frame.pack(fill="x")
        warning_frame.pack_propagate(False)
        
        warning_label = tk.Label(
            warning_frame,
            text="⚠️ 黄色でハイライトされた項目は読み取り精度が低い可能性があります。内容を確認してください。",
            bg="#fff3cd",
            fg="#856404",
            font=("游ゴシック", 10)
        )
        warning_label.pack(pady=10)
        
        # メインコンテンツ（スクロール可能）
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # セクション1: 基本情報
        self.create_basic_info_section(scrollable_frame)
        
        # セクション2: 家族関係（ジェノグラム）
        self.create_family_section(scrollable_frame)
        
        # セクション3: 登校状況
        self.create_attendance_section(scrollable_frame)
        
        # セクション4: 生活状況
        self.create_life_section(scrollable_frame)
        
        # セクション5: 学習状況
        self.create_study_section(scrollable_frame)
        
        # セクション6: 対人関係
        self.create_social_section(scrollable_frame)
        
        # セクション7: 発達特性・医療情報
        self.create_medical_section(scrollable_frame)
        
        # セクション8: 家庭環境
        self.create_family_issues_section(scrollable_frame)
        
        # セクション9: ニーズ・目標
        self.create_plans_section(scrollable_frame)
        
        # セクション10: 支援への希望
        self.create_support_wishes_section(scrollable_frame)
        
        # セクション11: 当日の様子
        self.create_memo_section(scrollable_frame)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # ボタンエリア
        button_frame = tk.Frame(self)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        cancel_btn = tk.Button(
            button_frame,
            text="キャンセル",
            command=self.destroy,
            padx=15,
            pady=8
        )
        cancel_btn.pack(side="left")
        
        save_btn = tk.Button(
            button_frame,
            text="✅ 確認完了・データを保存",
            font=("游ゴシック", 12, "bold"),
            bg="#27ae60",
            fg="white",
            command=self.save_data,
            padx=20,
            pady=10
        )
        save_btn.pack(side="right")
    
    def create_section_frame(self, parent, title: str) -> ttk.Frame:
        """セクションフレームを作成"""
        section = ttk.LabelFrame(parent, text=title, padding=15)
        section.pack(fill="x", padx=10, pady=10)
        return section
    
    def create_entry_field(self, parent, label: str, field_name: str, default_value: str = "", 
                          highlight: bool = False, width: int = 40) -> tk.Entry:
        """入力フィールドを作成"""
        frame = tk.Frame(parent)
        frame.pack(fill="x", pady=5)
        
        tk.Label(frame, text=label, width=20, anchor="w").pack(side="left")
        
        entry = tk.Entry(frame, width=width)
        entry.pack(side="left", padx=5, fill="x", expand=True)
        if default_value:
            entry.insert(0, str(default_value))
        
        if highlight:
            entry.config(bg="#fff3cd")  # 黄色ハイライト
        
        self.fields[field_name] = entry
        return entry
    
    def create_text_field(self, parent, label: str, field_name: str, default_value: str = "",
                         highlight: bool = False, height: int = 3) -> scrolledtext.ScrolledText:
        """複数行テキストフィールドを作成"""
        frame = tk.Frame(parent)
        frame.pack(fill="x", pady=5)
        
        tk.Label(frame, text=label, anchor="w").pack(anchor="w")
        
        text_widget = scrolledtext.ScrolledText(frame, height=height, wrap=tk.WORD)
        text_widget.pack(fill="x", padx=5, pady=5)
        if default_value:
            text_widget.insert("1.0", str(default_value))
        
        if highlight:
            text_widget.config(bg="#fff3cd")  # 黄色ハイライト
        
        self.fields[field_name] = text_widget
        return text_widget
    
    def create_checkbox_field(self, parent, label: str, field_name: str, 
                             default_value: bool = False) -> tk.BooleanVar:
        """チェックボックスを作成"""
        var = tk.BooleanVar(value=default_value)
        checkbox = ttk.Checkbutton(parent, text=label, variable=var)
        checkbox.pack(anchor="w", pady=2)
        
        self.fields[field_name] = var
        return var
    
    def create_basic_info_section(self, parent):
        """基本情報セクション"""
        section = self.create_section_frame(parent, "📋 基本情報")
        
        # 低信頼度の判定（仮）
        low_confidence = self.confidence < 70
        
        self.create_entry_field(section, "児童氏名:", "child_name", 
                               self.ocr_data.get('child_name', ''), low_confidence)
        self.create_entry_field(section, "保護者氏名:", "guardian_name",
                               self.ocr_data.get('guardian_name', ''), low_confidence)
        self.create_entry_field(section, "学校名:", "school_name",
                               self.ocr_data.get('school_name', ''), low_confidence)
        self.create_entry_field(section, "学年:", "grade",
                               self.ocr_data.get('grade', ''), low_confidence, width=10)
        
        # 性別（ラジオボタン）
        gender_frame = tk.Frame(section)
        gender_frame.pack(fill="x", pady=5)
        tk.Label(gender_frame, text="性別:", width=20, anchor="w").pack(side="left")
        
        self.fields['gender'] = tk.StringVar(value='unselected')  # デフォルトは未選択
        tk.Radiobutton(gender_frame, text="男性", variable=self.fields['gender'], 
                      value="男性").pack(side="left")
        tk.Radiobutton(gender_frame, text="女性", variable=self.fields['gender'],
                      value="女性").pack(side="left")
        
        self.create_entry_field(section, "担当支援員:", "supporter",
                               self.ocr_data.get('supporter', ''), low_confidence)
        
        # ひとり親世帯
        self.create_checkbox_field(section, "ひとり親世帯", "single_parent",
                                  self.ocr_data.get('single_parent', False))
    
    def create_family_section(self, parent):
        """家族関係セクション"""
        section = self.create_section_frame(parent, "👨‍👩‍👧 家族関係・ジェノグラム")
        
        genogram_data = self.ocr_data.get('family_genogram', {})
        
        self.create_text_field(section, "ジェノグラム（自由記入）:", "genogram_raw",
                              genogram_data.get('raw_text', ''), height=5)
        self.create_text_field(section, "特記事項:", "genogram_notes",
                              genogram_data.get('notes', ''), height=2)
    
    def create_attendance_section(self, parent):
        """登校状況セクション"""
        section = self.create_section_frame(parent, "🏫 登校状況")
        
        attendance = self.ocr_data.get('attendance', {})
        
        # 登校頻度
        freq_frame = tk.Frame(section)
        freq_frame.pack(fill="x", pady=5)
        tk.Label(freq_frame, text="登校頻度:", width=20, anchor="w").pack(side="left")
        
        # OCRで正しく認識されなかった場合は空文字（未選択）にする
        frequency_value = 'unselected'  # 常に未選択（OCR精度が低いため）
            
        self.fields['attendance_frequency'] = tk.StringVar(value=frequency_value)
        frequencies = ['週0回', '週1-2回', '週3-4回', 'ほぼ毎日']
        for freq in frequencies:
            tk.Radiobutton(freq_frame, text=freq, variable=self.fields['attendance_frequency'],
                          value=freq).pack(side="left")
        
        # 不登校該当（OCRで認識されなかった場合はFalse）
        truancy_value = False  # 常に未選択（OCR精度が低いため）
        self.create_checkbox_field(section, "不登校に該当", "truancy", truancy_value)
        
        self.create_text_field(section, "詳細・経緯:", "attendance_detail",
                              attendance.get('detail', ''), height=3)
    
    def create_life_section(self, parent):
        """生活状況セクション"""
        section = self.create_section_frame(parent, "🏠 生活状況")
        
        # 生活リズムの課題
        rhythm_frame = tk.LabelFrame(section, text="生活リズムの課題", padx=10, pady=5)
        rhythm_frame.pack(fill="x", pady=5)
        
        rhythm_issues = ['朝起きられない', '昼夜逆転', '睡眠不足']
        self.fields['life_rhythm'] = {}
        for issue in rhythm_issues:
            checked = issue in self.ocr_data.get('life_rhythm', [])
            self.fields['life_rhythm'][issue] = self.create_checkbox_field(rhythm_frame, issue, 
                                                                           f'life_rhythm_{issue}', checked)
        
        # 生活習慣の課題
        habit_frame = tk.LabelFrame(section, text="生活習慣の課題", padx=10, pady=5)
        habit_frame.pack(fill="x", pady=5)
        
        habit_issues = ['食事の乱れ', '運動不足', 'ゲーム依存']
        self.fields['life_habit'] = {}
        for issue in habit_issues:
            checked = issue in self.ocr_data.get('life_habit', [])
            self.fields['life_habit'][issue] = self.create_checkbox_field(habit_frame, issue,
                                                                          f'life_habit_{issue}', checked)
        
        # 外出状況
        outing_frame = tk.Frame(section)
        outing_frame.pack(fill="x", pady=5)
        tk.Label(outing_frame, text="外出状況:", width=20, anchor="w").pack(side="left")
        
        self.fields['outing'] = tk.StringVar(value='unselected')  # デフォルトは未選択
        outings = ['外出する', 'コンビニ程度', 'ほぼ外出しない']
        for outing in outings:
            tk.Radiobutton(outing_frame, text=outing, variable=self.fields['outing'],
                          value=outing).pack(side="left")
    
    def create_study_section(self, parent):
        """学習状況セクション"""
        section = self.create_section_frame(parent, "📚 学習状況")
        
        study_issues = ['学習の遅れ', '低学力', '習慣なし', '環境なし']
        self.fields['study_issues'] = {}
        for issue in study_issues:
            checked = issue in self.ocr_data.get('study_issues', [])
            self.fields['study_issues'][issue] = self.create_checkbox_field(section, issue,
                                                                            f'study_{issue}', checked)
    
    def create_social_section(self, parent):
        """対人関係セクション"""
        section = self.create_section_frame(parent, "👥 対人関係")
        
        social_issues = ['対人緊張', '友達不安', 'コミュ苦手']
        self.fields['social_issues'] = {}
        for issue in social_issues:
            checked = issue in self.ocr_data.get('social_issues', [])
            self.fields['social_issues'][issue] = self.create_checkbox_field(section, issue,
                                                                             f'social_{issue}', checked)
    
    def create_medical_section(self, parent):
        """発達特性・医療情報セクション"""
        section = self.create_section_frame(parent, "🧠 発達特性・医療情報")
        
        developmental = self.ocr_data.get('developmental', {})
        medical_info = self.ocr_data.get('medical_info', {})
        
        self.create_checkbox_field(section, "発達特性あり", "developmental_has_issues",
                                  developmental.get('has_issues', False))
        self.create_entry_field(section, "発達特性の内容:", "developmental_detail",
                               developmental.get('detail', ''))
        
        self.create_entry_field(section, "通院（病院名）:", "hospital",
                               medical_info.get('hospital', ''))
        self.create_entry_field(section, "通院頻度:", "hospital_frequency",
                               medical_info.get('frequency', ''))
        self.create_entry_field(section, "診断名:", "diagnosis",
                               medical_info.get('diagnosis', ''))
        self.create_entry_field(section, "投薬（薬名）:", "medication",
                               medical_info.get('medication', ''))
        self.create_entry_field(section, "手帳（種類）:", "handbook",
                               medical_info.get('handbook', ''))
    
    def create_family_issues_section(self, parent):
        """家庭環境セクション"""
        section = self.create_section_frame(parent, "👨‍👩‍👧‍👦 家庭環境")
        
        family_issues = ['経済困難', '家族関係', '他世帯員', '虐待', 'その他']
        self.fields['family_issues'] = {}
        for issue in family_issues:
            checked = issue in self.ocr_data.get('family_issues', [])
            self.fields['family_issues'][issue] = self.create_checkbox_field(section, issue,
                                                                             f'family_{issue}', checked)
    
    def create_plans_section(self, parent):
        """ニーズ・目標セクション"""
        section = self.create_section_frame(parent, "🎯 ニーズ・目標")
        
        # 短期目標
        short_plan_frame = tk.LabelFrame(section, text="短期目標", padx=10, pady=10)
        short_plan_frame.pack(fill="x", pady=5)
        
        short_plan = self.ocr_data.get('short_term_plan', {})
        self.create_entry_field(short_plan_frame, "課題:", "short_issue",
                               short_plan.get('issue', ''))
        self.create_text_field(short_plan_frame, "現状:", "short_current_status",
                              short_plan.get('current_status', ''), height=2)
        self.create_text_field(short_plan_frame, "ニーズ（本人）:", "short_needs_child",
                              short_plan.get('needs_child', ''), height=2)
        self.create_text_field(short_plan_frame, "ニーズ（保護者）:", "short_needs_guardian",
                              short_plan.get('needs_guardian', ''), height=2)
        self.create_text_field(short_plan_frame, "目標:", "short_goal",
                              short_plan.get('goal', ''), height=2)
        self.create_text_field(short_plan_frame, "具体的な方法:", "short_method",
                              short_plan.get('method', ''), height=3)
        
        # 長期目標
        long_plan_frame = tk.LabelFrame(section, text="長期目標（本事業における達成目標）", 
                                       padx=10, pady=10)
        long_plan_frame.pack(fill="x", pady=5)
        
        long_plan = self.ocr_data.get('long_term_plan', {})
        self.create_entry_field(long_plan_frame, "課題:", "long_issue",
                               long_plan.get('issue', ''))
        self.create_text_field(long_plan_frame, "目標:", "long_goal",
                              long_plan.get('goal', ''), height=2)
        self.create_text_field(long_plan_frame, "具体的な方法:", "long_method",
                              long_plan.get('method', ''), height=3)
    
    def create_support_wishes_section(self, parent):
        """支援への希望セクション"""
        section = self.create_section_frame(parent, "🙏 支援への希望")
        
        wishes = self.ocr_data.get('support_wishes', {})
        
        # 希望の曜日
        days_frame = tk.Frame(section)
        days_frame.pack(fill="x", pady=5)
        tk.Label(days_frame, text="希望の曜日:", width=20, anchor="w").pack(side="left")
        
        self.fields['support_days'] = {}
        days = ['月', '火', '水', '木', '金']
        preferred_days = wishes.get('preferred_days', '').split('・')
        for day in days:
            var = tk.BooleanVar(value=(day in preferred_days))
            ttk.Checkbutton(days_frame, text=day, variable=var).pack(side="left")
            self.fields['support_days'][day] = var
        
        self.create_entry_field(section, "希望の時間帯:", "support_time",
                               wishes.get('preferred_time', ''))
        self.create_entry_field(section, "希望の場所:", "support_location",
                               wishes.get('preferred_location', ''))
        self.create_entry_field(section, "希望の支援員:", "support_staff",
                               wishes.get('preferred_staff', ''))
        self.create_text_field(section, "解決したいこと:", "support_goals",
                              wishes.get('solving_goals', ''), height=3)
    
    def create_memo_section(self, parent):
        """当日の様子セクション"""
        section = self.create_section_frame(parent, "📝 当日の様子・メモ")
        
        self.create_text_field(section, "当日の様子:", "memo",
                              self.ocr_data.get('memo', ''), height=5)
    
    def populate_data(self):
        """OCRデータをフィールドに反映（既に各create関数内で実施済み）"""
        pass
    
    def get_form_data(self) -> Dict:
        """フォームからデータを取得"""
        data = {}
        
        # 基本情報
        data['児童氏名'] = self.fields['child_name'].get()
        data['保護者氏名'] = self.fields['guardian_name'].get()
        data['学校名'] = self.fields['school_name'].get()
        data['学年'] = int(self.fields['grade'].get()) if self.fields['grade'].get().isdigit() else 2
        data['性別'] = self.fields['gender'].get() if self.fields['gender'].get() != 'unselected' else ''
        data['担当支援員'] = self.fields['supporter'].get()
        data['ひとり親世帯'] = '該当' if self.fields['single_parent'].get() else '該当しない'
        
        # 家族関係
        data['家族関係'] = {
            'ジェノグラム': self.fields['genogram_raw'].get("1.0", tk.END).strip(),
            '特記事項': self.fields['genogram_notes'].get("1.0", tk.END).strip()
        }
        
        # 登校状況
        data['登校状況'] = {
            '頻度': self.fields['attendance_frequency'].get() if self.fields['attendance_frequency'].get() != 'unselected' else '',
            '不登校該当': self.fields['truancy'].get(),
            '詳細': self.fields['attendance_detail'].get("1.0", tk.END).strip()
        }
        
        # 生活状況
        data['生活リズム'] = [issue for issue, var in self.fields['life_rhythm'].items() if var.get()]
        data['生活習慣'] = [issue for issue, var in self.fields['life_habit'].items() if var.get()]
        data['外出状況'] = self.fields['outing'].get() if self.fields['outing'].get() != 'unselected' else ''
        
        # 学習状況
        data['学習課題'] = [issue for issue, var in self.fields['study_issues'].items() if var.get()]
        
        # 対人関係
        data['対人関係課題'] = [issue for issue, var in self.fields['social_issues'].items() if var.get()]
        
        # 発達特性・医療情報
        data['発達特性'] = {
            '該当': self.fields['developmental_has_issues'].get(),
            '内容': self.fields['developmental_detail'].get()
        }
        data['医療情報'] = {
            '病院': self.fields['hospital'].get(),
            '頻度': self.fields['hospital_frequency'].get(),
            '診断': self.fields['diagnosis'].get(),
            '投薬': self.fields['medication'].get(),
            '手帳': self.fields['handbook'].get()
        }
        
        # 家庭環境
        data['家庭環境課題'] = [issue for issue, var in self.fields['family_issues'].items() if var.get()]
        
        # 短期目標
        data['短期目標'] = {
            '課題': self.fields['short_issue'].get(),
            '現状': self.fields['short_current_status'].get("1.0", tk.END).strip(),
            'ニーズ本人': self.fields['short_needs_child'].get("1.0", tk.END).strip(),
            'ニーズ保護者': self.fields['short_needs_guardian'].get("1.0", tk.END).strip(),
            '目標': self.fields['short_goal'].get("1.0", tk.END).strip(),
            '方法': self.fields['short_method'].get("1.0", tk.END).strip()
        }
        
        # 長期目標
        data['長期目標'] = {
            '課題': self.fields['long_issue'].get(),
            '目標': self.fields['long_goal'].get("1.0", tk.END).strip(),
            '方法': self.fields['long_method'].get("1.0", tk.END).strip()
        }
        
        # 支援への希望
        preferred_days = [day for day, var in self.fields['support_days'].items() if var.get()]
        data['支援希望'] = {
            '希望の曜日': '・'.join(preferred_days),
            '希望の時間帯': self.fields['support_time'].get(),
            '希望の場所': self.fields['support_location'].get(),
            '希望の支援員': self.fields['support_staff'].get(),
            '解決したいこと': self.fields['support_goals'].get("1.0", tk.END).strip()
        }
        
        # 当日の様子
        data['当日の様子'] = self.fields['memo'].get("1.0", tk.END).strip()
        
        # 面談実施日（現在日時）
        data['面談実施日'] = datetime.now()
        
        return data
    
    def save_data(self):
        """データを保存"""
        try:
            # フォームデータを取得
            form_data = self.get_form_data()
            
            # 必須項目のチェック
            if not form_data['児童氏名']:
                messagebox.showwarning("警告", "児童氏名を入力してください。")
                return
            
            # アセスメントデータを生成（smart_input_formと同じ形式）
            from src.utils.assessment_data_builder import build_assessment_data
            assessment_data = build_assessment_data(form_data)
            
            # 親アプリケーションのコールバックを呼び出し
            if hasattr(self, 'parent_app') and hasattr(self.parent_app, 'on_smart_complete'):
                self.parent_app.on_smart_complete(form_data, assessment_data)
                messagebox.showinfo("完了", "データを保存しました！")
            else:
                messagebox.showinfo("完了", "データを保存しました！")
            
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("エラー", f"データ保存中にエラーが発生しました:\n{str(e)}")
            import traceback
            traceback.print_exc()
    


if __name__ == '__main__':
    # テスト用
    root = tk.Tk()
    root.withdraw()
    
    # テストデータ
    test_data = {
        'child_name': '山田太郎',
        'guardian_name': '山田花子',
        'school_name': '○○中学校',
        'grade': '2',
        'gender': '男性',
        'supporter': '田中支援員',
        'single_parent': False,
        'attendance': {
            'frequency': '週1-2回',
            'truancy': True,
            'detail': 'コロナ以降不登校'
        },
        'life_rhythm': ['昼夜逆転', '朝起きられない'],
        'life_habit': ['ゲーム依存'],
        'outing': 'コンビニ程度',
        'study_issues': ['学習の遅れ', '習慣なし'],
        'social_issues': ['対人緊張'],
        'short_term_plan': {
            'issue': '生活リズムの改善',
            'goal': '9時までに起床'
        }
    }
    
    form = PhotoInputForm(root, test_data, confidence=75.5)
    root.mainloop()

