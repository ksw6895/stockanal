import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import markdown
from jinja2 import Template
# Rich imports removed for server compatibility

from .value_analyzer import AnalysisResult, InvestmentGrade

# Console removed for server compatibility

class ReportGenerator:
    def __init__(self, reports_dir: str = "reports"):
        self.logger = logging.getLogger(__name__)
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
        
        # 보고서 템플릿들
        self.templates = {
            'individual_report': self._get_individual_report_template(),
            'comparison_report': self._get_comparison_report_template(),
            'summary_report': self._get_summary_report_template()
        }
        
        console.print(f"[green]보고서 생성기 초기화 완료 (저장 경로: {self.reports_dir})[/green]")
    
    def generate_individual_report(self, analysis_result: AnalysisResult, 
                                 ai_analysis: str, 
                                 format_type: str = "markdown") -> str:
        """
        개별 종목 분석 보고서를 생성합니다.
        
        Args:
            analysis_result: 분석 결과
            ai_analysis: AI 생성 분석 내용
            format_type: 보고서 형식 ("markdown", "html", "json")
        
        Returns:
            str: 생성된 보고서 파일 경로
        """
        try:
            print("📝 보고서 생성 중...")
                
                # 파일명 생성
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{analysis_result.symbol}_analysis_{timestamp}.{format_type}"
                filepath = self.reports_dir / filename
                
                # 보고서 데이터 준비
                report_data = {
                    'analysis_result': analysis_result.to_dict(),
                    'ai_analysis': ai_analysis,
                    'generated_at': datetime.now().isoformat(),
                    'report_type': 'individual'
                }
                
                # 형식에 따라 보고서 생성
                if format_type == "json":
                    content = self._generate_json_report(report_data)
                elif format_type == "html":
                    content = self._generate_html_report(report_data, 'individual_report')
                else:  # markdown (기본값)
                    content = self._generate_markdown_report(report_data, 'individual_report')
                
                # 파일 저장
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                progress.update(task, description=f"[green]보고서 생성 완료: {filename}")
                
                console.print(f"[green]✓ 개별 보고서 저장됨: {filepath}[/green]")
                
                return str(filepath)
                
        except Exception as e:
            self.logger.error(f"개별 보고서 생성 중 오류: {str(e)}")
            raise Exception(f"보고서 생성 실패: {str(e)}")
    
    def generate_comparison_report(self, analysis_results: List[AnalysisResult], 
                                 ai_analysis: str, 
                                 format_type: str = "markdown") -> str:
        """
        비교 분석 보고서를 생성합니다.
        
        Args:
            analysis_results: 분석 결과 리스트
            ai_analysis: AI 생성 비교 분석 내용
            format_type: 보고서 형식
        
        Returns:
            str: 생성된 보고서 파일 경로
        """
        try:
            print("📝 보고서 생성 중...")
                
                # 파일명 생성
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                symbols = "_vs_".join([result.symbol for result in analysis_results])
                filename = f"comparison_{symbols}_{timestamp}.{format_type}"
                filepath = self.reports_dir / filename
                
                # 보고서 데이터 준비
                report_data = {
                    'analysis_results': [result.to_dict() for result in analysis_results],
                    'ai_analysis': ai_analysis,
                    'generated_at': datetime.now().isoformat(),
                    'report_type': 'comparison',
                    'symbols': [result.symbol for result in analysis_results]
                }
                
                # 형식에 따라 보고서 생성
                if format_type == "json":
                    content = self._generate_json_report(report_data)
                elif format_type == "html":
                    content = self._generate_html_report(report_data, 'comparison_report')
                else:  # markdown (기본값)
                    content = self._generate_markdown_report(report_data, 'comparison_report')
                
                # 파일 저장
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                progress.update(task, description=f"[green]비교 보고서 생성 완료: {filename}")
                
                console.print(f"[green]✓ 비교 분석 보고서 저장됨: {filepath}[/green]")
                
                return str(filepath)
                
        except Exception as e:
            self.logger.error(f"비교 보고서 생성 중 오류: {str(e)}")
            raise Exception(f"비교 보고서 생성 실패: {str(e)}")
    
    def generate_summary_report(self, analysis_results: List[AnalysisResult], 
                              additional_info: Optional[Dict] = None,
                              format_type: str = "markdown") -> str:
        """
        요약 보고서를 생성합니다.
        
        Args:
            analysis_results: 분석 결과 리스트
            additional_info: 추가 정보
            format_type: 보고서 형식
        
        Returns:
            str: 생성된 보고서 파일 경로
        """
        try:
            print("📝 보고서 생성 중...")
                
                # 파일명 생성
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"summary_report_{timestamp}.{format_type}"
                filepath = self.reports_dir / filename
                
                # 요약 통계 계산
                summary_stats = self._calculate_summary_stats(analysis_results)
                
                # 보고서 데이터 준비
                report_data = {
                    'analysis_results': [result.to_dict() for result in analysis_results],
                    'summary_stats': summary_stats,
                    'additional_info': additional_info or {},
                    'generated_at': datetime.now().isoformat(),
                    'report_type': 'summary'
                }
                
                # 형식에 따라 보고서 생성
                if format_type == "json":
                    content = self._generate_json_report(report_data)
                elif format_type == "html":
                    content = self._generate_html_report(report_data, 'summary_report')
                else:  # markdown (기본값)
                    content = self._generate_markdown_report(report_data, 'summary_report')
                
                # 파일 저장
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                progress.update(task, description=f"[green]요약 보고서 생성 완료: {filename}")
                
                console.print(f"[green]✓ 요약 보고서 저장됨: {filepath}[/green]")
                
                return str(filepath)
                
        except Exception as e:
            self.logger.error(f"요약 보고서 생성 중 오류: {str(e)}")
            raise Exception(f"요약 보고서 생성 실패: {str(e)}")
    
    def _generate_json_report(self, report_data: Dict) -> str:
        """JSON 형식 보고서를 생성합니다."""
        return json.dumps(report_data, indent=2, ensure_ascii=False, default=str)
    
    def _generate_markdown_report(self, report_data: Dict, template_name: str) -> str:
        """Markdown 형식 보고서를 생성합니다."""
        template = Template(self.templates[template_name])
        return template.render(**report_data)
    
    def _generate_html_report(self, report_data: Dict, template_name: str) -> str:
        """HTML 형식 보고서를 생성합니다."""
        # 먼저 Markdown 생성
        markdown_content = self._generate_markdown_report(report_data, template_name)
        
        # Markdown을 HTML로 변환
        html_content = markdown.markdown(markdown_content, extensions=['tables', 'toc'])
        
        # HTML 템플릿에 적용
        html_template = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>주식 가치투자 분석 보고서</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f9f9f9;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1, h2, h3 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        .grade-strong-buy {{ color: #27ae60; font-weight: bold; }}
        .grade-buy {{ color: #2ecc71; font-weight: bold; }}
        .grade-hold {{ color: #f39c12; font-weight: bold; }}
        .grade-sell {{ color: #e74c3c; font-weight: bold; }}
        .grade-strong-sell {{ color: #c0392b; font-weight: bold; }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_content}
        <div class="footer">
            <p>본 보고서는 AI 기반 주식 가치투자 분석 시스템에 의해 생성되었습니다.</p>
            <p>생성일시: {report_data.get('generated_at', 'Unknown')}</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html_template
    
    def _calculate_summary_stats(self, analysis_results: List[AnalysisResult]) -> Dict:
        """요약 통계를 계산합니다."""
        if not analysis_results:
            return {}
        
        # 등급별 분포
        grade_distribution = {}
        for result in analysis_results:
            grade = result.investment_grade.value
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
        
        # 평균 지표 계산
        pe_ratios = [r.value_metrics.pe_ratio for r in analysis_results if r.value_metrics.pe_ratio > 0]
        pb_ratios = [r.value_metrics.pb_ratio for r in analysis_results if r.value_metrics.pb_ratio > 0]
        roe_values = [r.value_metrics.roe for r in analysis_results if r.value_metrics.roe > 0]
        
        return {
            'total_stocks': len(analysis_results),
            'grade_distribution': grade_distribution,
            'avg_pe_ratio': sum(pe_ratios) / len(pe_ratios) if pe_ratios else 0,
            'avg_pb_ratio': sum(pb_ratios) / len(pb_ratios) if pb_ratios else 0,
            'avg_roe': sum(roe_values) / len(roe_values) if roe_values else 0,
            'avg_upside_potential': sum(r.upside_potential for r in analysis_results) / len(analysis_results),
            'best_performer': max(analysis_results, key=lambda x: x.upside_potential).symbol,
            'worst_performer': min(analysis_results, key=lambda x: x.upside_potential).symbol
        }
    
    def _get_individual_report_template(self) -> str:
        """개별 보고서 템플릿을 반환합니다."""
        return """
# {{ analysis_result.company_name }} ({{ analysis_result.symbol }}) 가치투자 분석 보고서

**분석일시:** {{ generated_at }}  
**투자등급:** {{ analysis_result.investment_grade }}  
**신뢰도:** {{ analysis_result.confidence_score|round(1) }}%  

---

## 📊 핵심 정보

| 항목 | 값 |
|------|-----|
| 현재 주가 | ${{ analysis_result.current_price|round(2) }} |
| 목표 주가 | ${{ analysis_result.target_price|round(2) }} |
| 상승 여력 | {{ analysis_result.upside_potential|round(1) }}% |
| 시장 | {{ analysis_result.company_name }} |

---

## 📈 주요 재무 지표

| 지표 | 값 |
|------|-----|
| PER | {{ analysis_result.value_metrics.pe_ratio|round(2) }} |
| PBR | {{ analysis_result.value_metrics.pb_ratio|round(2) }} |
| PEG | {{ analysis_result.value_metrics.peg_ratio|round(2) }} |
| ROE | {{ (analysis_result.value_metrics.roe * 100)|round(2) }}% |
| ROA | {{ (analysis_result.value_metrics.roa * 100)|round(2) }}% |
| 부채비율 | {{ analysis_result.value_metrics.debt_to_equity|round(2) }} |
| 배당수익률 | {{ (analysis_result.value_metrics.dividend_yield * 100)|round(2) }}% |
| 매출 성장률 | {{ analysis_result.value_metrics.revenue_growth|round(1) }}% |
| 순이익 성장률 | {{ analysis_result.value_metrics.income_growth|round(1) }}% |

---

## ✅ 주요 강점

{% for strength in analysis_result.key_strengths %}
- {{ strength }}
{% endfor %}

---

## ⚠️ 주요 약점

{% for weakness in analysis_result.key_weaknesses %}
- {{ weakness }}
{% endfor %}

---

## 🚨 위험 요인

{% for risk in analysis_result.risks %}
- {{ risk }}
{% endfor %}

---

## 🤖 AI 종합 분석

{{ ai_analysis }}

---

## 📋 투자 의견

**등급:** {{ analysis_result.investment_grade }}  
**목표가:** ${{ analysis_result.target_price|round(2) }}  
**상승여력:** {{ analysis_result.upside_potential|round(1) }}%  

---

*본 보고서는 AI 기반 분석 시스템에 의해 생성되었으며, 투자 참고용으로만 활용하시기 바랍니다.*
"""
    
    def _get_comparison_report_template(self) -> str:
        """비교 보고서 템플릿을 반환합니다."""
        return """
# 주식 비교 분석 보고서

**분석일시:** {{ generated_at }}  
**비교 종목:** {{ symbols|join(', ') }}  

---

## 📊 종목별 요약

| 종목 | 등급 | 현재가 | 목표가 | 상승여력 | PER | PBR | ROE |
|------|------|---------|---------|----------|-----|-----|-----|
{% for result in analysis_results %}
| {{ result.symbol }} | {{ result.investment_grade }} | ${{ result.current_price|round(2) }} | ${{ result.target_price|round(2) }} | {{ result.upside_potential|round(1) }}% | {{ result.value_metrics.pe_ratio|round(1) }} | {{ result.value_metrics.pb_ratio|round(1) }} | {{ (result.value_metrics.roe * 100)|round(1) }}% |
{% endfor %}

---

## 📈 상세 비교 분석

{% for result in analysis_results %}
### {{ result.symbol }} - {{ result.company_name }}

**투자등급:** {{ result.investment_grade }}  
**상승여력:** {{ result.upside_potential|round(1) }}%  

**주요 강점:**
{% for strength in result.key_strengths %}
- {{ strength }}
{% endfor %}

**주요 약점:**
{% for weakness in result.key_weaknesses %}
- {{ weakness }}
{% endfor %}

---
{% endfor %}

## 🤖 AI 종합 비교 분석

{{ ai_analysis }}

---

*본 보고서는 AI 기반 분석 시스템에 의해 생성되었으며, 투자 참고용으로만 활용하시기 바랍니다.*
"""
    
    def _get_summary_report_template(self) -> str:
        """요약 보고서 템플릿을 반환합니다."""
        return """
# 포트폴리오 분석 요약 보고서

**분석일시:** {{ generated_at }}  
**분석 종목 수:** {{ summary_stats.total_stocks }}개  

---

## 📊 투자등급 분포

{% for grade, count in summary_stats.grade_distribution.items() %}
- {{ grade }}: {{ count }}개 종목
{% endfor %}

---

## 📈 평균 재무지표

| 지표 | 평균값 |
|------|--------|
| PER | {{ summary_stats.avg_pe_ratio|round(2) }} |
| PBR | {{ summary_stats.avg_pb_ratio|round(2) }} |
| ROE | {{ (summary_stats.avg_roe * 100)|round(2) }}% |
| 평균 상승여력 | {{ summary_stats.avg_upside_potential|round(1) }}% |

---

## 🏆 최고 성과 예상 종목

**{{ summary_stats.best_performer }}** (최고 상승여력)

---

## 📉 최저 성과 예상 종목

**{{ summary_stats.worst_performer }}** (최저 상승여력)

---

## 📋 전체 종목 리스트

{% for result in analysis_results %}
### {{ result.symbol }} - {{ result.company_name }}
- **등급:** {{ result.investment_grade }}
- **상승여력:** {{ result.upside_potential|round(1) }}%
- **PER:** {{ result.value_metrics.pe_ratio|round(1) }}
- **ROE:** {{ (result.value_metrics.roe * 100)|round(1) }}%

{% endfor %}

---

*본 보고서는 AI 기반 분석 시스템에 의해 생성되었으며, 투자 참고용으로만 활용하시기 바랍니다.*
"""
    
    def list_reports(self) -> List[Dict]:
        """저장된 보고서 목록을 반환합니다."""
        reports = []
        
        for file_path in self.reports_dir.glob("*"):
            if file_path.is_file():
                stat = file_path.stat()
                reports.append({
                    'filename': file_path.name,
                    'filepath': str(file_path),
                    'size': stat.st_size,
                    'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        # 수정일 기준 내림차순 정렬
        reports.sort(key=lambda x: x['modified_at'], reverse=True)
        
        return reports
    
    def delete_report(self, filename: str) -> bool:
        """보고서를 삭제합니다."""
        try:
            file_path = self.reports_dir / filename
            if file_path.exists():
                file_path.unlink()
                console.print(f"[green]✓ 보고서 삭제됨: {filename}[/green]")
                return True
            else:
                console.print(f"[red]✗ 파일을 찾을 수 없음: {filename}[/red]")
                return False
        except Exception as e:
            console.print(f"[red]✗ 파일 삭제 실패: {str(e)}[/red]")
            return False
    
    def get_report_content(self, filename: str) -> Optional[str]:
        """보고서 내용을 반환합니다."""
        try:
            file_path = self.reports_dir / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            return None
        except Exception as e:
            self.logger.error(f"보고서 읽기 실패: {str(e)}")
            return None