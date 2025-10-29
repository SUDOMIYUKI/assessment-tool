import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from src.database.staff import StaffManager

class StaffManagerDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.staff_manager = StaffManager()
        self.current_staff_id = None
        self.selected_staff_id = None
        self.selected_unassigned_case_id = None
        self.selected_unassigned_case_data = None
        
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
        
        title = tk.Label(
            header_frame,
            text="👥 支援員管理システム",
            font=("游ゴシック", 14, "bold"),
            bg="#9b59b6",
            fg="white"
        )
        title.pack(pady=15)
        
        # メインコンテンツ（タブ付き）
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # タブを追加
        self.staff_management_frame = tk.Frame(self.notebook)
        self.case_list_frame = tk.Frame(self.notebook)
        
        self.notebook.add(self.staff_management_frame, text="支援員管理")
        self.notebook.add(self.case_list_frame, text="ケース一覧")
        
        # 支援員管理画面
        self.create_staff_management_view(self.staff_management_frame)
        
        # ケース一覧画面
        self.create_case_list_view(self.case_list_frame)
    
    def create_case_list_view(self, parent):
        """未割り当てケース一覧ビュー"""
        main_frame = tk.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # タイトル
        title_label = tk.Label(main_frame, text="未処理のケース一覧", font=("游ゴシック", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # 左側：未割り当てケース一覧
        left_frame = ttk.LabelFrame(main_frame, text="未処理のケース", padding=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # 未割り当てケースのツリービュー
        columns = ('case_number', 'district', 'child_name', 'preferred_day', 'preferred_time', 'notes')
        self.unassigned_tree = ttk.Treeview(left_frame, columns=columns, show='headings', height=15)
        
        self.unassigned_tree.heading('case_number', text='ケース番号')
        self.unassigned_tree.heading('district', text='区')
        self.unassigned_tree.heading('child_name', text='児童氏名')
        self.unassigned_tree.heading('preferred_day', text='希望曜日')
        self.unassigned_tree.heading('preferred_time', text='希望時間')
        self.unassigned_tree.heading('notes', text='備考')
        
        self.unassigned_tree.column('case_number', width=100)
        self.unassigned_tree.column('district', width=80)
        self.unassigned_tree.column('child_name', width=100)
        self.unassigned_tree.column('preferred_day', width=80)
        self.unassigned_tree.column('preferred_time', width=100)
        self.unassigned_tree.column('notes', width=150)
        
        scrollbar1 = ttk.Scrollbar(left_frame, orient="vertical", command=self.unassigned_tree.yview)
        self.unassigned_tree.configure(yscrollcommand=scrollbar1.set)
        
        self.unassigned_tree.pack(side="left", fill="both", expand=True)
        scrollbar1.pack(side="right", fill="y")
        
        self.unassigned_tree.bind('<<TreeviewSelect>>', self.on_unassigned_tree_selected)
        
        # ケース詳細表示・編集エリア
        detail_frame = ttk.LabelFrame(left_frame, text="ケース詳細", padding=10)
        detail_frame.pack(fill="x", pady=(5, 0))
        
        # 詳細情報のラベル
        self.unassigned_detail_text = tk.Text(detail_frame, height=6, width=80, wrap=tk.WORD, state="disabled")
        self.unassigned_detail_text.pack(fill="x", pady=(0, 5))
        
        # 編集・削除ボタン
        detail_button_frame = tk.Frame(detail_frame)
        detail_button_frame.pack(fill="x")
        
        edit_btn = tk.Button(
            detail_button_frame,
            text="編集",
            font=("游ゴシック", 9),
            bg="#3498db",
            fg="white",
            command=self.edit_unassigned_case,
            padx=15,
            pady=3
        )
        edit_btn.pack(side="left", padx=(0, 5))
        
        delete_btn = tk.Button(
            detail_button_frame,
            text="削除",
            font=("游ゴシック", 9),
            bg="#e74c3c",
            fg="white",
            command=self.delete_unassigned_case,
            padx=15,
            pady=3
        )
        delete_btn.pack(side="left")
        
        # 右側：支援員一覧と割り当てボタン
        right_frame = ttk.LabelFrame(main_frame, text="支援員一覧", padding=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # 支援員のツリービュー
        staff_columns = ('name', 'current_cases')
        self.assign_staff_tree = ttk.Treeview(right_frame, columns=staff_columns, show='headings', height=10)
        
        self.assign_staff_tree.heading('name', text='名前')
        self.assign_staff_tree.heading('current_cases', text='現在のケース数')
        
        self.assign_staff_tree.column('name', width=150)
        self.assign_staff_tree.column('current_cases', width=120)
        
        scrollbar2 = ttk.Scrollbar(right_frame, orient="vertical", command=self.assign_staff_tree.yview)
        self.assign_staff_tree.configure(yscrollcommand=scrollbar2.set)
        
        self.assign_staff_tree.pack(side="left", fill="both", expand=True)
        scrollbar2.pack(side="right", fill="y")
        
        # 割り当てボタン
        button_frame = tk.Frame(right_frame)
        button_frame.pack(fill="x", pady=10)
        
        assign_btn = tk.Button(
            button_frame,
            text="ケースを割り当て",
            font=("游ゴシック", 10, "bold"),
            bg="#3498db",
            fg="white",
            command=self.assign_case_to_staff,
            padx=20,
            pady=5
        )
        assign_btn.pack(pady=5)
        
        # 初期データ読み込み
        self.refresh_unassigned_tree()
        self.refresh_assign_staff_tree()
    
    def on_unassigned_tree_selected(self, event):
        """未割り当てケースが選択された時"""
        selection = self.unassigned_tree.selection()
        if selection:
            item = self.unassigned_tree.item(selection[0])
            values = item.get('values', [])
            if values:
                # ケースIDを取得（最初のカラムがcase_numberと想定）
                case_number = values[0]
                # データベースからケース詳細を取得
                conn = sqlite3.connect(str(self.staff_manager.db_path), timeout=10.0)
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM unassigned_cases WHERE case_number = ? AND status = ?', (case_number, '未割り当て'))
                columns = [desc[0] for desc in cursor.description]
                row = cursor.fetchone()
                if row:
                    case_data = dict(zip(columns, row))
                    self.selected_unassigned_case_id = case_data['id']
                    self.selected_unassigned_case_data = case_data
                    # 詳細情報を表示
                    self.display_unassigned_case_details(case_data)
                conn.close()
    
    def display_unassigned_case_details(self, case_data):
        """未割り当てケースの詳細を表示"""
        self.unassigned_detail_text.config(state="normal")
        self.unassigned_detail_text.delete(1.0, tk.END)
        
        detail_text = f"""ケース番号: {case_data.get('case_number', 'なし')}
区: {case_data.get('district', 'なし')}
児童氏名: {case_data.get('child_name', 'なし')}
児童年齢: {case_data.get('child_age', 'なし')}
性別: {case_data.get('child_gender', 'なし')}
希望曜日: {case_data.get('preferred_day', 'なし')}
希望時間: {case_data.get('preferred_time', 'なし')}
頻度: {case_data.get('frequency', 'なし')}
場所: {case_data.get('location', 'なし')}
備考: {case_data.get('notes', 'なし')}"""
        
        self.unassigned_detail_text.insert(1.0, detail_text)
        self.unassigned_detail_text.config(state="disabled")
    
    def refresh_unassigned_tree(self):
        """未割り当てケース一覧を更新"""
        try:
            # 既存のアイテムをクリア
            for item in self.unassigned_tree.get_children():
                self.unassigned_tree.delete(item)
            
            # 未割り当てケースを取得
            unassigned_cases = self.staff_manager.get_unassigned_cases()
            
            for case in unassigned_cases:
                # status が '未割り当て' のケースのみを表示
                if case.get('status') == '未割り当て':
                    self.unassigned_tree.insert('', 'end', values=(
                        case.get('case_number', ''),
                        case.get('district', ''),
                        case.get('child_name', ''),
                        case.get('preferred_day', ''),
                        case.get('preferred_time', ''),
                        case.get('notes', '')
                    ))
        except Exception as e:
            print(f"refresh_unassigned_tree エラー: {e}")
    
    def refresh_assign_staff_tree(self):
        """割り当て用支援員一覧を更新"""
        try:
            # 既存のアイテムをクリア
            for item in self.assign_staff_tree.get_children():
                self.assign_staff_tree.delete(item)
            
            # 支援員一覧を取得
            staff_list = self.staff_manager.get_all_staff()
            
            for staff in staff_list:
                # 現在のケース数を計算
                case_count = 0
                if staff.get('case_number') and staff.get('case_number').strip() != '':
                    case_count = 1
                
                self.assign_staff_tree.insert('', 'end', values=(
                    staff['name'],
                    case_count
                ), tags=(staff['id'],))
        except Exception as e:
            print(f"refresh_assign_staff_tree エラー: {e}")
    
    def assign_case_to_staff(self):
        """選択されたケースを選択された支援員に割り当て"""
        # ケース選択確認
        if not self.selected_unassigned_case_id:
            messagebox.showwarning("警告", "割り当てるケースを選択してください")
            return
        
        # 支援員選択確認
        selection = self.assign_staff_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "割り当て先の支援員を選択してください")
            return
        
        item = self.assign_staff_tree.item(selection[0])
        tags = item.get('tags', [])
        if not tags:
            messagebox.showwarning("警告", "支援員情報が見つかりません")
            return
        
        staff_id = tags[0]
        
        try:
            # ケースを割り当て
            self.staff_manager.assign_unassigned_case_to_staff(self.selected_unassigned_case_id, staff_id)
            
            # 一覧を更新
            self.refresh_unassigned_tree()
            self.refresh_assign_staff_tree()
            
            messagebox.showinfo("完了", "ケースを割り当てました")
            
        except Exception as e:
            print(f"割り当てエラー: {e}")
            messagebox.showerror("エラー", f"ケースの割り当て中にエラーが発生しました: {e}")
    
    def edit_unassigned_case(self):
        """未割り当てケースを編集"""
        if not self.selected_unassigned_case_data:
            messagebox.showwarning("警告", "編集するケースを選択してください")
            return
        
        # 編集ダイアログを開く
        edit_dialog = tk.Toplevel(self)
        edit_dialog.title("ケース編集")
        edit_dialog.geometry("500x600")
        edit_dialog.transient(self)
        edit_dialog.grab_set()
        
        # 中央に配置
        edit_dialog.update_idletasks()
        x = (edit_dialog.winfo_screenwidth() // 2) - (edit_dialog.winfo_width() // 2)
        y = (edit_dialog.winfo_screenheight() // 2) - (edit_dialog.winfo_height() // 2)
        edit_dialog.geometry(f'+{x}+{y}')
        
        # メインフレーム
        main_frame = tk.Frame(edit_dialog)
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
        district_var = tk.StringVar(value=str(self.selected_unassigned_case_data.get('district', '')))
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
        case_number_var = tk.StringVar(value=str(self.selected_unassigned_case_data.get('case_number', '')))
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
        child_name_var = tk.StringVar(value=str(self.selected_unassigned_case_data.get('child_name', '')))
        tk.Entry(child_frame, textvariable=child_name_var, width=30, font=("游ゴシック", 10)).pack(side="left", padx=(10, 0))
        
        # 曜日
        day_frame = tk.Frame(form_frame)
        day_frame.pack(fill="x", pady=5)
        tk.Label(day_frame, text="曜日:", font=("游ゴシック", 10), width=15, anchor="w").pack(side="left")
        
        # 曜日チェックボックスのフレーム
        day_checkbox_frame = tk.Frame(day_frame)
        day_checkbox_frame.pack(side="left", padx=(10, 0))
        
        # チェックボックス用の変数
        day_vars = {}
        days = ["月", "火", "水", "木", "金"]
        for day in days:
            day_vars[day] = tk.BooleanVar()
            # 現在の値を確認してセット（複数選択対応）
            current_value = str(self.selected_unassigned_case_data.get('preferred_day', ''))
            if day in current_value:
                day_vars[day].set(True)
        
        # チェックボックスを作成
        for day in days:
            ttk.Checkbutton(day_checkbox_frame, text=day, variable=day_vars[day]).pack(side="left", padx=5)
        
        # 時間
        time_frame = tk.Frame(form_frame)
        time_frame.pack(fill="x", pady=5)
        tk.Label(time_frame, text="時間:", font=("游ゴシック", 10), width=15, anchor="w").pack(side="left")
        schedule_time_var = tk.StringVar(value=str(self.selected_unassigned_case_data.get('preferred_time', '')))
        tk.Entry(time_frame, textvariable=schedule_time_var, width=30, font=("游ゴシック", 10)).pack(side="left", padx=(10, 0))
        
        # 場所
        location_frame = tk.Frame(form_frame)
        location_frame.pack(fill="x", pady=5)
        tk.Label(location_frame, text="場所:", font=("游ゴシック", 10), width=15, anchor="w").pack(side="left")
        location_var = tk.StringVar(value=str(self.selected_unassigned_case_data.get('location', '')))
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
        frequency_var = tk.StringVar(value=str(self.selected_unassigned_case_data.get('frequency', '')))
        frequency_combo = ttk.Combobox(freq_frame, textvariable=frequency_var, values=["週1回", "週2回", "月1回", "月2回", "その他"], width=27, state="readonly")
        frequency_combo.pack(side="left", padx=(10, 0))
        
        # 備考
        notes_frame = tk.Frame(form_frame)
        notes_frame.pack(fill="x", pady=5)
        tk.Label(notes_frame, text="備考:", font=("游ゴシック", 10), width=15, anchor="nw").pack(side="left", anchor="nw")
        notes_text = tk.Text(notes_frame, width=30, height=4, wrap=tk.WORD, font=("游ゴシック", 10))
        notes_text.insert(1.0, str(self.selected_unassigned_case_data.get('notes', '')))
        notes_text.pack(side="left", padx=(10, 0))
        
        # スクロールバーとキャンバスを配置
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # ボタン（下に配置）
        button_frame = tk.Frame(main_frame)
        button_frame.pack(side="bottom", pady=20, fill="x")
        
        def save_changes():
            try:
                # チェックされた曜日を文字列として取得
                selected_days = ''.join([day for day in days if day_vars[day].get()])
                
                conn = sqlite3.connect(str(self.staff_manager.db_path), timeout=10.0)
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE unassigned_cases 
                    SET district = ?,
                        child_name = ?,
                        preferred_day = ?,
                        preferred_time = ?,
                        frequency = ?,
                        location = ?,
                        notes = ?
                    WHERE id = ?
                ''', (
                    district_var.get(),
                    child_name_var.get(),
                    selected_days,
                    schedule_time_var.get(),
                    frequency_var.get(),
                    location_var.get(),
                    notes_text.get(1.0, tk.END).strip(),
                    self.selected_unassigned_case_id
                ))
                
                conn.commit()
                conn.close()
                
                # 一覧を更新
                self.refresh_unassigned_tree()
                
                # 詳細表示を更新
                if hasattr(self, 'display_unassigned_case_details'):
                    # データを再取得
                    conn = sqlite3.connect(str(self.staff_manager.db_path), timeout=10.0)
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM unassigned_cases WHERE id = ?', (self.selected_unassigned_case_id,))
                    columns = [desc[0] for desc in cursor.description]
                    row = cursor.fetchone()
                    if row:
                        case_data = dict(zip(columns, row))
                        self.selected_unassigned_case_data = case_data
                        self.display_unassigned_case_details(case_data)
                    conn.close()
                
                edit_dialog.destroy()
                messagebox.showinfo("完了", "ケース情報を更新しました")
                
            except Exception as e:
                print(f"編集エラー: {e}")
                messagebox.showerror("エラー", f"ケースの編集中にエラーが発生しました: {e}")
        
        def cancel_changes():
            edit_dialog.destroy()
        
        tk.Button(
            button_frame,
            text="保存",
            font=("游ゴシック", 10, "bold"),
            bg="#27ae60",
            fg="white",
            command=save_changes,
            padx=20,
            pady=5
        ).pack(side="left", padx=5)
        
        tk.Button(
            button_frame,
            text="キャンセル",
            font=("游ゴシック", 10),
            bg="#95a5a6",
            fg="white",
            command=cancel_changes,
            padx=20,
            pady=5
        ).pack(side="left", padx=5)
    
    def delete_unassigned_case(self):
        """未割り当てケースを削除"""
        if not self.selected_unassigned_case_id:
            messagebox.showwarning("警告", "削除するケースを選択してください")
            return
        
        result = messagebox.askyesno("確認", "このケースを削除しますか？")
        if result:
            try:
                conn = sqlite3.connect(str(self.staff_manager.db_path), timeout=10.0)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM unassigned_cases WHERE id = ?', (self.selected_unassigned_case_id,))
                conn.commit()
                conn.close()
                
                # 一覧を更新
                self.refresh_unassigned_tree()
                
                # 詳細表示をクリア
                self.unassigned_detail_text.config(state="normal")
                self.unassigned_detail_text.delete(1.0, tk.END)
                self.unassigned_detail_text.config(state="disabled")
                
                self.selected_unassigned_case_id = None
                self.selected_unassigned_case_data = None
                
                messagebox.showinfo("完了", "ケースを削除しました")
                
            except Exception as e:
                print(f"削除エラー: {e}")
                messagebox.showerror("エラー", f"ケースの削除中にエラーが発生しました: {e}")

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
        
        # 左列の項目
        row = 0
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
        
        # 右列の項目
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
            text="📝 新規追加",
            font=("游ゴシック", 9, "bold"),
            bg="#3498db",
            fg="white",
            command=self.save_staff_new,
            padx=10,
            pady=5
        ).pack(side="left", padx=2)
        
        tk.Button(
            button_frame,
            text="💾 保存",
            font=("游ゴシック", 9, "bold"),
            bg="#27ae60",
            fg="white",
            command=self.save_staff_update,
            padx=10,
            pady=5
        ).pack(side="left", padx=2)
        
        tk.Button(
            button_frame,
            text="🗑️ 削除",
            font=("游ゴシック", 9),
            bg="#e74c3c",
            fg="white",
            command=self.delete_staff_confirm,
            padx=10,
            pady=5
        ).pack(side="left", padx=2)
        
        tk.Button(
            button_frame,
            text="📅 スケジュール表示",
            font=("游ゴシック", 9, "bold"),
            bg="#9b59b6",
            fg="white",
            command=self.open_schedule_window,
            padx=10,
            pady=5
        ).pack(side="left", padx=2)
        
        # ケース一覧（支援員詳細の下に表示）
        case_frame = ttk.LabelFrame(right_frame, text="ケース一覧", padding=5)
        case_frame.pack(fill="x", pady=(10, 0))
        
        # ケース追加ボタン
        case_button_frame = tk.Frame(case_frame)
        case_button_frame.pack(fill="x", pady=(0, 5))
        
        # ケース追加ボタン
        tk.Button(
            case_button_frame,
            text="➕ ケース追加",
            command=self.open_add_case_dialog,
            font=("游ゴシック", 9),
            bg="#27ae60",
            fg="white",
            padx=10,
            pady=3
        ).pack(side="left", padx=(0, 5))
        
        # ケース削除ボタン
        tk.Button(
            case_button_frame,
            text="− ケース削除",
            command=self.delete_case_item,
            font=("游ゴシック", 9),
            bg="#e74c3c",
            fg="white",
            padx=10,
            pady=3
        ).pack(side="left")
        
        # ケース一覧テーブル
        case_columns = ('case_number', 'district', 'schedule', 'frequency', 'location')
        self.case_tree = ttk.Treeview(case_frame, columns=case_columns, show='headings', height=6)
        
        # 列の設定
        self.case_tree.heading('case_number', text='ケース番号')
        self.case_tree.heading('district', text='区')
        self.case_tree.heading('schedule', text='日程・時間')
        self.case_tree.heading('frequency', text='頻度')
        self.case_tree.heading('location', text='場所')
        
        # 列幅の設定
        self.case_tree.column('case_number', width=100)
        self.case_tree.column('district', width=80)
        self.case_tree.column('schedule', width=120)
        self.case_tree.column('frequency', width=60)
        self.case_tree.column('location', width=80)
        
        # スクロールバー
        case_scrollbar = ttk.Scrollbar(case_frame, orient="vertical", command=self.case_tree.yview)
        self.case_tree.configure(yscrollcommand=case_scrollbar.set)
        
        self.case_tree.pack(side="left", fill="both", expand=True)
        case_scrollbar.pack(side="right", fill="y")
        
        # 右クリックメニュー
        self.case_context_menu = tk.Menu(self, tearoff=0)
        self.case_context_menu.add_command(label="編集", command=self.edit_case)
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
                # 支援員情報を直接取得（staffテーブルからケース情報を取得）
                conn = sqlite3.connect(str(self.staff_manager.db_path), timeout=10.0)
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM staff WHERE id = ?', (self.selected_staff_id,))
                staff_columns = [desc[0] for desc in cursor.description]
                staff_data = dict(zip(staff_columns, cursor.fetchone()))
                conn.close()
                
                # ケース情報があれば表示
                case_number = staff_data.get('case_number', '')
                case_district = staff_data.get('case_district', '')
                case_day = staff_data.get('case_day', '')
                case_time = staff_data.get('case_time', '')
                case_frequency = staff_data.get('case_frequency', '')
                case_location = staff_data.get('case_location', '')
                
                # ケース番号が存在する場合のみ表示
                if case_number and case_number.strip() != '' and case_number != 'None':
                    self.case_tree.insert('', 'end', values=(
                        case_number,
                        case_district or '',
                        f"{case_day or ''} {case_time or ''}",
                        case_frequency or '',
                        case_location or ''
                    ))
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

    def edit_case(self):
        """ケースを編集"""
        selection = self.case_tree.selection()
        if selection:
            case_id = self.case_tree.item(selection[0])['tags'][0]
            messagebox.showinfo("編集", f"ケースID {case_id} を編集")

    def delete_case_item(self):
        """ケース項目を削除（未割り当てケースに戻す）"""
        # 支援員選択確認
        if not self.selected_staff_id:
            messagebox.showwarning("警告", "支援員が選択されていません")
            return
        
        # ケース選択確認（ケースツリーから選択）
        selection = self.case_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "削除するケースを選択してください")
            return
        
        result = messagebox.askyesno("確認", "このケースを未割り当てに戻しますか？")
        if result:
            try:
                conn = sqlite3.connect(str(self.staff_manager.db_path), timeout=10.0)
                cursor = conn.cursor()
                
                # 支援員情報を取得
                cursor.execute('SELECT * FROM staff WHERE id = ?', (self.selected_staff_id,))
                staff_columns = [desc[0] for desc in cursor.description]
                staff_data = dict(zip(staff_columns, cursor.fetchone()))
                
                # ケース情報を取得
                case_number = staff_data.get('case_number', '') or None
                district = staff_data.get('case_district', '') or None
                case_day = staff_data.get('case_day', '') or None
                case_time = staff_data.get('case_time', '') or None
                frequency = staff_data.get('case_frequency', '') or None
                location = staff_data.get('case_location', '') or None
                
                # ケース情報が空の場合はスキップ
                if not case_number or case_number == 'None' or case_number.strip() == '':
                    messagebox.showwarning("警告", "削除するケース情報が見つかりません")
                    return
                
                # 未割り当てケースとして登録（既に存在する場合は更新）
                cursor.execute('''
                    INSERT OR REPLACE INTO unassigned_cases 
                    (case_number, district, preferred_day, preferred_time, frequency, location, status)
                    VALUES (?, ?, ?, ?, ?, ?, '未割り当て')
                ''', (
                    case_number,
                    district,
                    case_day,
                    case_time,
                    frequency,
                    location
                ))
                
                # 既存のケースを未割り当てに戻す
                cursor.execute('''
                    UPDATE unassigned_cases 
                    SET status = '未割り当て'
                    WHERE case_number = ?
                ''', (case_number,))
                
                # 支援員のケース情報をクリア
                cursor.execute('''
                    UPDATE staff 
                    SET case_district = '',
                        case_number = '',
                        case_day = '',
                        case_time = '',
                        case_frequency = '',
                        case_location = ''
                    WHERE id = ?
                ''', (self.selected_staff_id,))
                
                conn.commit()
                conn.close()
                
                # 支援員を選択し直す（フォームを再読み込み）
                self.on_staff_tree_selected(None)
                
                # ケース一覧タブを更新
                if hasattr(self, 'refresh_unassigned_tree'):
                    self.refresh_unassigned_tree()
                
                messagebox.showinfo("完了", "ケースを未割り当てに戻しました")
                
            except Exception as e:
                print(f"ケース削除エラー: {e}")
                messagebox.showerror("エラー", f"ケースの削除中にエラーが発生しました: {e}")

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
        
        # 曜日
        day_frame = tk.Frame(form_frame)
        day_frame.pack(fill="x", pady=5)
        tk.Label(day_frame, text="曜日:", font=("游ゴシック", 10), width=15, anchor="w").pack(side="left")
        
        # 曜日チェックボックスのフレーム
        day_checkbox_frame = tk.Frame(day_frame)
        day_checkbox_frame.pack(side="left", padx=(10, 0))
        
        # チェックボックス用の変数
        day_vars = {}
        days = ["月", "火", "水", "木", "金"]
        for day in days:
            day_vars[day] = tk.BooleanVar()
        
        # チェックボックスを作成
        for day in days:
            ttk.Checkbutton(day_checkbox_frame, text=day, variable=day_vars[day]).pack(side="left", padx=5)
        
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
        
        # スクロールバーとキャンバスを配置
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # ボタン（下に配置）
        button_frame = tk.Frame(main_frame)
        button_frame.pack(side="bottom", pady=20, fill="x")
        
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
                
                # チェックされた曜日を文字列として取得
                selected_days = ''.join([day for day in days if day_vars[day].get()])
                
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
                    'schedule_day': selected_days,
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
        
        # スケジュールウィンドウを開く
        schedule_window = tk.Toplevel(self)
        schedule_window.title("週間スケジュール")
        schedule_window.geometry("800x600")
        schedule_window.transient(self)
        schedule_window.grab_set()
        
        # 中央に配置
        schedule_window.update_idletasks()
        x = (schedule_window.winfo_screenwidth() // 2) - (schedule_window.winfo_width() // 2)
        y = (schedule_window.winfo_screenheight() // 2) - (schedule_window.winfo_height() // 2)
        schedule_window.geometry(f'+{x}+{y}')
        
        # スケジュール表示
        self.create_schedule_view(schedule_window)

    def create_schedule_view(self, parent):
        """週間スケジュール表ビュー"""
        
        # エリア選択と選択された支援員表示
        control_frame = tk.Frame(parent)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(control_frame, text="エリア:", font=("游ゴシック", 10)).pack(side="left", padx=5)
        self.area_var = tk.StringVar(value="全て")
        area_combo = ttk.Combobox(
            control_frame, 
            textvariable=self.area_var,
            values=["全て", "東エリア", "南エリア"],
            state="readonly",
            width=15
        )
        area_combo.pack(side="left", padx=5)
        area_combo.bind('<<ComboboxSelected>>', self.refresh_schedule)
        
        # 選択された支援員表示
        self.selected_staff_label = tk.Label(
            control_frame, 
            text="支援員を選択してください", 
            font=("游ゴシック", 10, "bold"),
            fg="#9b59b6"
        )
        self.selected_staff_label.pack(side="left", padx=20)
        
        # 更新ボタン
        refresh_btn = tk.Button(
            control_frame,
            text="🔄 更新",
            command=self.refresh_schedule,
            font=("游ゴシック", 10),
            bg="#3498db",
            fg="white",
            padx=10,
            pady=5
        )
        refresh_btn.pack(side="left", padx=5)
        
        # スケジュール表本体
        canvas_frame = tk.Frame(parent)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # キャンバス
        self.schedule_canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=1, width=600, height=400)
        self.schedule_canvas.pack(fill="both", expand=True)
        
        # スケジュール表を描画
        self.draw_schedule_grid()

    def draw_schedule_grid(self):
        """スケジュールグリッドを描画"""
        canvas = self.schedule_canvas
        canvas.delete("all")
        
        # 定数
        CELL_WIDTH = 100
        CELL_HEIGHT = 40
        TIME_SLOTS = [f"{h:02d}:00" for h in range(9, 19)]
        DAYS = ["月", "火", "水", "木", "金"]
        
        # ヘッダー（曜日）
        for i, day in enumerate(DAYS):
            x = 80 + i * CELL_WIDTH
            canvas.create_rectangle(x, 0, x + CELL_WIDTH, 40, fill="#9b59b6", outline="black")
            canvas.create_text(x + CELL_WIDTH // 2, 20, text=day, font=("游ゴシック", 12, "bold"), fill="white")
        
        # 時間軸
        for i, time in enumerate(TIME_SLOTS):
            y = 40 + i * CELL_HEIGHT
            canvas.create_rectangle(0, y, 80, y + CELL_HEIGHT, fill="#ecf0f1", outline="black")
            canvas.create_text(40, y + CELL_HEIGHT // 2, text=time, font=("游ゴシック", 9))
        
        # グリッド
        for i in range(len(DAYS)):
            for j in range(len(TIME_SLOTS)):
                x = 80 + i * CELL_WIDTH
                y = 40 + j * CELL_HEIGHT
                canvas.create_rectangle(x, y, x + CELL_WIDTH, y + CELL_HEIGHT, fill="white", outline="#ddd")
        
        # スケジュールデータを取得して描画
        try:
            schedules = self.staff_manager.get_weekly_schedule()
            self.draw_schedule_items(schedules, CELL_WIDTH, CELL_HEIGHT, DAYS, TIME_SLOTS)
        except Exception as e:
            print(f"スケジュール取得エラー: {e}")

    def draw_schedule_items(self, schedules, cell_width, cell_height, days, time_slots):
        """スケジュールアイテムを描画"""
        canvas = self.schedule_canvas
        
        # 色のマッピング
        colors = [
            "#ffcdd2", "#f8bbd0", "#e1bee7", "#d1c4e9", "#c5cae9",
            "#bbdefb", "#b3e5fc", "#b2ebf2", "#b2dfdb", "#c8e6c9",
            "#dcedc8", "#f0f4c3", "#fff9c4", "#ffecb3", "#ffe0b2"
        ]
        
        staff_colors = {}
        color_idx = 0
        
        for schedule in schedules:
            day = schedule.get('day_of_week', '')
            if day not in days:
                continue
            
            # 支援員ごとの色を割り当て
            staff_name = schedule.get('staff_name', '')
            if staff_name not in staff_colors:
                staff_colors[staff_name] = colors[color_idx % len(colors)]
                color_idx += 1
            
            # 位置計算
            day_idx = days.index(day)
            start_time = schedule.get('start_time', '')
            end_time = schedule.get('end_time', '')
            
            try:
                start_hour = int(start_time.split(':')[0])
                end_hour = int(end_time.split(':')[0])
                start_min = int(start_time.split(':')[1])
                end_min = int(end_time.split(':')[1])
                
                # 9時を基準にしたインデックス
                start_slot = start_hour - 9
                end_slot = end_hour - 9
                
                # 座標計算
                x = 80 + day_idx * cell_width + 2
                y = 40 + start_slot * cell_height + (start_min / 60 * cell_height) + 2
                height = (end_slot - start_slot) * cell_height + (end_min / 60 * cell_height) - 4
                
                # カードを描画
                card_color = staff_colors[staff_name]
                card = canvas.create_rectangle(
                    x, y, x + cell_width - 4, y + height,
                    fill=card_color,
                    outline="#333",
                    width=2,
                    tags=("schedule_item", f"schedule_{schedule.get('id', '')}")
                )
                
                # テキスト
                text_content = f"{staff_name}\n{start_time}-{end_time}"
                text = canvas.create_text(
                    x + (cell_width - 4) // 2,
                    y + height // 2,
                    text=text_content,
                    font=("游ゴシック", 8),
                    tags=("schedule_item", f"schedule_{schedule.get('id', '')}")
                )
                
            except (ValueError, IndexError) as e:
                print(f"時間解析エラー: {e}")
                continue

    def refresh_schedule(self, event=None):
        """スケジュールを更新"""
        self.draw_schedule_grid()

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
                messagebox.showinfo("完了", "支援員を削除しました")
                self.refresh_staff_tree()
            except Exception as e:
                print(f"削除エラー: {e}")
                messagebox.showerror("エラー", f"削除中にエラーが発生しました: {e}")
