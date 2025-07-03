import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
from google import genai
from google.genai import types
# Rich imports removed for server compatibility

# Console removed for server compatibility

class GeminiClient:
    def __init__(self, api_key: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        
        if not self.api_key:
            raise ValueError("Google API 키가 설정되지 않았습니다. .env 파일에서 GOOGLE_API_KEY를 설정하세요.")
        
        # Gemini 클라이언트 초기화
        self.client = genai.Client(api_key=self.api_key)
        
        # 기본 설정
        self.model_name = "gemini-2.5-flash"
        self.max_tokens = 8192
        self.temperature = 0.7
        
        console.print(f"[green]Gemini API 클라이언트 초기화 완료 (모델: {self.model_name})[/green]")
    
    def generate_analysis(self, prompt: str, stock_data: Dict, 
                         thinking_enabled: bool = True, 
                         thinking_budget: int = 2048) -> str:
        """
        주식 분석 보고서를 생성합니다.
        
        Args:
            prompt: 분석 요청 프롬프트
            stock_data: 주식 데이터 딕셔너리
            thinking_enabled: 사고 과정 활성화 여부
            thinking_budget: 사고 과정 토큰 예산
        
        Returns:
            str: 생성된 분석 보고서
        """
        try:
            print("🤖 AI 분석 요청 중...")
            
            # 주식 데이터를 텍스트로 변환
                formatted_data = self._format_stock_data(stock_data)
                
                # 최종 프롬프트 구성
                full_prompt = f"""
{prompt}

**분석 대상 주식 데이터:**
{formatted_data}

**분석 요청사항:**
위 데이터를 바탕으로 해당 주식의 가치투자 관점에서의 종합적인 분석을 수행해주세요.
"""
                
                # 설정 구성
                config = types.GenerateContentConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                )
                
                # 사고 과정 활성화 시 설정 추가
                if thinking_enabled:
                    config.thinking_config = types.ThinkingConfig(
                        thinking_budget=thinking_budget
                    )
                
                # API 호출
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=full_prompt,
                    config=config
                )
                
                progress.update(task, description="[green]AI 분석 완료")
                
                if not response.text:
                    raise ValueError("AI로부터 응답을 받지 못했습니다.")
                
                return response.text
                
        except Exception as e:
            self.logger.error(f"AI 분석 중 오류 발생: {str(e)}")
            raise Exception(f"AI 분석 실패: {str(e)}")
    
    def _format_stock_data(self, stock_data: Dict) -> str:
        """주식 데이터를 AI가 이해하기 쉬운 텍스트 형태로 변환합니다."""
        try:
            symbol = stock_data.get('symbol', 'N/A')
            company_name = stock_data.get('company_name', 'N/A')
            sector = stock_data.get('sector', 'N/A')
            industry = stock_data.get('industry', 'N/A')
            current_price = stock_data.get('current_price', 0)
            market_cap = stock_data.get('market_cap', 0)
            metrics = stock_data.get('financial_metrics', {})
            
            # 시가총액을 읽기 쉬운 형태로 변환
            market_cap_str = self._format_currency(market_cap)
            
            formatted = f"""
## 기업 기본 정보
- 종목 코드: {symbol}
- 기업명: {company_name}
- 섹터: {sector}
- 산업: {industry}
- 현재 주가: ${current_price:.2f}
- 시가총액: {market_cap_str}

## 주요 재무 지표
- PER (주가수익비율): {metrics.get('pe_ratio', 0):.2f}
- PBR (주가순자산비율): {metrics.get('pb_ratio', 0):.2f}
- ROE (자기자본수익률): {metrics.get('roe', 0):.2%}
- ROA (총자산수익률): {metrics.get('roa', 0):.2%}
- 부채비율: {metrics.get('debt_to_equity', 0):.2f}
- 배당수익률: {metrics.get('dividend_yield', 0):.2%}
- 매출액 성장률: {metrics.get('revenue_growth', 0):.2f}%
- 순이익 성장률: {metrics.get('income_growth', 0):.2f}%

## 주가 및 위험 지표
- 52주 최고가: ${metrics.get('52_week_high', 0):.2f}
- 52주 최저가: ${metrics.get('52_week_low', 0):.2f}
- 베타값: {metrics.get('beta', 0):.2f}
- 30일 변동성: {metrics.get('volatility_30d', 0):.2%}
- 평균 거래량 (30일): {metrics.get('avg_volume_30d', 0):,.0f}

## 재무 건전성
- 현금 및 현금성 자산: {self._format_currency(metrics.get('cash_and_equivalents', 0))}
- 총 부채: {self._format_currency(metrics.get('total_debt', 0))}
- 자유현금흐름: {self._format_currency(metrics.get('free_cash_flow', 0))}
- 발행 주식 수: {metrics.get('shares_outstanding', 0):,.0f}
"""
            
            return formatted
            
        except Exception as e:
            self.logger.error(f"주식 데이터 포맷팅 중 오류: {str(e)}")
            return f"주식 데이터 포맷팅 오류: {str(e)}"
    
    def _format_currency(self, amount: float) -> str:
        """숫자를 읽기 쉬운 통화 형태로 변환합니다."""
        if amount == 0:
            return "$0"
        
        if amount >= 1e12:
            return f"${amount/1e12:.2f}T"
        elif amount >= 1e9:
            return f"${amount/1e9:.2f}B"
        elif amount >= 1e6:
            return f"${amount/1e6:.2f}M"
        elif amount >= 1e3:
            return f"${amount/1e3:.2f}K"
        else:
            return f"${amount:.2f}"
    
    def generate_comparison_analysis(self, stocks_data: Dict[str, Dict], 
                                   custom_prompt: Optional[str] = None) -> str:
        """
        여러 주식을 비교 분석합니다.
        
        Args:
            stocks_data: 종목별 데이터 딕셔너리
            custom_prompt: 사용자 지정 프롬프트
        
        Returns:
            str: 비교 분석 보고서
        """
        try:
            symbols = list(stocks_data.keys())
            
            if len(symbols) < 2:
                raise ValueError("비교 분석을 위해서는 최소 2개의 종목이 필요합니다.")
            
            # 기본 비교 분석 프롬프트
            default_prompt = f"""
다음 {len(symbols)}개 종목({', '.join(symbols)})에 대한 가치투자 관점에서의 비교 분석을 수행해주세요.

**분석 요청사항:**
1. 각 종목의 가치투자 매력도 평가
2. 재무 건전성 비교
3. 성장성 및 수익성 분석
4. 위험 요인 분석
5. 포트폴리오 구성 시 고려사항
6. 최종 투자 우선순위 및 이유

각 종목의 강점과 약점을 명확히 구분하여 제시하고, 
가치투자자가 중요하게 고려해야 할 요소들을 중심으로 분석해주세요.
"""
            
            prompt = custom_prompt or default_prompt
            
            # 모든 종목 데이터를 하나의 문자열로 결합
            all_data = ""
            for symbol, data in stocks_data.items():
                all_data += f"\n{'='*50}\n"
                all_data += f"종목: {symbol}\n"
                all_data += f"{'='*50}\n"
                all_data += self._format_stock_data(data)
                all_data += "\n"
            
            full_prompt = f"""
{prompt}

**분석 대상 종목들의 데이터:**
{all_data}
"""
            
            # 비교 분석은 더 많은 토큰이 필요할 수 있으므로 설정 조정
            config = types.GenerateContentConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens * 2,  # 더 긴 응답 허용
                thinking_config=types.ThinkingConfig(
                    thinking_budget=4096  # 더 많은 사고 과정 토큰
                )
            )
            
            print("🔄 비교 분석 중...")
            
            response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=full_prompt,
                    config=config
                )
                
                progress.update(task, description="[green]비교 분석 완료")
                
                if not response.text:
                    raise ValueError("AI로부터 응답을 받지 못했습니다.")
                
                return response.text
                
        except Exception as e:
            self.logger.error(f"비교 분석 중 오류 발생: {str(e)}")
            raise Exception(f"비교 분석 실패: {str(e)}")
    
    def test_connection(self) -> bool:
        """API 연결 상태를 테스트합니다."""
        try:
            console.print("[cyan]API 연결 테스트 중...[/cyan]")
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents="Hello, this is a connection test. Please respond with 'Connection successful.'",
                config=types.GenerateContentConfig(
                    max_output_tokens=50,
                    temperature=0.1
                )
            )
            
            if response.text and "successful" in response.text.lower():
                console.print("[green]✓ API 연결 테스트 성공[/green]")
                return True
            else:
                console.print("[red]✗ API 연결 테스트 실패[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]✗ API 연결 테스트 오류: {str(e)}[/red]")
            return False
    
    def set_model_parameters(self, model_name: Optional[str] = None, 
                           max_tokens: Optional[int] = None, 
                           temperature: Optional[float] = None):
        """모델 매개변수를 설정합니다."""
        if model_name:
            self.model_name = model_name
        if max_tokens:
            self.max_tokens = max_tokens
        if temperature is not None:
            self.temperature = temperature
            
        console.print(f"[blue]모델 설정 업데이트: {self.model_name}, "
                     f"max_tokens={self.max_tokens}, temperature={self.temperature}[/blue]")