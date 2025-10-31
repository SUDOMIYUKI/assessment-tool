import json
import sys
from pathlib import Path
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# configをインポート（パスワード設定を取得するため）
import config

# Excel生成スクリプトをインポート
from src.excel.excel_generator_with_password import generate_assessment_sheet

class AssessmentWriter:
    def __init__(self, template_path='templates/アセスメントシート原本.xlsx'):
        self.template_path = Path(template_path)
    
    def create_assessment_file(self, interview_data, assessment_data, output_path):
        """アセスメントシートExcelファイルを作成（Python版 - 書式完全保持）"""
        
        if not self.template_path.exists():
            raise FileNotFoundError(f"テンプレートが見つかりません: {self.template_path}")
        
        # データを整形
        data = self._format_data_for_python(interview_data, assessment_data, output_path)
        
        try:
            # Python スクリプトを直接実行
            print(f"📋 Python でファイルを生成中...")
            # config.pyの設定からパスワードを取得
            password = config.EXCEL_PASSWORD if config.EXCEL_PASSWORD else None
            result = generate_assessment_sheet(
                template_path=str(self.template_path),
                output_path=str(output_path),
                data=data,
                password=password  # config.pyで設定されたパスワードを使用
            )
            
            if result['success']:
                print(f"✅ アセスメントシートを作成: {output_path}")
                return str(output_path)
            else:
                raise RuntimeError(f"Excel生成エラー: {result.get('error', '不明なエラー')}")
            
        except Exception as e:
            raise RuntimeError(f"Excel生成エラー: {str(e)}")
    
    def _format_data_for_python(self, interview_data, assessment_data, output_path):
        """Python用にデータを整形"""
        
        # 支援番号生成
        date_obj = interview_data['面談実施日']
        if isinstance(date_obj, datetime):
            support_number = date_obj.strftime('%Y%m%d')
            interview_date = date_obj.strftime('%m月%d日')
            confirm_date = date_obj.strftime('%Y年%m月%d日')
        else:
            support_number = str(date_obj)
            interview_date = str(date_obj)
            confirm_date = str(date_obj)
        
        # 課題データを整形
        issues = {}
        for issue_name, issue_data in assessment_data['issues'].items():
            issues[issue_name] = {
                'checked': issue_data.get('該当', False),
                'detail': issue_data.get('詳細', '')
            }
        
        # 短期目標を整形
        short_term = assessment_data.get('short_term_plan', {})
        short_term_plan = {
            'issue': short_term.get('課題', ''),
            'currentStatus': short_term.get('現状', ''),
            'needsChild': short_term.get('ニーズ_本人', ''),
            'needsGuardian': short_term.get('ニーズ_保護者', ''),
            'goal': short_term.get('目標', ''),
            'method': short_term.get('方法', '')
        } if short_term else None
        
        # 長期目標を整形
        long_term = assessment_data.get('long_term_plan', {})
        long_term_plan = {
            'issue': long_term.get('課題', ''),
            'currentStatus': long_term.get('現状', ''),
            'needsChild': long_term.get('ニーズ_本人', ''),
            'needsGuardian': long_term.get('ニーズ_保護者', ''),
            'goal': long_term.get('目標', ''),
            'method': long_term.get('方法', '')
        } if long_term else None
        
        return {
            'supportNumber': support_number,
            'supporter': interview_data.get('担当支援員', ''),
            'interviewDate': interview_date,
            'guardianName': interview_data.get('保護者氏名', ''),
            'childName': interview_data.get('児童氏名', ''),
            'gender': interview_data.get('性別', ''),
            'schoolName': interview_data.get('学校名', ''),
            'grade': interview_data.get('学年', 2),
            'singleParent': interview_data.get('ひとり親世帯', '該当しない'),
            'issues': issues,
            'futurePath': {
                'type': assessment_data.get('future_path', {}).get('type', ''),
                'detail': assessment_data.get('future_path', {}).get('detail', '')
            },
            'confirmDate': confirm_date,
            'shortTermPlan': short_term_plan,
            'longTermPlan': long_term_plan
        }