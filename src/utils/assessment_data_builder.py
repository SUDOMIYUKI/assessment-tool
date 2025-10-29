"""
アセスメントデータビルダー
- 入力フォームのデータをアセスメントシート用のデータ形式に変換
"""

from typing import Dict


def build_assessment_data(form_data: Dict) -> Dict:
    """
    フォームデータをアセスメントシート用のデータ形式に変換
    
    Args:
        form_data: photo_input_formやsmart_input_formから取得したデータ
        
    Returns:
        アセスメントシート用のデータ辞書
    """
    assessment_data = {
        'issues': {},
        'short_term_plan': {},
        'long_term_plan': {},
        'missing_info': []
    }
    
    # 課題チェックリストの構築
    issues = assessment_data['issues']
    
    # 登校状況
    attendance = form_data.get('登校状況', {})
    if attendance.get('不登校該当'):
        issues['不登校'] = {
            '該当': True,
            '詳細': f"{attendance.get('頻度', '')} - {attendance.get('詳細', '')}"
        }
    
    # 生活リズム
    life_rhythm = form_data.get('生活リズム', [])
    if life_rhythm:
        issues['生活リズム'] = {
            '該当': True,
            '詳細': '、'.join(life_rhythm)
        }
    
    # 生活習慣
    life_habit = form_data.get('生活習慣', [])
    if life_habit:
        issues['生活習慣'] = {
            '該当': True,
            '詳細': '、'.join(life_habit)
        }
    
    # 学習課題
    study_issues = form_data.get('学習課題', [])
    if study_issues:
        issues['学習の遅れ・低学力'] = {
            '該当': True,
            '詳細': '、'.join(study_issues)
        }
    
    # 対人関係
    social_issues = form_data.get('対人関係課題', [])
    if social_issues:
        issues['対人緊張の高さ'] = {
            '該当': True,
            '詳細': '、'.join(social_issues)
        }
    
    # 発達特性
    developmental = form_data.get('発達特性', {})
    if developmental.get('該当'):
        issues['発達特性or発達課題'] = {
            '該当': True,
            '詳細': developmental.get('内容', '')
        }
    
    # 家庭環境
    family_issues = form_data.get('家庭環境課題', [])
    if family_issues:
        for issue in family_issues:
            if issue == '経済困難':
                issues['家庭環境'] = {
                    '該当': True,
                    '詳細': '経済的困難'
                }
            elif issue == '虐待':
                issues['虐待'] = {
                    '該当': True,
                    '詳細': ''
                }
            elif issue in ['家族関係', '他世帯員']:
                issues['他の世帯員の問題'] = {
                    '該当': True,
                    '詳細': issue
                }
    
    # 短期目標
    short_plan = form_data.get('短期目標', {})
    if short_plan:
        assessment_data['short_term_plan'] = {
            '課題': short_plan.get('課題', ''),
            '現状': short_plan.get('現状', ''),
            'ニーズ_本人': short_plan.get('ニーズ本人', ''),
            'ニーズ_保護者': short_plan.get('ニーズ保護者', ''),
            '目標': short_plan.get('目標', ''),
            '方法': short_plan.get('方法', '')
        }
    
    # 長期目標
    long_plan = form_data.get('長期目標', {})
    if long_plan:
        assessment_data['long_term_plan'] = {
            '課題': long_plan.get('課題', ''),
            '現状': long_plan.get('現状', ''),
            'ニーズ_本人': long_plan.get('ニーズ本人', ''),
            'ニーズ_保護者': long_plan.get('ニーズ保護者', ''),
            '目標': long_plan.get('目標', ''),
            '方法': long_plan.get('方法', '')
        }
    
    # 不足情報のチェック
    if not form_data.get('児童氏名'):
        assessment_data['missing_info'].append('児童氏名')
    
    if not form_data.get('保護者氏名'):
        assessment_data['missing_info'].append('保護者氏名')
    
    if not short_plan.get('目標'):
        assessment_data['missing_info'].append('短期目標')
    
    return assessment_data

