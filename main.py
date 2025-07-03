#!/usr/bin/env python3
"""
AI 기반 주식 가치투자 분석 프로그램
Gemini 2.5 Flash를 활용한 실시간 주식 분석 도구
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
import asyncio

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown

# 로컬 모듈 import
from modules.stock_data_collector import StockDataCollector
from modules.gemini_client import GeminiClient
from modules.value_analyzer import ValueAnalyzer, AnalysisResult
from modules.report_generator import ReportGenerator

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_analyzer.log'),
        logging.StreamHandler()
    ]
)

console = Console()

class StockValueAnalyzer:
    """메인 애플리케이션 클래스"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 환경 변수 로드
        load_dotenv()
        
        # 컴포넌트 초기화
        self.stock_collector = StockDataCollector()
        self.gemini_client = None
        self.value_analyzer = ValueAnalyzer()
        self.report_generator = ReportGenerator()
        
        # 설정값
        self.default_report_format = os.getenv('REPORT_FORMAT', 'markdown')
        self.max_stocks_per_batch = int(os.getenv('MAX_STOCKS_PER_BATCH', '5'))
        
        console.print(Panel.fit("🚀 AI 기반 주식 가치투자 분석 시스템", style="bold blue"))
    
    def initialize_gemini_client(self) -> bool:
        """Gemini API 클라이언트를 초기화합니다."""
        try:
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                console.print("[red]❌ Google API 키가 설정되지 않았습니다.[/red]")
                console.print("📝 .env 파일을 생성하고 GOOGLE_API_KEY를 설정하세요.")
                return False
            
            self.gemini_client = GeminiClient(api_key)
            
            # 연결 테스트
            if self.gemini_client.test_connection():
                console.print("[green]✅ Gemini API 연결 성공[/green]")
                return True
            else:
                console.print("[red]❌ Gemini API 연결 실패[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]❌ Gemini 클라이언트 초기화 실패: {str(e)}[/red]")
            return False
    
    def get_user_input(self) -> Dict[str, Any]:
        """사용자 입력을 받습니다."""
        console.print("\n" + "="*50)
        console.print("📊 주식 분석 설정")
        console.print("="*50)
        
        # 분석 모드 선택
        mode_choices = {
            "1": "individual",
            "2": "comparison",
            "3": "portfolio"
        }
        
        console.print("\n🎯 분석 모드를 선택하세요:")
        console.print("1. 개별 종목 분석")
        console.print("2. 종목 비교 분석")
        console.print("3. 포트폴리오 분석")
        
        mode_choice = Prompt.ask("선택", choices=list(mode_choices.keys()), default="1")
        mode = mode_choices[mode_choice]
        
        # 종목 입력
        if mode == "individual":
            symbols = self._get_single_symbol()
        else:
            symbols = self._get_multiple_symbols()
        
        # 보고서 형식 선택
        format_choices = {
            "1": "markdown",
            "2": "html",
            "3": "json"
        }
        
        console.print("\n📄 보고서 형식을 선택하세요:")
        console.print("1. Markdown (기본)")
        console.print("2. HTML")
        console.print("3. JSON")
        
        format_choice = Prompt.ask("선택", choices=list(format_choices.keys()), default="1")
        report_format = format_choices[format_choice]
        
        # 분석 깊이 선택
        analysis_depth = Prompt.ask(
            "분석 깊이 (basic/detailed/comprehensive)", 
            default="comprehensive"
        )
        
        return {
            'mode': mode,
            'symbols': symbols,
            'report_format': report_format,
            'analysis_depth': analysis_depth
        }
    
    def _get_single_symbol(self) -> List[str]:
        """단일 종목 입력을 받습니다."""
        while True:
            symbol = Prompt.ask("분석할 종목 코드를 입력하세요 (예: AAPL, MSFT)").upper().strip()
            
            if self.stock_collector.validate_symbol(symbol):
                return [symbol]
            else:
                console.print(f"[red]❌ 유효하지 않은 종목 코드: {symbol}[/red]")
                
                # 유사한 종목 제안
                suggestions = self.stock_collector.search_similar_symbols(symbol)
                if suggestions:
                    console.print(f"💡 유사한 종목: {', '.join(suggestions)}")
                
                if not Confirm.ask("다시 입력하시겠습니까?"):
                    sys.exit(0)
    
    def _get_multiple_symbols(self) -> List[str]:
        """여러 종목 입력을 받습니다."""
        symbols = []
        
        console.print(f"\n📋 종목 코드를 입력하세요 (최대 {self.max_stocks_per_batch}개, 완료하려면 'done' 입력):")
        
        while len(symbols) < self.max_stocks_per_batch:
            symbol = Prompt.ask(f"종목 {len(symbols) + 1}").upper().strip()
            
            if symbol.lower() == 'done':
                break
            
            if symbol in symbols:
                console.print(f"[yellow]⚠️ 이미 추가된 종목: {symbol}[/yellow]")
                continue
            
            if self.stock_collector.validate_symbol(symbol):
                symbols.append(symbol)
                console.print(f"[green]✅ 추가됨: {symbol}[/green]")
            else:
                console.print(f"[red]❌ 유효하지 않은 종목 코드: {symbol}[/red]")
                
                # 유사한 종목 제안
                suggestions = self.stock_collector.search_similar_symbols(symbol)
                if suggestions:
                    console.print(f"💡 유사한 종목: {', '.join(suggestions)}")
        
        if not symbols:
            console.print("[red]❌ 종목이 선택되지 않았습니다.[/red]")
            sys.exit(0)
        
        return symbols
    
    def analyze_stocks(self, symbols: List[str], analysis_depth: str = "comprehensive") -> List[AnalysisResult]:
        """주식들을 분석합니다."""
        console.print(f"\n📊 {len(symbols)}개 종목 분석 시작...")
        
        # 1. 주식 데이터 수집
        console.print("\n1️⃣ 주식 데이터 수집 중...")
        stock_data = self.stock_collector.get_multiple_stocks_data(symbols)
        
        if not stock_data:
            console.print("[red]❌ 주식 데이터를 수집할 수 없습니다.[/red]")
            return []
        
        # 2. 가치투자 분석
        console.print("\n2️⃣ 가치투자 분석 중...")
        analysis_results = []
        
        for symbol, data in stock_data.items():
            try:
                result = self.value_analyzer.analyze_stock(data, self.gemini_client)
                analysis_results.append(result)
            except Exception as e:
                console.print(f"[red]❌ {symbol} 분석 실패: {str(e)}[/red]")
        
        # 3. AI 분석 (Gemini)
        console.print("\n3️⃣ AI 기반 심층 분석 중...")
        for i, result in enumerate(analysis_results):
            symbol = result.symbol
            if symbol in stock_data:
                try:
                    # 분석 깊이에 따른 프롬프트 생성
                    prompt = self._generate_analysis_prompt(analysis_depth)
                    
                    ai_analysis = self.gemini_client.generate_analysis(
                        prompt=prompt,
                        stock_data=stock_data[symbol],
                        thinking_enabled=True
                    )
                    
                    # AI 분석 결과를 기존 분석에 추가
                    result.detailed_analysis = ai_analysis
                    
                except Exception as e:
                    console.print(f"[yellow]⚠️ {symbol} AI 분석 실패: {str(e)}[/yellow]")
                    result.detailed_analysis = f"AI 분석 실패: {str(e)}"
        
        return analysis_results
    
    def _generate_analysis_prompt(self, depth: str) -> str:
        """분석 깊이에 따른 프롬프트를 생성합니다."""
        base_prompt = """
당신은 전문적인 가치투자 분석가입니다. 주어진 주식 데이터를 바탕으로 
워렌 버핏과 벤저민 그레이엄의 가치투자 철학에 따라 분석해주세요.
"""
        
        if depth == "basic":
            return base_prompt + """
기본적인 분석 항목:
1. 현재 밸류에이션 평가 (PER, PBR 중심)
2. 재무 건전성 간단 평가
3. 투자 권고 및 간단한 이유
"""
        elif depth == "detailed":
            return base_prompt + """
상세 분석 항목:
1. 밸류에이션 분석 (PER, PBR, PEG, 배당수익률)
2. 재무 건전성 분석 (부채비율, 유동성)
3. 성장성 분석 (매출·이익 성장률)
4. 경쟁우위 및 비즈니스 모델 평가
5. 위험 요인 분석
6. 목표가 및 투자 전략 제시
"""
        else:  # comprehensive
            return base_prompt + """
종합적 분석 항목:
1. 심층 밸류에이션 분석
   - 다양한 밸류에이션 지표 분석
   - 동종업계 비교 분석
   - 내재가치 추정

2. 재무 분석
   - 재무제표 3년간 트렌드 분석
   - 현금흐름 분석
   - 자본구조 분석

3. 비즈니스 분석
   - 경쟁우위 및 해자(Moat) 분석
   - 산업 전망 및 시장 포지션
   - 경영진 평가

4. 위험 분석
   - 시장 위험, 신용 위험, 유동성 위험
   - 경영 위험, 산업 위험
   - 거시경제 위험

5. 투자 전략
   - 장기 투자 관점에서의 매력도
   - 적정 매수 시점 및 목표가
   - 포트폴리오 내 적정 비중

6. ESG 요소 고려사항

각 항목을 구체적인 근거와 함께 분석하고, 
최종적으로 명확한 투자 의견을 제시해주세요.
"""
    
    def generate_reports(self, analysis_results: List[AnalysisResult], 
                        mode: str, report_format: str) -> List[str]:
        """보고서를 생성합니다."""
        console.print(f"\n📄 {report_format.upper()} 보고서 생성 중...")
        
        report_paths = []
        
        if mode == "individual":
            # 개별 보고서 생성
            for result in analysis_results:
                try:
                    path = self.report_generator.generate_individual_report(
                        analysis_result=result,
                        ai_analysis=result.detailed_analysis,
                        format_type=report_format
                    )
                    report_paths.append(path)
                except Exception as e:
                    console.print(f"[red]❌ {result.symbol} 보고서 생성 실패: {str(e)}[/red]")
        
        elif mode == "comparison":
            # 비교 분석 보고서 생성
            try:
                # 종목들 간 비교 분석을 위한 AI 분석
                symbols = [result.symbol for result in analysis_results]
                stock_data = {}
                
                for result in analysis_results:
                    # 임시로 주식 데이터 재구성 (실제로는 이전에 수집한 데이터 사용)
                    stock_data[result.symbol] = {
                        'symbol': result.symbol,
                        'company_name': result.company_name,
                        'current_price': result.current_price,
                        'financial_metrics': result.value_metrics.to_dict()
                    }
                
                comparison_analysis = self.gemini_client.generate_comparison_analysis(
                    stocks_data=stock_data
                )
                
                path = self.report_generator.generate_comparison_report(
                    analysis_results=analysis_results,
                    ai_analysis=comparison_analysis,
                    format_type=report_format
                )
                report_paths.append(path)
                
            except Exception as e:
                console.print(f"[red]❌ 비교 분석 보고서 생성 실패: {str(e)}[/red]")
        
        elif mode == "portfolio":
            # 포트폴리오 요약 보고서 생성
            try:
                path = self.report_generator.generate_summary_report(
                    analysis_results=analysis_results,
                    format_type=report_format
                )
                report_paths.append(path)
                
                # 개별 보고서도 생성
                for result in analysis_results:
                    try:
                        path = self.report_generator.generate_individual_report(
                            analysis_result=result,
                            ai_analysis=result.detailed_analysis,
                            format_type=report_format
                        )
                        report_paths.append(path)
                    except Exception as e:
                        console.print(f"[yellow]⚠️ {result.symbol} 개별 보고서 생성 실패: {str(e)}[/yellow]")
                        
            except Exception as e:
                console.print(f"[red]❌ 포트폴리오 보고서 생성 실패: {str(e)}[/red]")
        
        return report_paths
    
    def display_results(self, analysis_results: List[AnalysisResult]):
        """분석 결과를 화면에 표시합니다."""
        console.print("\n" + "="*60)
        console.print("📊 분석 결과 요약")
        console.print("="*60)
        
        # 요약 테이블 생성
        table = self.value_analyzer.create_analysis_summary_table(analysis_results)
        console.print(table)
        
        # 각 종목별 간단한 요약 표시
        for result in analysis_results:
            panel_content = f"""
💰 **현재가:** ${result.current_price:.2f}
🎯 **목표가:** ${result.target_price:.2f}
📈 **상승여력:** {result.upside_potential:.1f}%
💡 **신뢰도:** {result.confidence_score:.1f}%

**🔍 주요 강점:**
{chr(10).join(f"• {s}" for s in result.key_strengths[:3])}

**⚠️ 주요 위험:**
{chr(10).join(f"• {r}" for r in result.risks[:2])}
"""
            
            grade_color = self.value_analyzer._get_grade_color(result.investment_grade)
            console.print(
                Panel(
                    panel_content,
                    title=f"[bold]{result.symbol} - {result.company_name}[/bold]",
                    subtitle=f"[{grade_color}]등급: {result.investment_grade.value}[/{grade_color}]",
                    expand=False
                )
            )
    
    def show_menu(self):
        """메뉴를 표시합니다."""
        console.print("\n" + "="*50)
        console.print("🎯 메뉴를 선택하세요:")
        console.print("="*50)
        console.print("1. 새 분석 시작")
        console.print("2. 저장된 보고서 보기")
        console.print("3. 설정 변경")
        console.print("4. 종료")
        console.print("="*50)
        
        choice = Prompt.ask("선택", choices=["1", "2", "3", "4"], default="1")
        return choice
    
    def show_saved_reports(self):
        """저장된 보고서를 표시합니다."""
        reports = self.report_generator.list_reports()
        
        if not reports:
            console.print("[yellow]📝 저장된 보고서가 없습니다.[/yellow]")
            return
        
        console.print("\n📋 저장된 보고서 목록:")
        
        table = Table()
        table.add_column("번호", style="cyan")
        table.add_column("파일명", style="blue")
        table.add_column("크기", style="green")
        table.add_column("생성일", style="yellow")
        
        for i, report in enumerate(reports, 1):
            size_kb = report['size'] / 1024
            created_date = report['created_at'][:19].replace('T', ' ')
            
            table.add_row(
                str(i),
                report['filename'],
                f"{size_kb:.1f} KB",
                created_date
            )
        
        console.print(table)
        
        if Confirm.ask("보고서를 여시겠습니까?"):
            choice = Prompt.ask("번호를 입력하세요", default="1")
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(reports):
                    report_path = reports[idx]['filepath']
                    console.print(f"\n📄 보고서 위치: {report_path}")
                    
                    # 운영체제에 따라 파일 열기
                    import platform
                    system = platform.system()
                    
                    if system == "Windows":
                        os.startfile(report_path)
                    elif system == "Darwin":  # macOS
                        os.system(f"open '{report_path}'")
                    else:  # Linux
                        os.system(f"xdg-open '{report_path}'")
                    
                    console.print("[green]✅ 보고서가 열렸습니다.[/green]")
                else:
                    console.print("[red]❌ 잘못된 번호입니다.[/red]")
            except ValueError:
                console.print("[red]❌ 숫자를 입력해주세요.[/red]")
    
    def run(self):
        """메인 실행 루프"""
        # Gemini 클라이언트 초기화
        if not self.initialize_gemini_client():
            console.print("[red]❌ 프로그램을 종료합니다.[/red]")
            return
        
        while True:
            try:
                choice = self.show_menu()
                
                if choice == "1":
                    # 새 분석 시작
                    user_input = self.get_user_input()
                    
                    analysis_results = self.analyze_stocks(
                        symbols=user_input['symbols'],
                        analysis_depth=user_input['analysis_depth']
                    )
                    
                    if analysis_results:
                        self.display_results(analysis_results)
                        
                        report_paths = self.generate_reports(
                            analysis_results=analysis_results,
                            mode=user_input['mode'],
                            report_format=user_input['report_format']
                        )
                        
                        if report_paths:
                            console.print(f"\n[green]✅ 보고서가 생성되었습니다:[/green]")
                            for path in report_paths:
                                console.print(f"   📄 {path}")
                
                elif choice == "2":
                    # 저장된 보고서 보기
                    self.show_saved_reports()
                
                elif choice == "3":
                    # 설정 변경
                    console.print("[yellow]⚙️ 설정 기능은 개발 중입니다.[/yellow]")
                
                elif choice == "4":
                    # 종료
                    console.print("[blue]👋 프로그램을 종료합니다.[/blue]")
                    break
                
                if not Confirm.ask("\n계속하시겠습니까?", default=True):
                    break
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]⚠️ 사용자가 중단했습니다.[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]❌ 예상치 못한 오류: {str(e)}[/red]")
                self.logger.error(f"예상치 못한 오류: {str(e)}")
                
                if not Confirm.ask("계속하시겠습니까?"):
                    break

