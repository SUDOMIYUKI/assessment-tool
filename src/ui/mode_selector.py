import tkinter as tk
from tkinter import ttk, messagebox

class ModeSelectorDialog(tk.Toplevel):
    def __init__(self, parent, history_count=0):
        super().__init__(parent)
        
        self.selected_mode = None
        self.history_count = history_count
        
        self.title("分析モードを選択")
        self.geometry("650x600")
        self.minsize(600, 550)
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
        header_frame = tk.Frame(self, bg="#4A90E2", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame,
            text="📊 分析モードを選択してください",
            font=("游ゴシック", 16, "bold"),
            bg="#4A90E2",
            fg="white"
        )
        title.pack(pady=25)
        
        # メインコンテンツ（スクロール可能）
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # レイアウト
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # マウスホイールでスクロール
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        main_frame = tk.Frame(scrollable_frame, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        
        # モード1: データ活用モード（統合モード）
        mode1_frame = tk.LabelFrame(
            main_frame,
            text="🔍 データ活用モード（オフライン）",
            font=("游ゴシック", 12, "bold"),
            padx=15,
            pady=15
        )
        mode1_frame.pack(fill="x", pady=10)
        
        tk.Label(
            mode1_frame,
            text="テンプレートと過去データを統合して選択",
            font=("游ゴシック", 10),
            fg="gray"
        ).pack(anchor="w")
        
        tk.Label(
            mode1_frame,
            text="✓ テンプレートと過去データを同時表示\n✓ より多くの選択肢から最適なものを選択\n✓ 効率的で柔軟なアセスメント作成",
            font=("游ゴシック", 9),
            justify="left"
        ).pack(anchor="w", pady=(5, 10))
        
        data_btn = tk.Button(
            mode1_frame,
            text="🔍 データ活用モードで作成",
            font=("游ゴシック", 11, "bold"),
            bg="#F5A623",
            fg="white",
            command=lambda: self.select_mode('integrated'),
            padx=20,
            pady=10
        )
        data_btn.pack(anchor="w", pady=(10, 0))
        
        # デバッグ情報
        print(f"🔧 デバッグ: データ活用モードボタンを作成しました - 履歴数: {self.history_count}")
        
        
        # モード2: AI分析モード
        mode2_frame = tk.LabelFrame(
            main_frame,
            text="🤖 AI分析モード（オンライン）",
            font=("游ゴシック", 12, "bold"),
            padx=15,
            pady=15
        )
        mode2_frame.pack(fill="x", pady=10)
        
        tk.Label(
            mode2_frame,
            text="Claude AIで詳細分析",
            font=("游ゴシック", 10),
            fg="gray"
        ).pack(anchor="w")
        
        tk.Label(
            mode2_frame,
            text="✓ 最高品質の分析\n✓ 柔軟な対応\n✓ 複雑なケースに最適\n※ ネット接続が必要",
            font=("游ゴシック", 9),
            justify="left"
        ).pack(anchor="w", pady=(5, 10))
        
        ai_btn = tk.Button(
            mode2_frame,
            text="🤖 AI分析モードで作成",
            font=("游ゴシック", 11, "bold"),
            bg="#4A90E2",
            fg="white",
            command=lambda: self.select_mode('ai'),
            padx=20,
            pady=8
        )
        ai_btn.pack(anchor="w")
        
        # キャンセルボタン
        cancel_btn = tk.Button(
            main_frame,
            text="キャンセル",
            command=self.destroy,
            padx=15,
            pady=5
        )
        cancel_btn.pack(side="bottom", pady=(20, 0))
    
    def select_mode(self, mode):
        self.selected_mode = mode
        self.destroy()
    
    def get_selected_mode(self):
        return self.selected_mode


