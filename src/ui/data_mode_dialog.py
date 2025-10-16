import tkinter as tk
from tkinter import ttk, messagebox
from src.database.history import HistoryManager

class DataModeDialog(tk.Toplevel):
    def __init__(self, parent, interview_data):
        super().__init__(parent)
        
        self.interview_data = interview_data
        self.history_manager = HistoryManager()
        self.selected_case = None
        
        self.title("データ活用モード - 過去の似たケースを検索")
        self.geometry("1000x700")
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        self.search_similar_cases()
        
        # 中央に配置
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f'+{x}+{y}')
    
    def create_widgets(self):
        # ヘッダー
        header_frame = tk.Frame(self, bg="#F5A623", height=70)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame,
            text="🔍 データ活用モード - 過去の似たケースを検索",
            font=("游ゴシック", 14, "bold"),
            bg="#F5A623",
            fg="white"
        )
        title.pack(pady=20)
        
        # 説明
        info_frame = tk.Frame(self, bg="#FFF9E6", height=60)
        info_frame.pack(fill="x", padx=10, pady=10)
        info_frame.pack_propagate(False)
        
        info_label = tk.Label(
            info_frame,
            text="💡 現在の入力内容に似た過去のケースを検索しています。参考にしたいケースを選択してください。",
            bg="#FFF9E6",
            fg="#666",
            font=("游ゴシック", 10),
            wraplength=900
        )
        info_label.pack(padx=10, pady=10)
        
        # メインエリア
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 左側：ケース一覧
        left_frame = ttk.LabelFrame(main_frame, text="類似ケース一覧", padding=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # リストボックス
        list_frame = tk.Frame(left_frame)
        list_frame.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.case_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=("游ゴシック", 10),
            height=20
        )
        self.case_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.case_listbox.yview)
        
        self.case_listbox.bind('<<ListboxSelect>>', self.on_case_selected)
        
        # リストボックスのマウスホイールスクロールを有効化
        def _on_listbox_mousewheel(event):
            self.case_listbox.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_listbox_mousewheel(event):
            self.case_listbox.bind_all("<MouseWheel>", _on_listbox_mousewheel)
        
        def _unbind_from_listbox_mousewheel(event):
            self.case_listbox.unbind_all("<MouseWheel>")
        
        self.case_listbox.bind('<Enter>', _bind_to_listbox_mousewheel)
        self.case_listbox.bind('<Leave>', _unbind_from_listbox_mousewheel)
        
        # 右側：詳細表示
        right_frame = ttk.LabelFrame(main_frame, text="ケース詳細", padding=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        self.detail_text = tk.Text(
            right_frame,
            wrap=tk.WORD,
            font=("游ゴシック", 10),
            height=20
        )
        self.detail_text.pack(fill="both", expand=True)
        
        # 詳細テキストのマウスホイールスクロールを有効化
        def _on_detail_mousewheel(event):
            self.detail_text.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_detail_mousewheel(event):
            self.detail_text.bind_all("<MouseWheel>", _on_detail_mousewheel)
        
        def _unbind_from_detail_mousewheel(event):
            self.detail_text.unbind_all("<MouseWheel>")
        
        self.detail_text.bind('<Enter>', _bind_to_detail_mousewheel)
        self.detail_text.bind('<Leave>', _unbind_from_detail_mousewheel)
        
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
        
        self.use_btn = tk.Button(
            button_frame,
            text="✅ このケースを参考にする",
            font=("游ゴシック", 11, "bold"),
            bg="#F5A623",
            fg="white",
            command=self.on_use_case,
            padx=20,
            pady=8,
            state="disabled"
        )
        self.use_btn.pack(side="right")
    
    def search_similar_cases(self):
        """類似ケースを検索"""
        similar_cases = self.history_manager.search_similar_cases(self.interview_data, limit=10)
        
        self.cases = similar_cases
        
        if not similar_cases:
            self.case_listbox.insert(tk.END, "類似するケースが見つかりませんでした")
            return
        
        for i, case in enumerate(similar_cases):
            grade = case.get('grade', '?')
            gender = case.get('gender', '?')
            date = case.get('interview_date', '不明')
            keywords = case.get('keywords', '')
            score = case.get('score', 0)
            
            # 学年表示
            if grade <= 6:
                grade_text = f"小{grade}"
            elif grade <= 9:
                grade_text = f"中{grade-6}"
            else:
                grade_text = f"高{grade-9}"
            
            display_text = f"[{grade_text}・{gender}] {date} | {keywords[:30]}..."
            if score > 0:
                display_text = f"★×{score} " + display_text
            
            self.case_listbox.insert(tk.END, display_text)
    
    def on_case_selected(self, event):
        """ケースが選択された時"""
        selection = self.case_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if index >= len(self.cases):
            return
        
        case = self.cases[index]
        
        # 詳細を表示
        self.detail_text.delete("1.0", tk.END)
        
        details = []
        details.append(f"【基本情報】")
        details.append(f"学年: {case.get('grade', '?')}年生")
        details.append(f"性別: {case.get('gender', '?')}")
        details.append(f"面談日: {case.get('interview_date', '不明')}")
        details.append("")
        
        details.append(f"【キーワード】")
        details.append(case.get('keywords', 'なし'))
        details.append("")
        
        details.append(f"【面談メモ】")
        memo = case.get('memo', '')
        details.append(memo[:500] + "..." if len(memo) > 500 else memo)
        details.append("")
        
        details.append(f"【課題】")
        issues = case.get('issues', {})
        for issue_name, issue_data in issues.items():
            if issue_data.get('該当'):
                detail = issue_data.get('詳細', '')
                if detail:
                    details.append(f"・{issue_name}: {detail}")
                else:
                    details.append(f"・{issue_name}")
        details.append("")
        
        details.append(f"【支援計画（短期）】")
        plan = case.get('short_term_plan', {})
        for key, value in plan.items():
            if value:
                details.append(f"{key}: {value}")
        
        self.detail_text.insert("1.0", "\n".join(details))
        
        self.selected_case = case
        self.use_btn.config(state="normal")
    
    def on_use_case(self):
        """このケースを使用"""
        if not self.selected_case:
            messagebox.showwarning("警告", "ケースを選択してください")
            return
        
        self.destroy()
    
    def get_selected_case(self):
        return self.selected_case


