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
            ws = wb['ｱｾｽﾒﾝﾄｼｰﾄ']
        except KeyError:
            raise ValueError("テンプレートに'ｱｾｽﾒﾝﾄｼｰﾄ'シートが見つかりません")
        
        ws['C3'] = self._generate_support_number(interview_data['面談実施日'])
        ws['G3'] = interview_data['担当支援員']
        ws['H3'] = interview_data['面談実施日']
        
        ws['C4'] = interview_data['保護者氏名']
        ws['G4'] = interview_data['児童氏名']
        ws['O4'] = interview_data['性別']
        
        ws['C5'] = interview_data['学校名']
        ws['I5'] = str(interview_data['学年'])
        ws['N5'] = interview_data['ひとり親世帯']
        
        issues_text = self._format_issues_cell(assessment_data['issues'])
        ws['B11'] = issues_text
        
        future_path = assessment_data.get('future_path', {})
        checkbox_進学 = "■" if future_path.get('type') == "進学" else "□"
        checkbox_就職 = "■" if future_path.get('type') == "就職" else "□"
        
        path_text = f"""確認日　{interview_data['面談実施日'].strftime('%Y/%m/%d')}
{checkbox_進学}進学　　{checkbox_就職}就職
（具体的内容）
・{future_path.get('detail', '')}
"""
        ws['B18'] = path_text
        
        self._fill_support_plan(ws, assessment_data['short_term_plan'], start_row=29)
        
        if 'long_term_plan' in assessment_data:
            self._fill_support_plan(ws, assessment_data['long_term_plan'], start_row=35)
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        wb.save(str(output_path))
        print(f"✅ アセスメントシートを作成: {output_path}")
        
        return str(output_path)
    
    def _generate_support_number(self, date):
        return date.strftime('%Y%m%d')
    
    def _format_issues_cell(self, issues_data):
        lines = []
        
        for key, value in issues_data.items():
            checkbox = "☑" if value.get('該当') else "☐"
            detail = value.get('詳細', '')
            
            if key == "その他" and value.get('該当'):
                lines.append(f"{checkbox} {key}")
                if detail:
                    lines.append(f"・{detail}")
            else:
                if detail and detail not in ["該当なし", "特に問題なし", "不明", ""]:
                    lines.append(f"{checkbox} {key}（{detail}）")
                else:
                    lines.append(f"{checkbox} {key}")
        
        return "\n".join(lines)
    
    def _fill_support_plan(self, ws, plan_data, start_row):
        ws[f'B{start_row}'] = plan_data.get('現状', '')
        ws[f'E{start_row}'] = plan_data.get('ニーズ_本人', '')
        ws[f'E{start_row + 1}'] = plan_data.get('ニーズ_保護者', '')
        ws[f'I{start_row}'] = plan_data.get('目標', '')
        ws[f'M{start_row}'] = plan_data.get('方法', '')

