import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime

class InputForm(tk.Frame):
    def __init__(self, parent, on_analyze_callback):
        super().__init__(parent)
        self.on_analyze_callback = on_analyze_callback
        self.create_widgets()
    
    def create_widgets(self):
        title = tk.Label(
            self,
            text="📝 新規面談記録",
            font=("游ゴシック", 18, "bold")
        )
        title.pack(pady=10)
        
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # マウスホイールスクロールを有効化
        def _on_canvas_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"  # 他のイベントハンドラに渡さない
        
        # Canvasに直接バインド
        canvas.bind("<MouseWheel>", _on_canvas_mousewheel)
        
        # 全体のスクロール用（テキストエリア以外）
        def _on_global_mousewheel(event):
            # マウスがテキストエリア上にあるかチェック
            widget = event.widget
            if not isinstance(widget, (scrolledtext.ScrolledText, tk.Text)):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # 全体にバインド
        self.bind_all("<MouseWheel>", _on_global_mousewheel)
        
        basic_frame = ttk.LabelFrame(scrollable_frame, text="基本情報", padding=15)
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
        ttk.Label(basic_frame, text="ひとり親世帯:").grid(row=row, column=0, sticky="w", pady=5)
        self.single_parent_var = tk.StringVar(value="該当しない")
        ttk.Radiobutton(basic_frame, text="該当", variable=self.single_parent_var, value="該当").grid(row=row, column=1, sticky="w")
        ttk.Radiobutton(basic_frame, text="該当しない", variable=self.single_parent_var, value="該当しない").grid(row=row, column=2, sticky="w")
        
        row += 1
        ttk.Label(basic_frame, text="担当支援員:").grid(row=row, column=0, sticky="w", pady=5)
        self.supporter_entry = ttk.Entry(basic_frame, width=20)
        self.supporter_entry.grid(row=row, column=1, sticky="w", padx=5)
        
        ttk.Label(basic_frame, text="面談実施日:").grid(row=row, column=2, sticky="w", padx=(20, 5))
        self.interview_date_entry = ttk.Entry(basic_frame, width=15)
        self.interview_date_entry.insert(0, datetime.now().strftime('%Y/%m/%d'))
        self.interview_date_entry.grid(row=row, column=3, columnspan=2, sticky="w")
        
        medical_frame = ttk.LabelFrame(scrollable_frame, text="医療・支援情報", padding=15)
        medical_frame.pack(fill="x", padx=20, pady=10)
        
        # チェックボックスエリア
        checkbox_frame = tk.Frame(medical_frame)
        checkbox_frame.pack(fill="x", pady=(0, 10))
        
        # 通院
        self.medical_check_var = tk.BooleanVar(value=False)
        medical_check = ttk.Checkbutton(
            checkbox_frame,
            text="通院あり",
            variable=self.medical_check_var,
            command=self.toggle_medical_fields
        )
        medical_check.grid(row=0, column=0, sticky="w", pady=5, padx=(0, 20))
        
        # 投薬治療
        self.medication_check_var = tk.BooleanVar(value=False)
        medication_check = ttk.Checkbutton(
            checkbox_frame,
            text="投薬治療",
            variable=self.medication_check_var,
            command=self.toggle_medication_fields
        )
        medication_check.grid(row=0, column=1, sticky="w", pady=5, padx=(0, 20))
        
        # 診断
        self.diagnosis_check_var = tk.BooleanVar(value=False)
        diagnosis_check = ttk.Checkbutton(
            checkbox_frame,
            text="診断あり",
            variable=self.diagnosis_check_var,
            command=self.toggle_diagnosis_fields
        )
        diagnosis_check.grid(row=0, column=2, sticky="w", pady=5, padx=(0, 20))
        
        # 手帳
        self.disability_book_check_var = tk.BooleanVar(value=False)
        disability_book_check = ttk.Checkbutton(
            checkbox_frame,
            text="手帳あり",
            variable=self.disability_book_check_var,
            command=self.toggle_disability_book_fields
        )
        disability_book_check.grid(row=0, column=3, sticky="w", pady=5)
        
        # 通院詳細（病院名と頻度）
        self.medical_detail_frame = tk.Frame(medical_frame)
        self.medical_detail_frame.pack(fill="x", pady=(0, 5))
        self.medical_detail_frame.pack_forget()
        
        ttk.Label(self.medical_detail_frame, text="病院名:").pack(side="left", padx=(0, 5))
        self.hospital_entry = ttk.Entry(self.medical_detail_frame, width=25)
        self.hospital_entry.pack(side="left", padx=(0, 10))
        
        ttk.Label(self.medical_detail_frame, text="頻度:").pack(side="left", padx=(0, 5))
        self.frequency_entry = ttk.Entry(self.medical_detail_frame, width=15)
        self.frequency_entry.pack(side="left")
        
        # 投薬治療詳細（薬名のみ）
        self.medication_detail_frame = tk.Frame(medical_frame)
        self.medication_detail_frame.pack(fill="x", pady=(0, 5))
        self.medication_detail_frame.pack_forget()
        
        ttk.Label(self.medication_detail_frame, text="薬名:").pack(side="left", padx=(0, 5))
        self.medication_name_entry = ttk.Entry(self.medication_detail_frame, width=30)
        self.medication_name_entry.pack(side="left")
        
        # 診断詳細（診断名のみ）
        self.diagnosis_detail_frame = tk.Frame(medical_frame)
        self.diagnosis_detail_frame.pack(fill="x", pady=(0, 5))
        self.diagnosis_detail_frame.pack_forget()
        
        ttk.Label(self.diagnosis_detail_frame, text="診断名:").pack(side="left", padx=(0, 5))
        self.diagnosis_name_entry = ttk.Entry(self.diagnosis_detail_frame, width=30)
        self.diagnosis_name_entry.pack(side="left")
        
        # 手帳詳細（手帳種類のみ）
        self.disability_book_detail_frame = tk.Frame(medical_frame)
        self.disability_book_detail_frame.pack(fill="x", pady=(0, 5))
        self.disability_book_detail_frame.pack_forget()
        
        ttk.Label(self.disability_book_detail_frame, text="手帳種類:").pack(side="left", padx=(0, 5))
        self.disability_book_type_entry = ttk.Entry(self.disability_book_detail_frame, width=30)
        self.disability_book_type_entry.pack(side="left")
        
        memo_frame = ttk.LabelFrame(scrollable_frame, text="面談メモ", padding=15)
        memo_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # テンプレート挿入ボタン
        template_btn = tk.Button(
            memo_frame,
            text="📝 質問項目テンプレートを挿入",
            font=("游ゴシック", 10),
            bg="#E8F4F8",
            command=self.insert_template,
            padx=15,
            pady=8,
            relief="raised"
        )
        template_btn.pack(anchor="w", pady=(0, 10))
        
        # メモ入力エリア
        self.memo_text = scrolledtext.ScrolledText(
            memo_frame,
            wrap=tk.WORD,
            width=80,
            height=15,
            font=("游ゴシック", 11)
        )
        self.memo_text.pack(fill="both", expand=True)
        
        # 面談メモのホイールスクロール設定
        def _on_memo_mousewheel(event):
            self.memo_text.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"  # 他のイベントハンドラに渡さない
        
        # 面談メモに直接バインド
        self.memo_text.bind("<MouseWheel>", _on_memo_mousewheel)
        
        self.char_count_label = tk.Label(memo_frame, text="文字数: 0", fg="gray")
        self.char_count_label.pack(anchor="e", pady=(5, 0))
        self.memo_text.bind("<KeyRelease>", self.update_char_count)
        
        # 支援希望セクション
        support_frame = ttk.LabelFrame(scrollable_frame, text="支援への希望", padding=15)
        support_frame.pack(fill="x", padx=20, pady=10)
        
        # 支援希望の詳細入力
        support_details_frame = tk.Frame(support_frame)
        support_details_frame.pack(fill="x", pady=(0, 10))
        
        # 曜日
        tk.Label(support_details_frame, text="希望の曜日:", font=("游ゴシック", 10)).pack(anchor="w", pady=(0, 5))
        self.support_day_entry = ttk.Entry(support_details_frame, width=70)
        self.support_day_entry.pack(anchor="w", pady=(0, 10))
        
        # 時間帯
        tk.Label(support_details_frame, text="希望の時間帯:", font=("游ゴシック", 10)).pack(anchor="w", pady=(0, 5))
        self.support_time_entry = ttk.Entry(support_details_frame, width=70)
        self.support_time_entry.pack(anchor="w", pady=(0, 10))
        
        # 場所
        tk.Label(support_details_frame, text="希望の場所:", font=("游ゴシック", 10)).pack(anchor="w", pady=(0, 5))
        self.support_location_entry = ttk.Entry(support_details_frame, width=70)
        self.support_location_entry.pack(anchor="w", pady=(0, 10))
        
        # 支援員選択
        staff_frame = tk.Frame(support_details_frame)
        staff_frame.pack(anchor="w", pady=(0, 10))
        
        tk.Label(staff_frame, text="希望の支援員:", font=("游ゴシック", 10)).pack(side="left", pady=(0, 5))
        
        self.support_staff_entry = ttk.Entry(staff_frame, width=50)
        self.support_staff_entry.pack(side="left", padx=(5, 5))
        
        select_staff_btn = tk.Button(
            staff_frame,
            text="👥 支援員を選択",
            font=("游ゴシック", 9),
            bg="#3498db",
            fg="white",
            command=self.select_staff,
            padx=10,
            pady=5
        )
        select_staff_btn.pack(side="left")
        
        # 解決したいこと
        tk.Label(support_details_frame, text="解決したいこと:", font=("游ゴシック", 10)).pack(anchor="w", pady=(0, 5))
        self.support_goals_text = scrolledtext.ScrolledText(
            support_details_frame,
            wrap=tk.WORD,
            width=70,
            height=4,
            font=("游ゴシック", 10)
        )
        self.support_goals_text.pack(anchor="w")
        
        # 支援希望テキストのホイールスクロール設定
        def _on_support_mousewheel(event):
            self.support_goals_text.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"  # 他のイベントハンドラに渡さない
        
        # 支援希望テキストに直接バインド
        self.support_goals_text.bind("<MouseWheel>", _on_support_mousewheel)
        
        button_frame = tk.Frame(scrollable_frame)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        analyze_btn = tk.Button(
            button_frame,
            text="🔍 AI分析を実行",
            font=("游ゴシック", 12, "bold"),
            bg="#4A90E2",
            fg="white",
            command=self.on_analyze_clicked,
            padx=20,
            pady=10
        )
        analyze_btn.pack(side="right")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def toggle_medical_fields(self):
        if self.medical_check_var.get():
            self.medical_detail_frame.pack(fill="x", pady=(0, 5))
        else:
            self.medical_detail_frame.pack_forget()
    
    def toggle_medication_fields(self):
        if self.medication_check_var.get():
            self.medication_detail_frame.pack(fill="x", pady=(0, 5))
        else:
            self.medication_detail_frame.pack_forget()
    
    def toggle_diagnosis_fields(self):
        if self.diagnosis_check_var.get():
            self.diagnosis_detail_frame.pack(fill="x", pady=(0, 5))
        else:
            self.diagnosis_detail_frame.pack_forget()
    
    def toggle_disability_book_fields(self):
        if self.disability_book_check_var.get():
            self.disability_book_detail_frame.pack(fill="x", pady=(0, 5))
        else:
            self.disability_book_detail_frame.pack_forget()
    
    def insert_template(self):
        """質問項目テンプレートをメモ欄に挿入"""
        template = """【登校状況】
・現在の登校頻度：週　回
・不登校が始まった時期：
・きっかけ：

【生活リズム】
・起床時間：
・就寝時間：
・昼夜逆転の有無：

【学習状況】
・家での学習：
・学習への意欲：
・得意な教科：
・苦手な教科：

【対人関係】
・友達との関わり：
・コミュニケーション：
・集団での様子：

【本人の趣味・好きなこと】
・好きなゲーム/アプリ：
・好きな音楽/動画：
・好きな活動：
・興味のあること：

【本人の気持ち】
・今の気持ち：
・将来どうなりたいか：
・やりたいこと：

【保護者の希望】
・どうしてほしいか：
・心配していること：

【進路希望】
・進学/就職の希望：
・具体的な目標：

【その他・気になること】
・

"""
        # 現在のカーソル位置に挿入
        self.memo_text.insert(tk.INSERT, template)
        self.update_char_count()
    
    def update_char_count(self, event=None):
        text = self.memo_text.get("1.0", tk.END)
        char_count = len(text.strip())
        self.char_count_label.config(text=f"文字数: {char_count}")
    
    def select_staff(self):
        """支援員選択ダイアログを開く"""
        try:
            from src.ui.staff_selector import StaffSelectorDialog
            
            # 現在の支援希望を取得
            support_wishes = {
                '希望の曜日': self.support_day_entry.get().strip(),
                '希望の時間帯': self.support_time_entry.get().strip(),
                '希望の場所': self.support_location_entry.get().strip(),
                '解決したいこと': self.support_goals_text.get("1.0", tk.END).strip()
            }
            
            # 支援員選択ダイアログを開く
            dialog = StaffSelectorDialog(self, support_wishes)
            self.wait_window(dialog)
            
            # 選択された支援員を取得
            selected_staff = dialog.get_selected_staff()
            if selected_staff:
                self.support_staff_entry.delete(0, tk.END)
                self.support_staff_entry.insert(0, selected_staff['name'])
                
        except ImportError as e:
            from tkinter import messagebox
            messagebox.showerror("エラー", f"支援員選択機能の読み込みに失敗しました：\n{str(e)}")
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("エラー", f"支援員選択中にエラーが発生しました：\n{str(e)}")
    
    def on_analyze_clicked(self):
        if not self.validate_input():
            return
        
        interview_data = self.get_interview_data()
        self.on_analyze_callback(interview_data)
    
    def validate_input(self):
        errors = []
        
        if not self.child_name_entry.get().strip():
            errors.append("・児童氏名を入力してください")
        
        if not self.school_entry.get().strip():
            errors.append("・学校名を入力してください")
        
        if not self.memo_text.get("1.0", tk.END).strip():
            errors.append("・面談メモを入力してください")
        
        if errors:
            messagebox.showerror(
                "入力エラー",
                "以下の項目を入力してください:\n\n" + "\n".join(errors)
            )
            return False
        
        return True
    
    def get_interview_data(self):
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
            '通院状況': {},
            '支援希望': {
                '希望の曜日': self.support_day_entry.get().strip(),
                '希望の時間帯': self.support_time_entry.get().strip(),
                '希望の場所': self.support_location_entry.get().strip(),
                '希望の支援員': self.support_staff_entry.get().strip(),
                '解決したいこと': self.support_goals_text.get("1.0", tk.END).strip()
            }
        }
        
        # 医療・支援情報の統合
        medical_info = {'通院あり': False, '投薬治療': False, '診断あり': False, '手帳あり': False}
        
        if self.medical_check_var.get():
            medical_info.update({
                '通院あり': True,
                '病院名': self.hospital_entry.get().strip(),
                '頻度': self.frequency_entry.get().strip()
            })
        
        if self.medication_check_var.get():
            medical_info.update({
                '投薬治療': True,
                '薬名': self.medication_name_entry.get().strip()
            })
        
        if self.diagnosis_check_var.get():
            medical_info.update({
                '診断あり': True,
                '診断名': self.diagnosis_name_entry.get().strip()
            })
        
        if self.disability_book_check_var.get():
            medical_info.update({
                '手帳あり': True,
                '手帳種類': self.disability_book_type_entry.get().strip()
            })
        
        data['通院状況'] = medical_info
        
        return data

