import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class StockDataCollector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def get_stock_data(self, symbol: str, period: str = "2y") -> Dict:
        """
        주식 종목의 기본 정보와 재무 데이터를 수집합니다.
        
        Args:
            symbol: 주식 종목 코드 (예: "AAPL", "MSFT")
            period: 데이터 수집 기간 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        
        Returns:
            Dict: 주식 데이터 딕셔너리
        """
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                task = progress.add_task(f"[cyan]{symbol} 데이터 수집 중...", total=None)
                
                stock = yf.Ticker(symbol)
                
                # 기본 정보
                info = stock.info
                if not info:
                    raise ValueError(f"종목 {symbol}의 정보를 찾을 수 없습니다.")
                
                # 주가 데이터
                hist = stock.history(period=period)
                if hist.empty:
                    raise ValueError(f"종목 {symbol}의 주가 데이터를 찾을 수 없습니다.")
                
                # 재무제표 데이터
                financials = stock.financials
                balance_sheet = stock.balance_sheet
                cashflow = stock.cashflow
                
                # 배당 정보
                dividends = stock.dividends
                
                # 주요 재무 지표 계산
                financial_metrics = self._calculate_financial_metrics(
                    info, hist, financials, balance_sheet, cashflow, dividends
                )
                
                progress.update(task, description=f"[green]{symbol} 데이터 수집 완료")
                
                return {
                    'symbol': symbol,
                    'company_name': info.get('longName', symbol),
                    'sector': info.get('sector', 'Unknown'),
                    'industry': info.get('industry', 'Unknown'),
                    'market_cap': info.get('marketCap', 0),
                    'current_price': hist['Close'].iloc[-1] if not hist.empty else 0,
                    'basic_info': info,
                    'price_history': hist,
                    'financials': financials,
                    'balance_sheet': balance_sheet,
                    'cashflow': cashflow,
                    'dividends': dividends,
                    'financial_metrics': financial_metrics,
                    'data_collected_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"데이터 수집 중 오류 발생 ({symbol}): {str(e)}")
            raise Exception(f"'{symbol}' 종목 데이터 수집 실패: {str(e)}")
    
    def _calculate_financial_metrics(self, info: Dict, hist: pd.DataFrame, 
                                   financials: pd.DataFrame, balance_sheet: pd.DataFrame,
                                   cashflow: pd.DataFrame, dividends: pd.Series) -> Dict:
        """주요 재무 지표들을 계산합니다."""
        metrics = {}
        
        try:
            # 현재 주가
            current_price = hist['Close'].iloc[-1] if not hist.empty else 0
            metrics['current_price'] = float(current_price)
            
            # 52주 최고가/최저가
            metrics['52_week_high'] = float(hist['High'].max()) if not hist.empty else 0
            metrics['52_week_low'] = float(hist['Low'].min()) if not hist.empty else 0
            
            # 시가총액
            metrics['market_cap'] = info.get('marketCap', 0)
            
            # PER (Price-to-Earnings Ratio)
            metrics['pe_ratio'] = info.get('trailingPE', 0)
            metrics['forward_pe'] = info.get('forwardPE', 0)
            
            # PBR (Price-to-Book Ratio)
            metrics['pb_ratio'] = info.get('priceToBook', 0)
            
            # ROE (Return on Equity)
            metrics['roe'] = info.get('returnOnEquity', 0)
            
            # ROA (Return on Assets)
            metrics['roa'] = info.get('returnOnAssets', 0)
            
            # 부채비율
            metrics['debt_to_equity'] = info.get('debtToEquity', 0)
            
            # 배당수익률
            metrics['dividend_yield'] = info.get('dividendYield', 0)
            
            # 매출액 성장률 (최근 4분기 기준)
            if not financials.empty and len(financials.columns) >= 2:
                recent_revenue = financials.loc['Total Revenue'].iloc[0] if 'Total Revenue' in financials.index else 0
                prev_revenue = financials.loc['Total Revenue'].iloc[1] if 'Total Revenue' in financials.index else 0
                if prev_revenue != 0:
                    metrics['revenue_growth'] = ((recent_revenue - prev_revenue) / prev_revenue) * 100
                else:
                    metrics['revenue_growth'] = 0
            else:
                metrics['revenue_growth'] = 0
                
            # 순이익 성장률
            if not financials.empty and len(financials.columns) >= 2:
                recent_income = financials.loc['Net Income'].iloc[0] if 'Net Income' in financials.index else 0
                prev_income = financials.loc['Net Income'].iloc[1] if 'Net Income' in financials.index else 0
                if prev_income != 0:
                    metrics['income_growth'] = ((recent_income - prev_income) / prev_income) * 100
                else:
                    metrics['income_growth'] = 0
            else:
                metrics['income_growth'] = 0
            
            # 현금 및 현금성 자산
            metrics['cash_and_equivalents'] = info.get('totalCash', 0)
            
            # 총 부채
            metrics['total_debt'] = info.get('totalDebt', 0)
            
            # 자유현금흐름
            metrics['free_cash_flow'] = info.get('freeCashflow', 0)
            
            # 베타값 (시장 대비 변동성)
            metrics['beta'] = info.get('beta', 0)
            
            # 주식 수
            metrics['shares_outstanding'] = info.get('sharesOutstanding', 0)
            
            # 주가 변동성 계산 (30일 기준)
            if not hist.empty and len(hist) >= 30:
                returns = hist['Close'].pct_change().dropna()
                metrics['volatility_30d'] = float(returns.tail(30).std() * np.sqrt(252))  # 연환산
            else:
                metrics['volatility_30d'] = 0
                
            # 평균 거래량 (30일)
            if not hist.empty and len(hist) >= 30:
                metrics['avg_volume_30d'] = float(hist['Volume'].tail(30).mean())
            else:
                metrics['avg_volume_30d'] = 0
                
        except Exception as e:
            self.logger.warning(f"재무지표 계산 중 일부 오류 발생: {str(e)}")
        
        return metrics
    
    def get_multiple_stocks_data(self, symbols: List[str], period: str = "2y") -> Dict[str, Dict]:
        """
        여러 종목의 데이터를 한 번에 수집합니다.
        
        Args:
            symbols: 주식 종목 코드 리스트
            period: 데이터 수집 기간
        
        Returns:
            Dict: 종목별 데이터 딕셔너리
        """
        results = {}
        failed_symbols = []
        
        console.print(f"[bold blue]총 {len(symbols)}개 종목 데이터 수집 시작[/bold blue]")
        
        for i, symbol in enumerate(symbols, 1):
            try:
                console.print(f"[cyan]({i}/{len(symbols)}) {symbol} 처리 중...[/cyan]")
                results[symbol] = self.get_stock_data(symbol, period)
                console.print(f"[green]✓ {symbol} 완료[/green]")
            except Exception as e:
                failed_symbols.append(symbol)
                console.print(f"[red]✗ {symbol} 실패: {str(e)}[/red]")
        
        if failed_symbols:
            console.print(f"[yellow]실패한 종목: {', '.join(failed_symbols)}[/yellow]")
        
        console.print(f"[bold green]데이터 수집 완료: {len(results)}/{len(symbols)} 성공[/bold green]")
        
        return results
    
    def validate_symbol(self, symbol: str) -> bool:
        """종목 코드가 유효한지 확인합니다."""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            return bool(info and 'symbol' in info)
        except:
            return False
    
    def search_similar_symbols(self, query: str) -> List[str]:
        """비슷한 종목명을 검색합니다 (간단한 구현)."""
        common_symbols = {
            'apple': 'AAPL',
            'microsoft': 'MSFT',
            'google': 'GOOGL',
            'amazon': 'AMZN',
            'tesla': 'TSLA',
            'meta': 'META',
            'netflix': 'NFLX',
            'nvidia': 'NVDA',
            'samsung': '005930.KS',
            'sk하이닉스': '000660.KS',
            'lg화학': '051910.KS',
            'kakao': '035720.KS',
            'naver': '035420.KS'
        }
        
        query_lower = query.lower()
        suggestions = []
        
        for name, symbol in common_symbols.items():
            if query_lower in name or name in query_lower:
                suggestions.append(symbol)
        
        return suggestions[:5]  # 최대 5개 제안