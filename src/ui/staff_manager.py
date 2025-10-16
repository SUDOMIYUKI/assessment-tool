import tkinter as tk
from tkinter import ttk, messagebox
from src.database.staff import StaffManager

class StaffManagerDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.staff_manager = StaffManager()
        self.current_staff_id = None
        
        self.title("支援員管理")
        self.geometry("950x750")
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        self.refresh_staff_list()
        
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
        
        title = tk.Label(
            header_frame,
            text="👥 支援員管理",
            font=("游ゴシック", 14, "bold"),
            bg="#9b59b6",
            fg="white"
        )
        title.pack(pady=15)
        
        # メインエリア
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 左側：支援員一覧
        left_frame = ttk.LabelFrame(main_frame, text="支援員一覧", padding=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # ツリービュー
        columns = ('name', 'age', 'gender', 'region', 'is_active')
        self.tree = ttk.Treeview(left_frame, columns=columns, show='headings', height=15)
        
        self.tree.heading('name', text='名前')
        self.tree.heading('age', text='年齢')
        self.tree.heading('gender', text='性別')
        self.tree.heading('region', text='地域')
        self.tree.heading('is_active', text='状態')
        
        self.tree.column('name', width=100)
        self.tree.column('age', width=50)
        self.tree.column('gender', width=60)
        self.tree.column('region', width=120)
        self.tree.column('is_active', width=60)
        
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind('<<TreeviewSelect>>', self.on_staff_selected)
        
        # 右側：詳細・編集
        right_frame = ttk.LabelFrame(main_frame, text="支援員詳細", padding=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # フォーム
        form_frame = tk.Frame(right_frame)
        form_frame.pack(fill="both", expand=True)
        
        # 名前
        tk.Label(form_frame, text="名前:", font=("游ゴシック", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(form_frame, textvariable=self.name_var, width=30)
        self.name_entry.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # 年齢
        tk.Label(form_frame, text="年齢:", font=("游ゴシック", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.age_var = tk.StringVar()
        self.age_entry = ttk.Entry(form_frame, textvariable=self.age_var, width=30)
        self.age_entry.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # 性別
        tk.Label(form_frame, text="性別:", font=("游ゴシック", 10)).grid(row=2, column=0, sticky="w", pady=5)
        self.gender_var = tk.StringVar()
        self.gender_combo = ttk.Combobox(form_frame, textvariable=self.gender_var, values=["男性", "女性"], width=27, state="readonly")
        self.gender_combo.grid(row=2, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # 地域
        tk.Label(form_frame, text="地域:", font=("游ゴシック", 10)).grid(row=3, column=0, sticky="w", pady=5)
        self.region_var = tk.StringVar()
        self.region_entry = ttk.Entry(form_frame, textvariable=self.region_var, width=30)
        self.region_entry.grid(row=3, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # 趣味・特技
        tk.Label(form_frame, text="趣味・特技:", font=("游ゴシック", 10)).grid(row=4, column=0, sticky="nw", pady=5)
        self.hobbies_var = tk.StringVar()
        self.hobbies_text = tk.Text(form_frame, width=30, height=3, wrap=tk.WORD)
        self.hobbies_text.grid(row=4, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # 前職
        tk.Label(form_frame, text="前職:", font=("游ゴシック", 10)).grid(row=5, column=0, sticky="w", pady=5)
        self.previous_job_var = tk.StringVar()
        self.previous_job_entry = ttk.Entry(form_frame, textvariable=self.previous_job_var, width=30)
        self.previous_job_entry.grid(row=5, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Dropbox番号
        tk.Label(form_frame, text="Dropbox番号:", font=("游ゴシック", 10)).grid(row=6, column=0, sticky="w", pady=5)
        self.dropbox_var = tk.StringVar()
        self.dropbox_entry = ttk.Entry(form_frame, textvariable=self.dropbox_var, width=30)
        self.dropbox_entry.grid(row=6, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # 勤務曜日（チェックボックス形式）
        tk.Label(form_frame, text="勤務曜日:", font=("游ゴシック", 10)).grid(row=7, column=0, sticky="nw", pady=5)
        self.work_days_frame = tk.Frame(form_frame)
        self.work_days_frame.grid(row=7, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # 曜日のチェックボックス
        self.work_days_vars = {}
        days = ['月', '火', '水', '木', '金']
        for i, day in enumerate(days):
            self.work_days_vars[day] = tk.BooleanVar()
            ttk.Checkbutton(
                self.work_days_frame, 
                text=day, 
                variable=self.work_days_vars[day]
            ).grid(row=0, column=i, padx=5, sticky="w")
        
        # 勤務時間（開始時間・終了時間）
        tk.Label(form_frame, text="勤務時間:", font=("游ゴシック", 10)).grid(row=8, column=0, sticky="w", pady=5)
        self.work_hours_frame = tk.Frame(form_frame)
        self.work_hours_frame.grid(row=8, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # 開始時間
        tk.Label(self.work_hours_frame, text="開始:", font=("游ゴシック", 9)).pack(side="left", padx=(0, 5))
        self.start_time_var = tk.StringVar()
        self.start_time_entry = ttk.Entry(self.work_hours_frame, textvariable=self.start_time_var, width=8)
        self.start_time_entry.pack(side="left", padx=(0, 10))
        
        # 終了時間
        tk.Label(self.work_hours_frame, text="終了:", font=("游ゴシック", 9)).pack(side="left", padx=(0, 5))
        self.end_time_var = tk.StringVar()
        self.end_time_entry = ttk.Entry(self.work_hours_frame, textvariable=self.end_time_var, width=8)
        self.end_time_entry.pack(side="left")
        
        # 状態
        self.is_active_var = tk.BooleanVar(value=True)
        self.active_check = ttk.Checkbutton(form_frame, text="アクティブ", variable=self.is_active_var)
        self.active_check.grid(row=9, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # ボタンエリア
        button_frame = tk.Frame(right_frame)
        button_frame.pack(fill="x", pady=10)
        
        new_btn = tk.Button(
            button_frame,
            text="📝 新規追加",
            font=("游ゴシック", 10),
            bg="#3498db",
            fg="white",
            command=self.new_staff,
            padx=15,
            pady=5
        )
        new_btn.pack(side="left", padx=(0, 5))
        
        save_btn = tk.Button(
            button_frame,
            text="💾 保存",
            font=("游ゴシック", 10),
            bg="#27ae60",
            fg="white",
            command=self.save_staff,
            padx=15,
            pady=5
        )
        save_btn.pack(side="left", padx=(0, 5))
        
        delete_btn = tk.Button(
            button_frame,
            text="🗑️ 削除",
            font=("游ゴシック", 10),
            bg="#e74c3c",
            fg="white",
            command=self.delete_staff,
            padx=15,
            pady=5
        )
        delete_btn.pack(side="left")
        
        # 下部ボタンエリア
        bottom_frame = tk.Frame(self)
        bottom_frame.pack(fill="x", padx=20, pady=10)
        
        close_btn = tk.Button(
            bottom_frame,
            text="❌ 閉じる",
            font=("游ゴシック", 11),
            bg="#95a5a6",
            fg="white",
            command=self.destroy,
            padx=20,
            pady=8
        )
        close_btn.pack(side="right")
    
    def refresh_staff_list(self):
        """支援員リストを更新"""
        # 既存のアイテムをクリア
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 支援員一覧を取得
        staff_list = self.staff_manager.get_all_staff(active_only=False)
        
        for staff in staff_list:
            status = "アクティブ" if staff['is_active'] else "非アクティブ"
            self.tree.insert('', 'end', values=(
                staff['name'],
                staff['age'],
                staff['gender'],
                staff['region'],
                status
            ), tags=(staff['id'],))
    
    def on_staff_selected(self, event):
        """支援員が選択された時"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            staff_id = int(item['tags'][0])
            
            # 支援員情報を取得して表示
            staff = self.staff_manager.get_staff_by_id(staff_id)
            if staff:
                self.current_staff_id = staff_id
                self.name_var.set(staff['name'])
                self.age_var.set(str(staff['age']))
                self.gender_var.set(staff['gender'])
                self.region_var.set(staff['region'])
                self.hobbies_text.delete('1.0', tk.END)
                self.hobbies_text.insert('1.0', staff['hobbies_skills'] or '')
                self.previous_job_var.set(staff['previous_job'] or '')
                self.dropbox_var.set(staff['dropbox_number'] or '')
                # 勤務曜日の設定
                work_days = staff['work_days'] or ''
                for day in ['月', '火', '水', '木', '金']:
                    self.work_days_vars[day].set(day in work_days)
                
                # 勤務時間の設定
                work_hours = staff['work_hours'] or ''
                if '-' in work_hours:
                    start_time, end_time = work_hours.split('-')
                    self.start_time_var.set(start_time.strip())
                    self.end_time_var.set(end_time.strip())
                else:
                    self.start_time_var.set('')
                    self.end_time_var.set('')
                self.is_active_var.set(bool(staff['is_active']))
    
    def new_staff(self):
        """新規支援員作成"""
        self.current_staff_id = None
        self.clear_form()
    
    def clear_form(self):
        """フォームをクリア"""
        self.name_var.set('')
        self.age_var.set('')
        self.gender_var.set('')
        self.region_var.set('')
        self.hobbies_text.delete('1.0', tk.END)
        self.previous_job_var.set('')
        self.dropbox_var.set('')
        
        # 勤務曜日をクリア
        for day_var in self.work_days_vars.values():
            day_var.set(False)
        
        # 勤務時間をクリア
        self.start_time_var.set('')
        self.end_time_var.set('')
        
        self.is_active_var.set(True)
    
    def save_staff(self):
        """支援員を保存"""
        # 入力チェック
        if not self.name_var.get().strip():
            messagebox.showerror("エラー", "名前を入力してください")
            return
        
        if not self.age_var.get().strip():
            messagebox.showerror("エラー", "年齢を入力してください")
            return
        
        try:
            age = int(self.age_var.get())
        except ValueError:
            messagebox.showerror("エラー", "年齢は数値で入力してください")
            return
        
        if not self.gender_var.get():
            messagebox.showerror("エラー", "性別を選択してください")
            return
        
        if not self.region_var.get().strip():
            messagebox.showerror("エラー", "地域を入力してください")
            return
        
        # データを準備
        staff_data = {
            'name': self.name_var.get().strip(),
            'age': age,
            'gender': self.gender_var.get(),
            'region': self.region_var.get().strip(),
            'hobbies_skills': self.hobbies_text.get('1.0', tk.END).strip(),
            'previous_job': self.previous_job_var.get().strip(),
            'dropbox_number': self.dropbox_var.get().strip(),
            'work_days': self._get_selected_work_days(),
            'work_hours': self._get_work_hours_string(),
            'is_active': self.is_active_var.get()
        }
        
        try:
            if self.current_staff_id:
                # 更新
                self.staff_manager.update_staff(self.current_staff_id, **staff_data)
                messagebox.showinfo("完了", "支援員情報を更新しました")
            else:
                # 新規作成
                self.staff_manager.add_staff(**staff_data)
                messagebox.showinfo("完了", "新しい支援員を追加しました")
            
            self.refresh_staff_list()
            self.clear_form()
            
        except Exception as e:
            messagebox.showerror("エラー", f"保存中にエラーが発生しました：\n{str(e)}")
    
    def delete_staff(self):
        """支援員を削除"""
        if not self.current_staff_id:
            messagebox.showwarning("警告", "削除する支援員を選択してください")
            return
        
        staff = self.staff_manager.get_staff_by_id(self.current_staff_id)
        if not staff:
            messagebox.showerror("エラー", "支援員が見つかりません")
            return
        
        result = messagebox.askyesno(
            "確認",
            f"支援員「{staff['name']}」を削除しますか？\n（論理削除され、非アクティブになります）"
        )
        
        if result:
            try:
                self.staff_manager.delete_staff(self.current_staff_id)
                messagebox.showinfo("完了", "支援員を削除しました")
                self.refresh_staff_list()
                self.clear_form()
                self.current_staff_id = None
            except Exception as e:
                messagebox.showerror("エラー", f"削除中にエラーが発生しました：\n{str(e)}")
    
    def _get_selected_work_days(self):
        """選択された勤務曜日を文字列として取得"""
        selected_days = []
        for day, var in self.work_days_vars.items():
            if var.get():
                selected_days.append(day)
        return ''.join(selected_days)
    
    def _get_work_hours_string(self):
        """勤務時間を文字列として取得"""
        start_time = self.start_time_var.get().strip()
        end_time = self.end_time_var.get().strip()
        
        if start_time and end_time:
            return f"{start_time}-{end_time}"
        elif start_time:
            return start_time
        elif end_time:
            return end_time
        else:
            return ""
