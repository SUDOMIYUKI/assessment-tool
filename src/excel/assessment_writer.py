import openpyxl
from datetime import datetime
from pathlib import Path

class AssessmentWriter:
    def __init__(self, template_path='templates/アセスメントシート原本.xlsx'):
        self.template_path = Path(template_path)
    
    def create_assessment_file(self, interview_data, assessment_data, output_path):
        if not self.template_path.exists():
            raise FileNotFoundError(
                f"テンプレートファイルが見つかりません: {self.template_path}\n"
                "templates/ディレクトリにアセスメントシート原本.xlsxを配置してください"
            )
        
        try:
            wb = openpyxl.load_workbook(str(self.template_path))
            # シート名を確認して適切なシートを選択
            sheet_names = wb.sheetnames
            print(f"利用可能なシート名: {sheet_names}")
            
            # アセスメントシートまたは類似の名前を探す
            target_sheet = None
            for sheet_name in sheet_names:
                if 'アセスメント' in sheet_name or 'assessment' in sheet_name.lower():
                    target_sheet = sheet_name
                    break
            
            if not target_sheet:
                # 最初のシートを使用
                target_sheet = sheet_names[0]
                print(f"アセスメントシートが見つからないため、最初のシート '{target_sheet}' を使用します")
            
            ws = wb[target_sheet]
        except Exception as e:
            raise ValueError(f"テンプレートファイルの読み込みエラー: {str(e)}")
        
        # 基本情報の入力
        self._fill_basic_info(ws, interview_data)
        
        # 世帯の具体的な課題の入力
        self._fill_household_issues(ws, assessment_data)
        
        # 希望する進路の入力
        self._fill_future_path(ws, assessment_data, interview_data)
        
        # 支援計画の入力
        self._fill_support_plans(ws, assessment_data)
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        wb.save(str(output_path))
        print(f"✅ アセスメントシートを作成: {output_path}")
        
        return str(output_path)
    
    def _fill_basic_info(self, ws, interview_data):
        """基本情報を入力"""
        # 支援番号（日付ベース）
        if '面談実施日' in interview_data and interview_data['面談実施日']:
            date_obj = interview_data['面談実施日']
            if isinstance(date_obj, datetime):
                support_number = date_obj.strftime('%Y%m%d')
            else:
                support_number = date_obj
            ws['C3'] = support_number
        
        # 担当支援員
        ws['G3'] = interview_data.get('担当支援員', '')
        
        # 面談実施日
        if '面談実施日' in interview_data and interview_data['面談実施日']:
            date_obj = interview_data['面談実施日']
            if isinstance(date_obj, datetime):
                ws['H3'] = date_obj.strftime('%m月%d日')
            else:
                ws['H3'] = date_obj
        
        # 世帯主氏名（保護者氏名）
        ws['C4'] = interview_data.get('保護者氏名', '')
        
        # 児童氏名
        ws['G4'] = interview_data.get('児童氏名', '')
        
        # 性別
        ws['O4'] = interview_data.get('性別', '')
        
        # 学校名
        ws['C5'] = interview_data.get('学校名', '')
        
        # 学年
        ws['I5'] = str(interview_data.get('学年', ''))
        
        # ひとり親世帯
        ws['N5'] = interview_data.get('ひとり親世帯', '該当しない')
    
    def _fill_household_issues(self, ws, assessment_data):
        """世帯の具体的な課題を入力"""
        issues_data = assessment_data.get('issues', {})
        
        # 各課題項目のチェックボックスと詳細を設定
        issue_mappings = {
            '不登校': {'row': 11, 'col': 'B'},
            '引きこもり': {'row': 11, 'col': 'H'},
            '生活リズム': {'row': 12, 'col': 'B'},
            '生活習慣': {'row': 12, 'col': 'H'},
            '学習の遅れ・低学力': {'row': 13, 'col': 'B'},
            '学習習慣・環境': {'row': 13, 'col': 'H'},
            '発達特性or発達課題': {'row': 14, 'col': 'B'},
            '対人緊張の高さ': {'row': 14, 'col': 'H'},
            'コミュニケーションに苦手意識': {'row': 15, 'col': 'B'},
            '家庭環境': {'row': 15, 'col': 'H'},
            '虐待': {'row': 16, 'col': 'B'},
            'その他': {'row': 16, 'col': 'H'}
        }
        
        for issue_name, mapping in issue_mappings.items():
            if issue_name in issues_data:
                issue_data = issues_data[issue_name]
                checkbox = "■" if issue_data.get('該当', False) else "□"
                detail = issue_data.get('詳細', '')
                
                if detail and detail.strip():
                    cell_value = f"{checkbox}{issue_name}({detail})"
                else:
                    cell_value = f"{checkbox}{issue_name}"
                
                ws[f"{mapping['col']}{mapping['row']}"] = cell_value
    
    def _fill_future_path(self, ws, assessment_data, interview_data):
        """希望する進路を入力"""
        future_path = assessment_data.get('future_path', {})
        
        # 確認日
        if '面談実施日' in interview_data and interview_data['面談実施日']:
            date_obj = interview_data['面談実施日']
            if isinstance(date_obj, datetime):
                confirm_date = date_obj.strftime('%Y/%m/%d')
            else:
                confirm_date = date_obj
        else:
            confirm_date = ''
        
        # 進学・就職のチェックボックス
        path_type = future_path.get('type', '')
        checkbox_進学 = "■" if path_type == "進学" else "□"
        checkbox_就職 = "■" if path_type == "就職" else "□"
        
        # 具体的内容
        detail = future_path.get('detail', '')
        
        # B18セルに進路情報を設定
        path_text = f"確認日　{confirm_date}\n{checkbox_進学}進学　　{checkbox_就職}就職\n（具体的内容）\n・{detail}"
        ws['B18'] = path_text
    
    def _fill_support_plans(self, ws, assessment_data):
        """支援計画を入力"""
        # 短期目標（支援計画）
        short_term_plan = assessment_data.get('short_term_plan', {})
        self._fill_support_plan_table(ws, short_term_plan, start_row=29)
        
        # 長期目標（本事業における達成目標）
        long_term_plan = assessment_data.get('long_term_plan', {})
        self._fill_support_plan_table(ws, long_term_plan, start_row=35)
    
    def _fill_support_plan_table(self, ws, plan_data, start_row):
        """支援計画テーブルを入力"""
        # 課題
        ws[f'B{start_row}'] = plan_data.get('課題', '')
        
        # 現状
        ws[f'D{start_row}'] = plan_data.get('現状', '')
        
        # ニーズ（本人）
        ws[f'F{start_row}'] = plan_data.get('ニーズ_本人', '')
        
        # ニーズ（保護者）
        ws[f'F{start_row + 1}'] = plan_data.get('ニーズ_保護者', '')
        
        # 目標
        ws[f'J{start_row}'] = plan_data.get('目標', '')
        
        # 具体的な方法
        ws[f'N{start_row}'] = plan_data.get('具体的な方法', '')