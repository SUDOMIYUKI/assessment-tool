import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime

class SmartInputForm(tk.Frame):
    """スマート入力フォーム - 構造化された入力で即座にアセスメント完成"""
    
    def __init__(self, parent, on_complete_callback):
        super().__init__(parent)
        self.on_complete_callback = on_complete_callback
        self.create_widgets()
    
    def create_widgets(self):
        # タイトル
        title = tk.Label(
            self,
            text="⚡ スマート面談記録（リアルタイム作成）",
            font=("游ゴシック", 18, "bold")
        )
        title.pack(pady=10)
        
        hint = tk.Label(
            self,
            text="💡 面談しながらチェック・入力するだけで、アセスメントシートと報告書が同時に完成します",
            font=("游ゴシック", 10),
            fg="gray"
        )
        hint.pack(pady=5)
        
        # スクロール可能なキャンバス
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # === セクション1：基本情報 ===
        basic_frame = ttk.LabelFrame(scrollable_frame, text="📋 基本情報", padding=15)
        basic_frame.pack(fill="x", padx=20, pady=10)
        
        row = 0
        ttk.Label(basic_frame, text="児童氏名:").grid(row=row, column=0, sticky="w", pady=5)
        self.child_name_entry = ttk.Entry(basic_frame, width=20)
        self.child_name_entry.grid(row=row, column=1, sticky="w", padx=5)
        
        ttk.Label(basic_frame, text="性別:").grid(row=row, column=2, sticky="w", padx=(20, 5))
        self.gender_var = tk.StringVar(value="男性")
        ttk.Radiobutton(basic_frame, text="男性", variable=self.gender_var, value="男性").grid(row=row, column=3, sticky="w")
        ttk.Radiobutton(basic_frame, text="女性", variable=self.gender_var, value="女性").grid(row=row, column=4, sticky="w")
        
        row += 1
        ttk.Label(basic_frame, text="保護者氏名:").grid(row=row, column=0, sticky="w", pady=5)
        self.guardian_name_entry = ttk.Entry(basic_frame, width=20)
        self.guardian_name_entry.grid(row=row, column=1, sticky="w", padx=5)
        
        row += 1
        ttk.Label(basic_frame, text="学校名:").grid(row=row, column=0, sticky="w", pady=5)
        self.school_entry = ttk.Entry(basic_frame, width=30)
        self.school_entry.grid(row=row, column=1, columnspan=2, sticky="w", padx=5)
        
        ttk.Label(basic_frame, text="学年:").grid(row=row, column=3, sticky="w", padx=(20, 5))
        self.grade_spinbox = ttk.Spinbox(basic_frame, from_=1, to=12, width=5)
        self.grade_spinbox.set("2")
        self.grade_spinbox.grid(row=row, column=4, sticky="w")
        
        row += 1
        ttk.Label(basic_frame, text="担当支援員:").grid(row=row, column=0, sticky="w", pady=5)
        self.supporter_entry = ttk.Entry(basic_frame, width=20)
        self.supporter_entry.grid(row=row, column=1, sticky="w", padx=5)
        
        ttk.Label(basic_frame, text="面談実施日:").grid(row=row, column=2, sticky="w", padx=(20, 5))
        self.interview_date_entry = ttk.Entry(basic_frame, width=15)
        self.interview_date_entry.insert(0, datetime.now().strftime('%Y/%m/%d'))
        self.interview_date_entry.grid(row=row, column=3, columnspan=2, sticky="w")
        
        # === セクション2：登校状況 ===
        attendance_frame = ttk.LabelFrame(scrollable_frame, text="🏫 登校状況", padding=15)
        attendance_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(attendance_frame, text="現在の登校頻度:").grid(row=0, column=0, sticky="w", pady=5)
        self.attendance_var = tk.StringVar(value="週0回")
        attendance_options = ["週0回（完全不登校）", "週1-2回", "週3-4回", "ほぼ毎日"]
        self.attendance_combo = ttk.Combobox(attendance_frame, textvariable=self.attendance_var, values=attendance_options, width=25)
        self.attendance_combo.grid(row=0, column=1, sticky="w", padx=5)
        
        ttk.Label(attendance_frame, text="不登校の状況:").grid(row=1, column=0, sticky="nw", pady=5)
        self.truancy_check = tk.BooleanVar()
        ttk.Checkbutton(attendance_frame, text="不登校に該当", variable=self.truancy_check).grid(row=1, column=1, sticky="w", padx=5)
        
        ttk.Label(attendance_frame, text="詳細・経緯:").grid(row=2, column=0, sticky="nw", pady=5)
        self.truancy_detail = scrolledtext.ScrolledText(attendance_frame, width=50, height=3, wrap=tk.WORD)
        self.truancy_detail.grid(row=2, column=1, columnspan=2, sticky="w", padx=5)
        
        # === セクション3：生活状況 ===
        life_frame = ttk.LabelFrame(scrollable_frame, text="🏠 生活状況", padding=15)
        life_frame.pack(fill="x", padx=20, pady=10)
        
        # 生活リズム
        ttk.Label(life_frame, text="生活リズムの課題:").grid(row=0, column=0, sticky="nw", pady=5)
        rhythm_frame = tk.Frame(life_frame)
        rhythm_frame.grid(row=0, column=1, sticky="w", padx=5)
        
        self.rhythm_checks = {}
        rhythm_items = ["朝起きられない", "昼夜逆転", "睡眠不足", "特に問題なし"]
        for i, item in enumerate(rhythm_items):
            var = tk.BooleanVar()
            ttk.Checkbutton(rhythm_frame, text=item, variable=var).grid(row=i//2, column=i%2, sticky="w", padx=5)
            self.rhythm_checks[item] = var
        
        # 生活習慣
        ttk.Label(life_frame, text="生活習慣の課題:").grid(row=1, column=0, sticky="nw", pady=5)
        habit_frame = tk.Frame(life_frame)
        habit_frame.grid(row=1, column=1, sticky="w", padx=5)
        
        self.habit_checks = {}
        habit_items = ["食事の乱れ", "運動不足", "ゲーム依存傾向", "特に問題なし"]
        for i, item in enumerate(habit_items):
            var = tk.BooleanVar()
            ttk.Checkbutton(habit_frame, text=item, variable=var).grid(row=i//2, column=i%2, sticky="w", padx=5)
            self.habit_checks[item] = var
        
        # 引きこもり
        ttk.Label(life_frame, text="外出状況:").grid(row=2, column=0, sticky="w", pady=5)
        self.outing_var = tk.StringVar(value="外出する")
        outing_options = ["外出する", "コンビニ程度", "ほぼ外出しない"]
        self.outing_combo = ttk.Combobox(life_frame, textvariable=self.outing_var, values=outing_options, width=20)
        self.outing_combo.grid(row=2, column=1, sticky="w", padx=5)
        
        # === セクション4：学習状況 ===
        study_frame = ttk.LabelFrame(scrollable_frame, text="📚 学習状況", padding=15)
        study_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(study_frame, text="学習の課題:").grid(row=0, column=0, sticky="nw", pady=5)
        study_issues_frame = tk.Frame(study_frame)
        study_issues_frame.grid(row=0, column=1, sticky="w", padx=5)
        
        self.study_checks = {}
        study_items = ["学習の遅れ", "低学力", "学習習慣なし", "学習環境なし", "特に問題なし"]
        for i, item in enumerate(study_items):
            var = tk.BooleanVar()
            ttk.Checkbutton(study_issues_frame, text=item, variable=var).grid(row=i//2, column=i%2, sticky="w", padx=5)
            self.study_checks[item] = var
        
        # === セクション5：対人関係 ===
        social_frame = ttk.LabelFrame(scrollable_frame, text="👥 対人関係・コミュニケーション", padding=15)
        social_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(social_frame, text="対人関係の課題:").grid(row=0, column=0, sticky="nw", pady=5)
        social_issues_frame = tk.Frame(social_frame)
        social_issues_frame.grid(row=0, column=1, sticky="w", padx=5)
        
        self.social_checks = {}
        social_items = ["対人緊張が高い", "友達との関わりに不安", "コミュニケーション苦手", "特に問題なし"]
        for i, item in enumerate(social_items):
            var = tk.BooleanVar()
            ttk.Checkbutton(social_issues_frame, text=item, variable=var).grid(row=i//2, column=i%2, sticky="w", padx=5)
            self.social_checks[item] = var
        
        # === セクション6：発達特性 ===
        dev_frame = ttk.LabelFrame(scrollable_frame, text="🧠 発達特性・医療情報", padding=15)
        dev_frame.pack(fill="x", padx=20, pady=10)
        
        self.dev_check_var = tk.BooleanVar()
        ttk.Checkbutton(dev_frame, text="発達特性または発達課題あり", variable=self.dev_check_var).grid(row=0, column=0, sticky="w", pady=5)
        
        ttk.Label(dev_frame, text="詳細:").grid(row=1, column=0, sticky="w", pady=5)
        self.dev_detail = ttk.Entry(dev_frame, width=50)
        self.dev_detail.grid(row=1, column=1, sticky="w", padx=5)
        
        self.medical_check_var = tk.BooleanVar(value=False)
        medical_check = ttk.Checkbutton(
            dev_frame,
            text="通院あり",
            variable=self.medical_check_var,
            command=self.toggle_medical_fields
        )
        medical_check.grid(row=2, column=0, sticky="w", pady=5)
        
        self.medical_detail_frame = ttk.Frame(dev_frame)
        self.medical_detail_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=5)
        self.medical_detail_frame.grid_remove()
        
        ttk.Label(self.medical_detail_frame, text="病院名:").grid(row=0, column=0, sticky="w", pady=3)
        self.hospital_entry = ttk.Entry(self.medical_detail_frame, width=30)
        self.hospital_entry.grid(row=0, column=1, sticky="w", padx=5)
        
        ttk.Label(self.medical_detail_frame, text="診断名:").grid(row=1, column=0, sticky="w", pady=3)
        self.diagnosis_entry = ttk.Entry(self.medical_detail_frame, width=30)
        self.diagnosis_entry.grid(row=1, column=1, sticky="w", padx=5)
        
        # === セクション7：家庭環境 ===
        family_frame = ttk.LabelFrame(scrollable_frame, text="👨‍👩‍👧‍👦 家庭環境", padding=15)
        family_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(family_frame, text="ひとり親世帯:").grid(row=0, column=0, sticky="w", pady=5)
        self.single_parent_var = tk.StringVar(value="該当しない")
        ttk.Radiobutton(family_frame, text="該当", variable=self.single_parent_var, value="該当").grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(family_frame, text="該当しない", variable=self.single_parent_var, value="該当しない").grid(row=0, column=2, sticky="w")
        
        ttk.Label(family_frame, text="家庭環境の課題:").grid(row=1, column=0, sticky="nw", pady=5)
        family_issues_frame = tk.Frame(family_frame)
        family_issues_frame.grid(row=1, column=1, columnspan=2, sticky="w", padx=5)
        
        self.family_checks = {}
        family_items = ["経済的困難", "家族関係の課題", "他の世帯員の問題", "特に問題なし"]
        for i, item in enumerate(family_items):
            var = tk.BooleanVar()
            ttk.Checkbutton(family_issues_frame, text=item, variable=var).grid(row=i//2, column=i%2, sticky="w", padx=5)
            self.family_checks[item] = var
        
        # === セクション8：本人・保護者のニーズ ===
        needs_frame = ttk.LabelFrame(scrollable_frame, text="🎯 ニーズ・目標", padding=15)
        needs_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(needs_frame, text="本人のニーズ:").grid(row=0, column=0, sticky="nw", pady=5)
        self.child_needs = scrolledtext.ScrolledText(needs_frame, width=50, height=3, wrap=tk.WORD)
        self.child_needs.grid(row=0, column=1, sticky="w", padx=5)
        self.child_needs.insert("1.0", "例：友達と話せるようになりたい")
        
        ttk.Label(needs_frame, text="保護者のニーズ:").grid(row=1, column=0, sticky="nw", pady=5)
        self.guardian_needs = scrolledtext.ScrolledText(needs_frame, width=50, height=3, wrap=tk.WORD)
        self.guardian_needs.grid(row=1, column=1, sticky="w", padx=5)
        self.guardian_needs.insert("1.0", "例：学校に戻ってほしい")
        
        ttk.Label(needs_frame, text="希望する進路:").grid(row=2, column=0, sticky="w", pady=5)
        self.future_path_var = tk.StringVar(value="進学")
        ttk.Radiobutton(needs_frame, text="進学", variable=self.future_path_var, value="進学").grid(row=2, column=1, sticky="w")
        ttk.Radiobutton(needs_frame, text="就職", variable=self.future_path_var, value="就職").grid(row=2, column=2, sticky="w")
        
        ttk.Label(needs_frame, text="進路の詳細:").grid(row=3, column=0, sticky="w", pady=5)
        self.future_path_detail = ttk.Entry(needs_frame, width=50)
        self.future_path_detail.grid(row=3, column=1, columnspan=2, sticky="w", padx=5)
        self.future_path_detail.insert(0, "例：高校進学を希望")
        
        # === セクション9：当日の様子（自由記述） ===
        memo_frame = ttk.LabelFrame(scrollable_frame, text="📝 当日の様子・その他メモ", padding=15)
        memo_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        hint_label = tk.Label(
            memo_frame,
            text="💡 服装、表情、会話の流れ、気になった点など自由に記録",
            fg="gray"
        )
        hint_label.pack(anchor="w", pady=(0, 5))
        
        self.memo_text = scrolledtext.ScrolledText(
            memo_frame,
            wrap=tk.WORD,
            width=80,
            height=8,
            font=("游ゴシック", 11)
        )
        self.memo_text.pack(fill="both", expand=True)
        
        # === ボタンエリア ===
        button_frame = tk.Frame(scrollable_frame)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        preview_btn = tk.Button(
            button_frame,
            text="👀 プレビュー",
            font=("游ゴシック", 11),
            command=self.show_preview,
            padx=15,
            pady=8
        )
        preview_btn.pack(side="left", padx=5)
        
        complete_btn = tk.Button(
            button_frame,
            text="✅ 完成・保存",
            font=("游ゴシック", 12, "bold"),
            bg="#7ED321",
            fg="white",
            command=self.on_complete_clicked,
            padx=20,
            pady=10
        )
        complete_btn.pack(side="right")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def toggle_medical_fields(self):
        """通院情報の表示/非表示切り替え"""
        if self.medical_check_var.get():
            self.medical_detail_frame.grid()
        else:
            self.medical_detail_frame.grid_remove()
    
    def show_preview(self):
        """プレビュー表示"""
        if not self.validate_input():
            return
        
        assessment_data = self.generate_assessment_data()
        messagebox.showinfo(
            "プレビュー",
            f"課題チェック数: {self.count_checked_issues()}件\n"
            f"本人ニーズ: {self.child_needs.get('1.0', tk.END).strip()[:30]}...\n"
            f"保護者ニーズ: {self.guardian_needs.get('1.0', tk.END).strip()[:30]}...\n\n"
            "「完成・保存」ボタンでアセスメントシートと報告書を作成します"
        )
    
    def count_checked_issues(self):
        """チェックされた課題の数をカウント"""
        count = 0
        if self.truancy_check.get():
            count += 1
        for var in self.rhythm_checks.values():
            if var.get():
                count += 1
        for var in self.habit_checks.values():
            if var.get():
                count += 1
        for var in self.study_checks.values():
            if var.get():
                count += 1
        for var in self.social_checks.values():
            if var.get():
                count += 1
        if self.dev_check_var.get():
            count += 1
        for var in self.family_checks.values():
            if var.get():
                count += 1
        return count
    
    def on_complete_clicked(self):
        """完成ボタンクリック時"""
        if not self.validate_input():
            return
        
        interview_data = self.get_interview_data()
        assessment_data = self.generate_assessment_data()
        
        self.on_complete_callback(interview_data, assessment_data)
    
    def validate_input(self):
        """入力チェック"""
        errors = []
        
        if not self.child_name_entry.get().strip():
            errors.append("・児童氏名を入力してください")
        
        if not self.school_entry.get().strip():
            errors.append("・学校名を入力してください")
        
        if errors:
            messagebox.showerror(
                "入力エラー",
                "以下の項目を入力してください:\n\n" + "\n".join(errors)
            )
            return False
        
        return True
    
    def get_interview_data(self):
        """入力データを収集"""
        data = {
            '児童氏名': self.child_name_entry.get().strip(),
            '保護者氏名': self.guardian_name_entry.get().strip(),
            '性別': self.gender_var.get(),
            '学校名': self.school_entry.get().strip(),
            '学年': int(self.grade_spinbox.get()),
            'ひとり親世帯': self.single_parent_var.get(),
            '担当支援員': self.supporter_entry.get().strip(),
            '面談実施日': datetime.strptime(
                self.interview_date_entry.get(),
                '%Y/%m/%d'
            ),
            'メモ': self.memo_text.get("1.0", tk.END).strip(),
            '面談時間': '未記録',
            '面談場所': '未記録',
            '通院状況': {}
        }
        
        if self.medical_check_var.get():
            data['通院状況'] = {
                '通院あり': True,
                '病院名': self.hospital_entry.get().strip(),
                '診断名': self.diagnosis_entry.get().strip(),
                '投薬': '',
                '頻度': ''
            }
        else:
            data['通院状況'] = {'通院あり': False}
        
        return data
    
    def generate_assessment_data(self):
        """アセスメントデータを生成"""
        issues = {}
        
        # 不登校
        issues["不登校"] = {
            "該当": self.truancy_check.get(),
            "詳細": f"{self.attendance_var.get()}。{self.truancy_detail.get('1.0', tk.END).strip()}"
        }
        
        # 引きこもり
        outing = self.outing_var.get()
        issues["引きこもり"] = {
            "該当": outing == "ほぼ外出しない",
            "詳細": outing
        }
        
        # 生活リズム
        rhythm_items = [k for k, v in self.rhythm_checks.items() if v.get()]
        issues["生活リズム"] = {
            "該当": len(rhythm_items) > 0 and "特に問題なし" not in rhythm_items,
            "詳細": "、".join(rhythm_items) if rhythm_items else "特に問題なし"
        }
        
        # 生活習慣
        habit_items = [k for k, v in self.habit_checks.items() if v.get()]
        issues["生活習慣"] = {
            "該当": len(habit_items) > 0 and "特に問題なし" not in habit_items,
            "詳細": "、".join(habit_items) if habit_items else "特に問題なし"
        }
        
        # 学習
        study_items = [k for k, v in self.study_checks.items() if v.get()]
        issues["学習の遅れ・低学力"] = {
            "該当": any(item in study_items for item in ["学習の遅れ", "低学力"]),
            "詳細": "、".join(study_items) if study_items else "特に問題なし"
        }
        
        issues["学習習慣・環境"] = {
            "該当": any(item in study_items for item in ["学習習慣なし", "学習環境なし"]),
            "詳細": "、".join(study_items) if study_items else "特に問題なし"
        }
        
        # 発達特性
        issues["発達特性or発達課題"] = {
            "該当": self.dev_check_var.get(),
            "詳細": self.dev_detail.get() if self.dev_check_var.get() else "該当なし"
        }
        
        # 対人関係
        social_items = [k for k, v in self.social_checks.items() if v.get()]
        issues["対人緊張の高さ"] = {
            "該当": "対人緊張が高い" in social_items or "友達との関わりに不安" in social_items,
            "詳細": "、".join(social_items) if social_items else "特に問題なし"
        }
        
        issues["コミュニケーションに苦手意識"] = {
            "該当": "コミュニケーション苦手" in social_items,
            "詳細": "、".join(social_items) if social_items else "特に問題なし"
        }
        
        # 家庭環境
        family_items = [k for k, v in self.family_checks.items() if v.get()]
        issues["家庭環境"] = {
            "該当": len(family_items) > 0 and "特に問題なし" not in family_items,
            "詳細": "、".join(family_items) if family_items else "特に問題なし"
        }
        
        issues["虐待"] = {"該当": False, "詳細": "該当なし"}
        issues["他の世帯員の問題"] = {
            "該当": "他の世帯員の問題" in family_items,
            "詳細": "他の世帯員の問題" if "他の世帯員の問題" in family_items else "該当なし"
        }
        issues["その他"] = {"該当": False, "詳細": ""}
        
        # ニーズと目標
        short_term_plan = {
            "課題": "、".join([k for k, v in issues.items() if v["該当"]])[:50],
            "現状": self.truancy_detail.get("1.0", tk.END).strip()[:100],
            "ニーズ_本人": self.child_needs.get("1.0", tk.END).strip(),
            "ニーズ_保護者": self.guardian_needs.get("1.0", tk.END).strip(),
            "目標": "段階的な支援を通じた自立",
            "方法": "定期的な面談と個別支援"
        }
        
        return {
            "issues": issues,
            "future_path": {
                "type": self.future_path_var.get(),
                "detail": self.future_path_detail.get()
            },
            "short_term_plan": short_term_plan,
            "long_term_plan": {
                "課題": "進路実現",
                "現状": self.future_path_detail.get(),
                "ニーズ_本人": self.child_needs.get("1.0", tk.END).strip(),
                "ニーズ_保護者": self.guardian_needs.get("1.0", tk.END).strip(),
                "目標": f"{self.future_path_var.get()}を目指す",
                "方法": "継続的な支援と進路相談"
            },
            "missing_info": []
        }