def main():
    """CLI 진입점"""
    parser = argparse.ArgumentParser(
        description="AI 기반 주식 가치투자 분석 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python main.py                    # 대화형 모드
  python main.py --symbol AAPL     # 단일 종목 분석
  python main.py --symbols AAPL,MSFT,GOOGL --format html
        """
    )
    
    parser.add_argument(
        '--symbol', 
        type=str, 
        help='분석할 단일 종목 코드 (예: AAPL)'
    )
    
    parser.add_argument(
        '--symbols', 
        type=str, 
        help='분석할 종목 코드들 (쉼표로 구분, 예: AAPL,MSFT,GOOGL)'
    )
    
    parser.add_argument(
        '--format', 
        type=str, 
        choices=['markdown', 'html', 'json'],
        default='markdown',
        help='보고서 형식 (기본값: markdown)'
    )
    
    parser.add_argument(
        '--depth', 
        type=str, 
        choices=['basic', 'detailed', 'comprehensive'],
        default='comprehensive',
        help='분석 깊이 (기본값: comprehensive)'
    )
    
    parser.add_argument(
        '--output', 
        type=str,
        help='출력 디렉터리 (기본값: reports)'
    )
    
    args = parser.parse_args()
    
    # 환경 변수 확인
    if not os.path.exists('.env'):
        console.print("[red]❌ .env 파일이 없습니다.[/red]")
        console.print("📝 .env.example 파일을 참조하여 .env 파일을 생성하세요.")
        return
    
    # 애플리케이션 초기화
    app = StockValueAnalyzer()
    
    # 출력 디렉터리 설정
    if args.output:
        app.report_generator.reports_dir = Path(args.output)
        app.report_generator.reports_dir.mkdir(exist_ok=True)
    
    # CLI 모드 vs 대화형 모드
    if args.symbol or args.symbols:
        # CLI 모드
        if not app.initialize_gemini_client():
            console.print("[red]❌ 프로그램을 종료합니다.[/red]")
            return
        
        # 종목 설정
        if args.symbol:
            symbols = [args.symbol.upper()]
            mode = "individual"
        else:
            symbols = [s.strip().upper() for s in args.symbols.split(',')]
            mode = "comparison" if len(symbols) > 1 else "individual"
        
        # 분석 실행
        try:
            analysis_results = app.analyze_stocks(symbols, args.depth)
            
            if analysis_results:
                app.display_results(analysis_results)
                
                report_paths = app.generate_reports(
                    analysis_results=analysis_results,
                    mode=mode,
                    report_format=args.format
                )
                
                if report_paths:
                    console.print(f"\n[green]✅ 보고서가 생성되었습니다:[/green]")
                    for path in report_paths:
                        console.print(f"   📄 {path}")
        
        except Exception as e:
            console.print(f"[red]❌ 분석 실패: {str(e)}[/red]")
            
    else:
        # 대화형 모드
        app.run()

if __name__ == "__main__":
    main()