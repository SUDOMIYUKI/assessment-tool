import tkinter as tk
from tkinter import ttk, messagebox
from src.database.staff import StaffManager

class StaffManagerDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.staff_manager = StaffManager()
        self.current_staff_id = None
        self.selected_staff_id = None
        
        self.title("支援員管理")
        self.geometry("1200x700")
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        
        # 中央に配置
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f'+{x}+{y}')
    
    def create_widgets(self):
        # ヘッダー
        header_frame = tk.Frame(self, bg="#9b59b6", height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame, 
            text="支援員管理システム", 
            font=("游ゴシック", 16, "bold"), 
            fg="white", 
            bg="#9b59b6"
        )
        title_label.pack(expand=True)
        
        # メインコンテンツ
        main_content = tk.Frame(self)
        main_content.pack(fill="both", expand=True, padx=10, pady=10)

        
        # 支援員管理画面
        self.create_staff_management_view(main_content)

    def create_staff_management_view(self, parent):
        """支援員管理ビュー"""
        
        main_frame = tk.Frame(parent)
        main_frame.pack(fill="both", expand=True)
        
        # 左側：支援員一覧
        left_frame = ttk.LabelFrame(main_frame, text="支援員一覧", padding=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # ツリービュー
        columns = ('name', 'age', 'gender', 'region', 'is_active')
        self.staff_tree = ttk.Treeview(left_frame, columns=columns, show='headings', height=15)
        
        self.staff_tree.heading('name', text='名前')
        self.staff_tree.heading('age', text='年齢')
        self.staff_tree.heading('gender', text='性別')
        self.staff_tree.heading('region', text='地域')
        self.staff_tree.heading('is_active', text='状態')
        
        self.staff_tree.column('name', width=100)
        self.staff_tree.column('age', width=50)
        self.staff_tree.column('gender', width=60)
        self.staff_tree.column('region', width=120)
        self.staff_tree.column('is_active', width=60)
        
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.staff_tree.yview)
        self.staff_tree.configure(yscrollcommand=scrollbar.set)
        
        self.staff_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.staff_tree.bind('<<TreeviewSelect>>', self.on_staff_tree_selected)
        
        # 右側：詳細フォームとケース一覧
        right_frame = ttk.LabelFrame(main_frame, text="支援員詳細", padding=5)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # フォーム
        form_frame = tk.Frame(right_frame, bg="white")
        form_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 2列レイアウト
        left_col = tk.Frame(form_frame, bg="white")
        left_col.grid(row=0, column=0, sticky="nw", padx=(0, 10))
        
        right_col = tk.Frame(form_frame, bg="white")
        right_col.grid(row=0, column=1, sticky="nw")
        
        # 左列のフォーム項目
        row = 0
        
        # 名前
        tk.Label(left_col, text="名前:", font=("游ゴシック", 9)).grid(row=row, column=0, sticky="w", pady=2)
        self.staff_name_var = tk.StringVar()
        tk.Entry(left_col, textvariable=self.staff_name_var, width=20, font=("游ゴシック", 9)).grid(row=row, column=1, sticky="w", padx=(5, 0), pady=2)
        
        row += 1
        tk.Label(left_col, text="年齢:", font=("游ゴシック", 9)).grid(row=row, column=0, sticky="w", pady=2)
        self.staff_age_var = tk.StringVar()
        tk.Entry(left_col, textvariable=self.staff_age_var, width=20, font=("游ゴシック", 9)).grid(row=row, column=1, sticky="w", padx=(5, 0), pady=2)
        
        row += 1
        tk.Label(left_col, text="性別:", font=("游ゴシック", 9)).grid(row=row, column=0, sticky="w", pady=2)
        self.staff_gender_var = tk.StringVar()
        gender_combo = ttk.Combobox(left_col, textvariable=self.staff_gender_var, values=["男性", "女性"], width=17, state="readonly")
        gender_combo.grid(row=row, column=1, sticky="w", padx=(5, 0), pady=2)
        
        row += 1
        tk.Label(left_col, text="居住地域:", font=("游ゴシック", 9)).grid(row=row, column=0, sticky="w", pady=2)
        self.staff_district_var = tk.StringVar()
        
        # 居住地域の入力フィールド（自由入力）
        tk.Entry(left_col, textvariable=self.staff_district_var, width=20, font=("游ゴシック", 9)).grid(row=row, column=1, sticky="w", padx=(5, 0), pady=2)
        
        row += 1
        tk.Label(left_col, text="前職:", font=("游ゴシック", 9)).grid(row=row, column=0, sticky="w", pady=2)
        self.staff_previous_job_var = tk.StringVar()
        tk.Entry(left_col, textvariable=self.staff_previous_job_var, width=20, font=("游ゴシック", 9)).grid(row=row, column=1, sticky="w", padx=(5, 0), pady=2)
        
        row += 1
        tk.Label(left_col, text="Dropbox番号:", font=("游ゴシック", 9)).grid(row=row, column=0, sticky="w", pady=2)
        self.staff_dropbox_var = tk.StringVar()
        tk.Entry(left_col, textvariable=self.staff_dropbox_var, width=20, font=("游ゴシック", 9)).grid(row=row, column=1, sticky="w", padx=(5, 0), pady=2)
        
        # 右列のフォーム項目
        row = 0
        
        tk.Label(right_col, text="趣味・特技:", font=("游ゴシック", 9)).grid(row=row, column=0, sticky="nw", pady=2)
        self.staff_hobbies_text = tk.Text(right_col, width=25, height=4, wrap=tk.WORD, font=("游ゴシック", 9))
        self.staff_hobbies_text.grid(row=row, column=1, sticky="w", padx=(5, 0), pady=2)
        
        row += 1
        tk.Label(right_col, text="勤務曜日:", font=("游ゴシック", 9)).grid(row=row, column=0, sticky="nw", pady=2)
        work_days_frame = tk.Frame(right_col)
        work_days_frame.grid(row=row, column=1, sticky="w", padx=(5, 0), pady=2)
        
        self.work_days_vars = {}
        days = ['月', '火', '水', '木', '金']
        for i, day in enumerate(days):
            self.work_days_vars[day] = tk.BooleanVar()
            ttk.Checkbutton(work_days_frame, text=day, variable=self.work_days_vars[day]).grid(row=0, column=i, padx=2, sticky="w")
        
        row += 1
        tk.Label(right_col, text="勤務時間:", font=("游ゴシック", 9)).grid(row=row, column=0, sticky="w", pady=2)
        work_hours_frame = tk.Frame(right_col)
        work_hours_frame.grid(row=row, column=1, sticky="w", padx=(5, 0), pady=2)
        
        tk.Label(work_hours_frame, text="開始:", font=("游ゴシック", 8)).pack(side="left", padx=(0, 2))
        self.staff_start_time_var = tk.StringVar()
        tk.Entry(work_hours_frame, textvariable=self.staff_start_time_var, width=6, font=("游ゴシック", 8)).pack(side="left", padx=(0, 5))
        
        tk.Label(work_hours_frame, text="終了:", font=("游ゴシック", 8)).pack(side="left", padx=(0, 2))
        self.staff_end_time_var = tk.StringVar()
        tk.Entry(work_hours_frame, textvariable=self.staff_end_time_var, width=6, font=("游ゴシック", 8)).pack(side="left")
        
        # ボタン
        button_frame = tk.Frame(form_frame, bg="white")
        button_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")
        
        tk.Button(
            button_frame,
            text="新規追加",
            font=("游ゴシック", 9, "bold"),
            bg="#3498db",
            fg="white",
            command=self.save_staff_new,
            padx=15,
            pady=5
        ).pack(side="left", padx=5)
        
        tk.Button(
            button_frame,
            text="保存",
            font=("游ゴシック", 9, "bold"),
            bg="#27ae60",
            fg="white",
            command=self.save_staff_update,
            padx=15,
            pady=5
        ).pack(side="left", padx=5)
        
        tk.Button(
            button_frame,
            text="削除",
            font=("游ゴシック", 9, "bold"),
            bg="#e74c3c",
            fg="white",
            command=self.delete_staff_confirm,
            padx=15,
            pady=5
        ).pack(side="left", padx=5)
        
        tk.Button(
            button_frame,
            text="スケジュール表示",
            font=("游ゴシック", 9, "bold"),
            bg="#9b59b6",
            fg="white",
            command=self.open_schedule_window,
            padx=15,
            pady=5
        ).pack(side="left", padx=5)
        
        # ケース一覧
        case_frame = ttk.LabelFrame(right_frame, text="ケース一覧", padding=5)
        case_frame.pack(fill="both", expand=True, pady=(5, 0))
        
        # ケース追加ボタン
        add_case_btn = tk.Button(
            case_frame,
            text="+ ケース追加",
            font=("游ゴシック", 9, "bold"),
            bg="#27ae60",
            fg="white",
            command=self.open_add_case_dialog,
            padx=10,
            pady=5
        )
        add_case_btn.pack(pady=(0, 5))
        
        # ケース一覧のツリービュー
        case_columns = ('case_number', 'district', 'schedule', 'frequency', 'location')
        self.case_tree = ttk.Treeview(case_frame, columns=case_columns, show='headings', height=8)
        
        self.case_tree.heading('case_number', text='ケース番号')
        self.case_tree.heading('district', text='区')
        self.case_tree.heading('schedule', text='日程・時間')
        self.case_tree.heading('frequency', text='頻度')
        self.case_tree.heading('location', text='場所')
        
        self.case_tree.column('case_number', width=80)
        self.case_tree.column('district', width=80)
        self.case_tree.column('schedule', width=100)
        self.case_tree.column('frequency', width=60)
        self.case_tree.column('location', width=80)
        
        case_scrollbar = ttk.Scrollbar(case_frame, orient="vertical", command=self.case_tree.yview)
        self.case_tree.configure(yscrollcommand=case_scrollbar.set)
        
        self.case_tree.pack(side="left", fill="both", expand=True)
        case_scrollbar.pack(side="right", fill="y")
        
        # 右クリックメニュー
        self.case_context_menu = tk.Menu(self, tearoff=0)
        self.case_context_menu.add_command(label="削除", command=self.delete_case_item)
        
        self.case_tree.bind("<Button-3>", self.show_case_context_menu)
        
        # 初期データ読み込み
        self.refresh_staff_tree()

    def refresh_staff_tree(self):
        """支援員一覧を更新"""
        try:
            for item in self.staff_tree.get_children():
                self.staff_tree.delete(item)
            
            staff_list = self.staff_manager.get_all_staff()
            for staff in staff_list:
                self.staff_tree.insert('', 'end', values=(
                    staff['name'],
                    staff['age'],
                    staff['gender'],
                    staff['region'],
                    'アクティブ' if staff['is_active'] else '非アクティブ'
                ), tags=(staff['id'],))
        except Exception as e:
            print(f"refresh_staff_tree エラー: {e}")
    
    def on_staff_tree_selected(self, event):
        """支援員が選択された時"""
        try:
            selection = self.staff_tree.selection()
            if selection:
                item = self.staff_tree.item(selection[0])
                tags = item.get('tags', [])
                if tags and len(tags) > 0:
                    staff_id = tags[0]
                    if staff_id and staff_id != 'None':
                        self.selected_staff_id = staff_id
                        self.load_staff_details(staff_id)
                        # ケース一覧を更新
                        self.refresh_case_list()
        except Exception as e:
            print(f"on_staff_tree_selected エラー: {e}")

    def load_staff_details(self, staff_id):
        """支援員詳細を読み込み"""
        try:
            staff = self.staff_manager.get_staff_by_id(staff_id)
            if not staff:
                return
            
            self.current_staff_id = staff_id
            
            # フォームに値を設定
            self.staff_name_var.set(staff.get('name', ''))
            self.staff_age_var.set(staff.get('age', ''))
            self.staff_gender_var.set(staff.get('gender', ''))
            
            # 居住地域の設定
            self.staff_district_var.set(staff.get('region', ''))
            
            # 趣味・特技
            self.staff_hobbies_text.delete(1.0, tk.END)
            self.staff_hobbies_text.insert(1.0, staff.get('hobbies_skills', ''))
            
            # 前職
            self.staff_previous_job_var.set(staff.get('previous_job', ''))
            
            # Dropbox番号
            self.staff_dropbox_var.set(staff.get('dropbox_number', ''))
            
            # 勤務曜日
            work_days = staff.get('work_days', '')
            for day in ['月', '火', '水', '木', '金']:
                self.work_days_vars[day].set(day in work_days)
                
            # 勤務時間
            work_hours = staff.get('work_hours', '')
            if '-' in work_hours:
                start_time, end_time = work_hours.split('-', 1)
                self.staff_start_time_var.set(start_time.strip())
                self.staff_end_time_var.set(end_time.strip())
            else:
                self.staff_start_time_var.set('')
                self.staff_end_time_var.set('')
                
        except Exception as e:
            print(f"load_staff_details エラー: {e}")

    def refresh_case_list(self, event=None):
        """ケース一覧を更新"""
        try:
            # 既存のアイテムをクリア
            for item in self.case_tree.get_children():
                self.case_tree.delete(item)
            
            # 選択された支援員のケースのみを表示
            if self.selected_staff_id:
                cases = self.staff_manager.get_staff_with_cases(self.selected_staff_id)
                for case in cases:
                    self.case_tree.insert('', 'end', values=(
                        case.get('case_number', ''),
                        case.get('district_name', ''),
                        f"{case.get('schedule_day', '')} {case.get('schedule_time', '')}",
                        case.get('frequency', ''),
                        case.get('location', '')
                    ), tags=(case.get('id'),))
        except Exception as e:
            print(f"refresh_case_list エラー: {e}")
            # エラーが発生した場合は空のリストを表示
            pass

    def show_case_context_menu(self, event):
        """右クリックメニューを表示"""
        item = self.case_tree.identify_row(event.y)
        if item:
            self.case_tree.selection_set(item)
            self.case_context_menu.post(event.x_root, event.y_root)

    def delete_case_item(self):
        """ケース項目を削除"""
        selection = self.case_tree.selection()
        if selection:
            result = messagebox.askyesno("確認", "このケースを削除しますか？")
            if result:
                case_id = self.case_tree.item(selection[0])['tags'][0]
                self.refresh_case_list()

    def open_add_case_dialog(self):
        """ケース追加ダイアログを開く"""
        if not self.selected_staff_id:
            messagebox.showwarning("警告", "支援員を選択してください")
            return
        
        # ケース追加ダイアログを開く
        case_dialog = tk.Toplevel(self)
        case_dialog.title("ケース追加")
        case_dialog.geometry("500x600")
        case_dialog.transient(self)
        case_dialog.grab_set()
        
        # 中央に配置
        case_dialog.update_idletasks()
        x = (case_dialog.winfo_screenwidth() // 2) - (case_dialog.winfo_width() // 2)
        y = (case_dialog.winfo_screenheight() // 2) - (case_dialog.winfo_height() // 2)
        case_dialog.geometry(f'+{x}+{y}')
        
        # メインフレーム
        main_frame = tk.Frame(case_dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # タイトル
        title_label = tk.Label(main_frame, text="ケース情報を入力してください", font=("游ゴシック", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # スクロール可能なフレーム
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # フォーム項目
        form_frame = tk.Frame(scrollable_frame)
        form_frame.pack(fill="both", expand=True)
        
        # 区（最初の入力項目）
        district_frame = tk.Frame(form_frame)
        district_frame.pack(fill="x", pady=5)
        tk.Label(district_frame, text="区:", font=("游ゴシック", 10), width=15, anchor="w").pack(side="left")
        district_var = tk.StringVar()
        try:
            districts = self.staff_manager.get_all_districts()
            district_names = [d['name'] for d in districts]
        except Exception as e:
            print(f"区取得エラー: {e}")
            district_names = ["城東区", "鶴見区", "天王寺区", "中央区", "浪速区", "生野区", "東成区", "阿倍野区", "平野区", "住吉区", "東住吉区", "西成区"]
        
        district_combo = ttk.Combobox(district_frame, textvariable=district_var, values=district_names, width=27, state="readonly")
        district_combo.pack(side="left", padx=(10, 0))
        
        # ケース番号（2番目の入力項目）
        case_frame1 = tk.Frame(form_frame)
        case_frame1.pack(fill="x", pady=5)
        tk.Label(case_frame1, text="ケース番号:", font=("游ゴシック", 10), width=15, anchor="w").pack(side="left")
        case_number_var = tk.StringVar()
        tk.Entry(case_frame1, textvariable=case_number_var, width=30, font=("游ゴシック", 10)).pack(side="left", padx=(10, 0))
        
        # 電話番号
        phone_frame = tk.Frame(form_frame)
        phone_frame.pack(fill="x", pady=5)
        tk.Label(phone_frame, text="電話番号:", font=("游ゴシック", 10), width=15, anchor="w").pack(side="left")
        phone_number_var = tk.StringVar()
        tk.Entry(phone_frame, textvariable=phone_number_var, width=30, font=("游ゴシック", 10)).pack(side="left", padx=(10, 0))
        
        # 児童氏名
        child_frame = tk.Frame(form_frame)
        child_frame.pack(fill="x", pady=5)
        tk.Label(child_frame, text="児童氏名:", font=("游ゴシック", 10), width=15, anchor="w").pack(side="left")
        child_name_var = tk.StringVar()
        tk.Entry(child_frame, textvariable=child_name_var, width=30, font=("游ゴシック", 10)).pack(side="left", padx=(10, 0))
        
        # 日程
        day_frame = tk.Frame(form_frame)
        day_frame.pack(fill="x", pady=5)
        tk.Label(day_frame, text="日程:", font=("游ゴシック", 10), width=15, anchor="w").pack(side="left")
        schedule_day_var = tk.StringVar()
        day_combo = ttk.Combobox(day_frame, textvariable=schedule_day_var, values=["月", "火", "水", "木", "金"], width=27, state="readonly")
        day_combo.pack(side="left", padx=(10, 0))
        
        # 時間
        time_frame = tk.Frame(form_frame)
        time_frame.pack(fill="x", pady=5)
        tk.Label(time_frame, text="時間:", font=("游ゴシック", 10), width=15, anchor="w").pack(side="left")
        schedule_time_var = tk.StringVar()
        tk.Entry(time_frame, textvariable=schedule_time_var, width=30, font=("游ゴシック", 10)).pack(side="left", padx=(10, 0))
        
        # 場所
        location_frame = tk.Frame(form_frame)
        location_frame.pack(fill="x", pady=5)
        tk.Label(location_frame, text="場所:", font=("游ゴシック", 10), width=15, anchor="w").pack(side="left")
        location_var = tk.StringVar()
        tk.Entry(location_frame, textvariable=location_var, width=30, font=("游ゴシック", 10)).pack(side="left", padx=(10, 0))
        
        # 初回面談日
        meeting_frame = tk.Frame(form_frame)
        meeting_frame.pack(fill="x", pady=5)
        tk.Label(meeting_frame, text="初回面談日:", font=("游ゴシック", 10), width=15, anchor="w").pack(side="left")
        first_meeting_var = tk.StringVar()
        tk.Entry(meeting_frame, textvariable=first_meeting_var, width=30, font=("游ゴシック", 10)).pack(side="left", padx=(10, 0))
        
        # 頻度
        freq_frame = tk.Frame(form_frame)
        freq_frame.pack(fill="x", pady=5)
        tk.Label(freq_frame, text="頻度:", font=("游ゴシック", 10), width=15, anchor="w").pack(side="left")
        frequency_var = tk.StringVar()
        frequency_combo = ttk.Combobox(freq_frame, textvariable=frequency_var, values=["週1回", "週2回", "月1回", "月2回", "その他"], width=27, state="readonly")
        frequency_combo.pack(side="left", padx=(10, 0))
        
        # 備考
        notes_frame = tk.Frame(form_frame)
        notes_frame.pack(fill="x", pady=5)
        tk.Label(notes_frame, text="備考:", font=("游ゴシック", 10), width=15, anchor="nw").pack(side="left", anchor="nw")
        notes_text = tk.Text(notes_frame, width=30, height=4, wrap=tk.WORD, font=("游ゴシック", 10))
        notes_text.pack(side="left", padx=(10, 0))
        
        # ボタン（フォーム内に配置）
        button_frame = tk.Frame(form_frame)
        button_frame.pack(fill="x", pady=20)
        
        # スクロールバーとキャンバスを配置
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def save_case():
            try:
                # 必須項目のチェック
                if not case_number_var.get().strip():
                    messagebox.showwarning("警告", "ケース番号を入力してください")
                    return
                
                if not district_var.get():
                    messagebox.showwarning("警告", "区を選択してください")
                    return
                
                if not child_name_var.get().strip():
                    messagebox.showwarning("警告", "児童氏名を入力してください")
                    return
                
                # 区のIDを取得
                district_id = None
                for district in districts:
                    if district['name'] == district_var.get():
                        district_id = district['id']
                        break
                
                if not district_id:
                    messagebox.showerror("エラー", "選択された区が見つかりません")
                    return
                
                # ケースデータを作成
                case_data = {
                    'case_number': case_number_var.get().strip(),
                    'district_id': district_id,
                    'phone_number': phone_number_var.get().strip(),
                    'child_name': child_name_var.get().strip(),
                    'schedule_day': schedule_day_var.get(),
                    'schedule_time': schedule_time_var.get().strip(),
                    'location': location_var.get().strip(),
                    'first_meeting_date': first_meeting_var.get().strip(),
                    'frequency': frequency_var.get(),
                    'notes': notes_text.get(1.0, tk.END).strip()
                }
                
                # ケースを追加
                case_id = self.staff_manager.add_case_to_staff(self.selected_staff_id, case_data)
                
                # ケース一覧を更新
                self.refresh_case_list()
                
                # ダイアログを閉じる
                case_dialog.destroy()
                
                messagebox.showinfo("完了", "ケースを追加しました")
                
            except Exception as e:
                print(f"ケース追加エラー: {e}")
                messagebox.showerror("エラー", f"ケースの追加中にエラーが発生しました: {e}")
        
        def cancel_case():
            case_dialog.destroy()
        
        tk.Button(
            button_frame,
            text="保存",
            font=("游ゴシック", 10, "bold"),
            bg="#27ae60",
            fg="white",
            command=save_case,
            padx=20,
            pady=5
        ).pack(side="left", padx=5)
        
        tk.Button(
            button_frame,
            text="キャンセル",
            font=("游ゴシック", 10),
            bg="#95a5a6",
            fg="white",
            command=cancel_case,
            padx=20,
            pady=5
        ).pack(side="left", padx=5)
        
        # ボタンを中央揃えにする
        button_frame.pack_configure(anchor="center")
    
    def open_schedule_window(self):
        """スケジュールウィンドウを開く"""
        if not self.selected_staff_id:
            messagebox.showwarning("警告", "支援員を選択してください")
            return
        
        messagebox.showinfo("準備中", "スケジュール表示機能は準備中です")

    def save_staff_new(self):
        """新規支援員を保存"""
        try:
            # フォームの値を取得
            name = self.staff_name_var.get().strip()
            age = self.staff_age_var.get().strip()
            gender = self.staff_gender_var.get()
            district = self.staff_district_var.get()
            previous_job = self.staff_previous_job_var.get().strip()
            dropbox_number = self.staff_dropbox_var.get().strip()
            hobbies_skills = self.staff_hobbies_text.get(1.0, tk.END).strip()
            
            # 勤務曜日を取得
            work_days = ""
            for day in ['月', '火', '水', '木', '金']:
                if self.work_days_vars[day].get():
                    work_days += day
            
            # 勤務時間を取得
            start_time = self.staff_start_time_var.get().strip()
            end_time = self.staff_end_time_var.get().strip()
            work_hours = f"{start_time}-{end_time}" if start_time and end_time else ""
            
            # 必須項目のチェック
            if not name:
                messagebox.showwarning("警告", "名前を入力してください")
                return
            
            if not age:
                messagebox.showwarning("警告", "年齢を入力してください")
                return
            
            if not gender:
                messagebox.showwarning("警告", "性別を選択してください")
                return
            
            # データベースに保存
            staff_data = {
                'name': name,
                'age': int(age) if age.isdigit() else 0,
                'gender': gender,
                'region': district,
                'hobbies_skills': hobbies_skills,
                'previous_job': previous_job,
                'dropbox_number': dropbox_number,
                'work_days': work_days,
                'work_hours': work_hours,
                'is_active': True
            }
            
            # 支援員を追加
            self.staff_manager.add_staff(staff_data)
            
            # フォームをクリア
            self.clear_form()
            
            # 一覧を更新
            self.refresh_staff_tree()
            
            messagebox.showinfo("完了", "新しい支援員を追加しました")
            
        except Exception as e:
            print(f"新規追加エラー: {e}")
            messagebox.showerror("エラー", f"支援員の追加中にエラーが発生しました: {e}")
    
    def clear_form(self):
        """フォームをクリア"""
        self.staff_name_var.set("")
        self.staff_age_var.set("")
        self.staff_gender_var.set("")
        self.staff_district_var.set("")
        self.staff_previous_job_var.set("")
        self.staff_dropbox_var.set("")
        self.staff_hobbies_text.delete(1.0, tk.END)
        
        # 勤務曜日をクリア
        for day in ['月', '火', '水', '木', '金']:
            self.work_days_vars[day].set(False)
        
        # 勤務時間をクリア
        self.staff_start_time_var.set("")
        self.staff_end_time_var.set("")
        
        self.current_staff_id = None
        self.selected_staff_id = None

    def save_staff_update(self):
        """支援員情報を更新"""
        if not self.current_staff_id:
            messagebox.showwarning("警告", "支援員を選択してください")
            return
        
        try:
            # フォームの値を取得
            name = self.staff_name_var.get().strip()
            age = self.staff_age_var.get().strip()
            gender = self.staff_gender_var.get()
            district = self.staff_district_var.get()
            previous_job = self.staff_previous_job_var.get().strip()
            dropbox_number = self.staff_dropbox_var.get().strip()
            hobbies_skills = self.staff_hobbies_text.get(1.0, tk.END).strip()
            
            # 勤務曜日を取得
            work_days = ""
            for day in ['月', '火', '水', '木', '金']:
                if self.work_days_vars[day].get():
                    work_days += day
            
            # 勤務時間を取得
            start_time = self.staff_start_time_var.get().strip()
            end_time = self.staff_end_time_var.get().strip()
            work_hours = f"{start_time}-{end_time}" if start_time and end_time else ""
            
            # 必須項目のチェック
            if not name:
                messagebox.showwarning("警告", "名前を入力してください")
                return
            
            if not age:
                messagebox.showwarning("警告", "年齢を入力してください")
                return
            
            if not gender:
                messagebox.showwarning("警告", "性別を選択してください")
                return
            
            # データベースに更新
            staff_data = {
                'name': name,
                'age': int(age) if age.isdigit() else 0,
                'gender': gender,
                'region': district,
                'hobbies_skills': hobbies_skills,
                'previous_job': previous_job,
                'dropbox_number': dropbox_number,
                'work_days': work_days,
                'work_hours': work_hours,
                'is_active': True
            }
            
            # 支援員を更新
            self.staff_manager.update_staff(self.current_staff_id, staff_data)
            
            # 一覧を更新
            self.refresh_staff_tree()
            
            messagebox.showinfo("完了", "支援員情報を更新しました")
            
        except Exception as e:
            print(f"更新エラー: {e}")
            messagebox.showerror("エラー", f"支援員の更新中にエラーが発生しました: {e}")

    def delete_staff_confirm(self):
        """支援員削除の確認"""
        if not self.current_staff_id:
            messagebox.showwarning("警告", "削除する支援員を選択してください")
            return
        
        result = messagebox.askyesno("確認", "この支援員を削除しますか？")
        if result:
            try:
                self.staff_manager.delete_staff(self.current_staff_id)
                self.clear_form()
                self.refresh_staff_tree()
                messagebox.showinfo("完了", "支援員を削除しました")
            except Exception as e:
                print(f"削除エラー: {e}")
                messagebox.showerror("エラー", f"支援員の削除中にエラーが発生しました: {e}")
