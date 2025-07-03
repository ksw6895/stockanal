import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from rich.console import Console
from rich.table import Table

console = Console()

class InvestmentGrade(Enum):
    STRONG_BUY = "Strong Buy"
    BUY = "Buy"
    HOLD = "Hold"
    SELL = "Sell"
    STRONG_SELL = "Strong Sell"

@dataclass
class ValueMetrics:
    """가치투자 핵심 지표들"""
    pe_ratio: float
    pb_ratio: float
    peg_ratio: float
    dividend_yield: float
    roe: float
    roa: float
    debt_to_equity: float
    current_ratio: float
    revenue_growth: float
    income_growth: float
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class AnalysisResult:
    """분석 결과 구조"""
    symbol: str
    company_name: str
    analysis_date: str
    investment_grade: InvestmentGrade
    confidence_score: float
    target_price: float
    current_price: float
    upside_potential: float
    key_strengths: List[str]
    key_weaknesses: List[str]
    risks: List[str]
    value_metrics: ValueMetrics
    detailed_analysis: str
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        result['investment_grade'] = self.investment_grade.value
        return result

class ValueAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 가치투자 평가 기준
        self.evaluation_criteria = {
            'pe_ratio': {'excellent': 15, 'good': 20, 'acceptable': 25},
            'pb_ratio': {'excellent': 1.5, 'good': 2.0, 'acceptable': 3.0},
            'roe': {'excellent': 0.15, 'good': 0.12, 'acceptable': 0.10},
            'debt_to_equity': {'excellent': 0.3, 'good': 0.5, 'acceptable': 1.0},
            'dividend_yield': {'excellent': 0.03, 'good': 0.02, 'acceptable': 0.01},
            'revenue_growth': {'excellent': 10, 'good': 5, 'acceptable': 0},
            'income_growth': {'excellent': 15, 'good': 10, 'acceptable': 5},
        }
        
        # 섹터별 가중치
        self.sector_weights = {
            'Technology': {'growth': 0.4, 'profitability': 0.3, 'stability': 0.2, 'valuation': 0.1},
            'Healthcare': {'growth': 0.3, 'profitability': 0.3, 'stability': 0.3, 'valuation': 0.1},
            'Financials': {'stability': 0.4, 'valuation': 0.3, 'profitability': 0.2, 'growth': 0.1},
            'Consumer Staples': {'stability': 0.4, 'profitability': 0.3, 'valuation': 0.2, 'growth': 0.1},
            'Utilities': {'stability': 0.5, 'valuation': 0.3, 'profitability': 0.2, 'growth': 0.0},
            'default': {'growth': 0.25, 'profitability': 0.25, 'stability': 0.25, 'valuation': 0.25}
        }
    
    def analyze_stock(self, stock_data: Dict, gemini_client=None) -> AnalysisResult:
        """
        주식 데이터를 분석하여 가치투자 관점에서 평가합니다.
        
        Args:
            stock_data: 주식 데이터 딕셔너리
            gemini_client: Gemini API 클라이언트 (투자 등급 결정용)
        
        Returns:
            AnalysisResult: 분석 결과
        """
        try:
            console.print(f"[cyan]{stock_data.get('symbol', 'N/A')} 가치투자 분석 시작[/cyan]")
            
            # 기본 정보 추출
            symbol = stock_data.get('symbol', 'N/A')
            company_name = stock_data.get('company_name', 'N/A')
            sector = stock_data.get('sector', 'Unknown')
            current_price = stock_data.get('current_price', 0)
            metrics = stock_data.get('financial_metrics', {})
            
            # 가치투자 핵심 지표 계산
            value_metrics = self._calculate_value_metrics(metrics)
            
            # 목표 가격 계산
            target_price = self._calculate_target_price(stock_data, value_metrics)
            
            # 상승 여력 계산
            upside_potential = ((target_price - current_price) / current_price) * 100 if current_price > 0 else 0
            
            # 강점/약점 분석
            strengths, weaknesses = self._analyze_strengths_weaknesses(value_metrics)
            
            # 위험 요인 분석
            risks = self._identify_risks(stock_data, value_metrics)
            
            # AI 기반 투자 등급 결정
            if gemini_client:
                investment_grade, confidence_score = self._ai_determine_investment_grade(
                    gemini_client, stock_data, value_metrics, strengths, weaknesses, risks, upside_potential
                )
            else:
                # Fallback: 기본 등급 시스템
                investment_grade, confidence_score = self._fallback_investment_grade(value_metrics, upside_potential)
            
            # 상세 분석 생성
            detailed_analysis = self._generate_detailed_analysis(
                stock_data, value_metrics, investment_grade
            )
            
            result = AnalysisResult(
                symbol=symbol,
                company_name=company_name,
                analysis_date=datetime.now().isoformat(),
                investment_grade=investment_grade,
                confidence_score=confidence_score,
                target_price=target_price,
                current_price=current_price,
                upside_potential=upside_potential,
                key_strengths=strengths,
                key_weaknesses=weaknesses,
                risks=risks,
                value_metrics=value_metrics,
                detailed_analysis=detailed_analysis
            )
            
            console.print(f"[green]✓ {symbol} 분석 완료 (등급: {investment_grade.value})[/green]")
            
            return result
            
        except Exception as e:
            self.logger.error(f"주식 분석 중 오류 발생: {str(e)}")
            raise Exception(f"주식 분석 실패: {str(e)}")
    
    def _calculate_value_metrics(self, metrics: Dict) -> ValueMetrics:
        """가치투자 핵심 지표들을 계산합니다."""
        pe_ratio = metrics.get('pe_ratio', 0)
        pb_ratio = metrics.get('pb_ratio', 0)
        
        # PEG 비율 계산 (PE / 수익 성장률)
        income_growth = metrics.get('income_growth', 0)
        peg_ratio = pe_ratio / income_growth if income_growth > 0 else 0
        
        # Current Ratio 계산 (간단한 추정)
        current_ratio = 1.5  # 기본값 (실제로는 유동자산/유동부채)
        
        return ValueMetrics(
            pe_ratio=pe_ratio,
            pb_ratio=pb_ratio,
            peg_ratio=peg_ratio,
            dividend_yield=metrics.get('dividend_yield', 0),
            roe=metrics.get('roe', 0),
            roa=metrics.get('roa', 0),
            debt_to_equity=metrics.get('debt_to_equity', 0),
            current_ratio=current_ratio,
            revenue_growth=metrics.get('revenue_growth', 0),
            income_growth=income_growth
        )
    
    
    def _calculate_target_price(self, stock_data: Dict, value_metrics: ValueMetrics) -> float:
        """목표 가격을 계산합니다."""
        try:
            current_price = stock_data.get('current_price', 0)
            metrics = stock_data.get('financial_metrics', {})
            
            # 여러 밸류에이션 방법 사용
            target_prices = []
            
            # 1. PER 기반 목표가 (산업 평균 PER 15 적용)
            if value_metrics.pe_ratio > 0:
                fair_pe = 15
                eps = current_price / value_metrics.pe_ratio if value_metrics.pe_ratio > 0 else 0
                if eps > 0:
                    target_prices.append(eps * fair_pe)
            
            # 2. PBR 기반 목표가 (적정 PBR 2.0 적용)
            if value_metrics.pb_ratio > 0:
                fair_pbr = 2.0
                book_value_per_share = current_price / value_metrics.pb_ratio if value_metrics.pb_ratio > 0 else 0
                if book_value_per_share > 0:
                    target_prices.append(book_value_per_share * fair_pbr)
            
            # 3. 배당 할인 모델 (간단한 버전)
            if value_metrics.dividend_yield > 0:
                dividend_per_share = current_price * value_metrics.dividend_yield
                required_return = 0.10  # 10% 요구 수익률
                growth_rate = max(0, min(0.06, value_metrics.income_growth / 100))  # 최대 6% 성장률
                if required_return > growth_rate:
                    target_prices.append(dividend_per_share / (required_return - growth_rate))
            
            # 목표가 계산
            if target_prices:
                # 중간값 사용 (극값 제거)
                target_prices.sort()
                if len(target_prices) >= 3:
                    target_price = target_prices[len(target_prices)//2]
                else:
                    target_price = sum(target_prices) / len(target_prices)
                
                # 현재가의 50% ~ 200% 범위로 제한
                target_price = max(current_price * 0.5, min(current_price * 2.0, target_price))
            else:
                # 기본값: 현재가
                target_price = current_price
            
            return target_price
            
        except Exception as e:
            self.logger.warning(f"목표가 계산 중 오류: {str(e)}")
            return stock_data.get('current_price', 0)
    
    def _ai_determine_investment_grade(self, gemini_client, stock_data: Dict, 
                                      value_metrics: ValueMetrics, strengths: List[str], 
                                      weaknesses: List[str], risks: List[str], 
                                      upside_potential: float) -> Tuple[InvestmentGrade, float]:
        """AI를 사용하여 투자 등급을 결정합니다."""
        try:
            console.print("[cyan]AI 기반 투자 등급 평가 중...[/cyan]")
            
            prompt = f"""
당신은 워렌 버핏과 벤저민 그레이엄의 가치투자 철학을 따르는 전문 투자 분석가입니다.

다음 주식에 대해 투자 등급을 결정해주세요:

**기업 정보:**
- 종목: {stock_data.get('symbol', 'N/A')} ({stock_data.get('company_name', 'N/A')})
- 섹터: {stock_data.get('sector', 'Unknown')}
- 현재가: ${stock_data.get('current_price', 0):.2f}

**핵심 재무지표:**
- PER: {value_metrics.pe_ratio:.2f}
- PBR: {value_metrics.pb_ratio:.2f}
- ROE: {value_metrics.roe:.2%}
- ROA: {value_metrics.roa:.2%}
- 부채비율: {value_metrics.debt_to_equity:.2f}
- 배당수익률: {value_metrics.dividend_yield:.2%}
- 매출 성장률: {value_metrics.revenue_growth:.1f}%
- 순이익 성장률: {value_metrics.income_growth:.1f}%
- 상승여력: {upside_potential:.1f}%

**주요 강점:**
{chr(10).join(f"- {s}" for s in strengths)}

**주요 약점:**
{chr(10).join(f"- {w}" for w in weaknesses)}

**위험 요인:**
{chr(10).join(f"- {r}" for r in risks)}

**평가 기준:**
1. Strong Buy: 매우 매력적인 저평가, 강력한 펀더멘털, 높은 상승여력
2. Buy: 매력적인 투자 기회, 양호한 펀더멘털
3. Hold: 적정 가격, 보유 유지 권장
4. Sell: 고평가되었거나 펀더멘털 악화
5. Strong Sell: 심각한 문제, 즉시 매도 권장

**요청사항:**
다음 형식으로만 답변해주세요:

등급: [Strong Buy/Buy/Hold/Sell/Strong Sell]
신뢰도: [0-100 숫자]
핵심근거: [한 줄 요약]

예시:
등급: Buy
신뢰도: 85
핵심근거: 낮은 PER과 높은 ROE로 매력적인 저평가 상태
"""
            
            from google.genai import types
            
            response = gemini_client.client.models.generate_content(
                model=gemini_client.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,  # 일관성을 위해 낮은 온도
                    max_output_tokens=200
                )
            )
            
            # AI 응답 파싱
            ai_response = response.text.strip() if response.text else ""
            console.print(f"[blue]AI 등급 평가: {ai_response}[/blue]")
            
            if not ai_response:
                console.print("[yellow]⚠️ AI 응답이 비어있음, fallback 시스템 사용[/yellow]")
                return self._fallback_investment_grade(value_metrics, upside_potential)
            
            # 응답에서 등급과 신뢰도 추출
            grade_mapping = {
                'Strong Buy': InvestmentGrade.STRONG_BUY,
                'Buy': InvestmentGrade.BUY,
                'Hold': InvestmentGrade.HOLD,
                'Sell': InvestmentGrade.SELL,
                'Strong Sell': InvestmentGrade.STRONG_SELL
            }
            
            investment_grade = InvestmentGrade.HOLD  # 기본값
            confidence_score = 50.0  # 기본값
            
            for line in ai_response.split('\n'):
                if '등급:' in line:
                    grade_text = line.split('등급:')[1].strip()
                    investment_grade = grade_mapping.get(grade_text, InvestmentGrade.HOLD)
                elif '신뢰도:' in line:
                    try:
                        confidence_score = float(line.split('신뢰도:')[1].strip())
                    except:
                        confidence_score = 50.0
            
            return investment_grade, confidence_score
            
        except Exception as e:
            self.logger.error(f"AI 투자 등급 결정 중 오류: {str(e)}")
            # Fallback으로 기본 시스템 사용
            return self._fallback_investment_grade(value_metrics, upside_potential)
    
    def _fallback_investment_grade(self, value_metrics: ValueMetrics, upside_potential: float) -> Tuple[InvestmentGrade, float]:
        """AI 실패 시 사용할 기본 투자 등급 시스템"""
        # 간단한 규칙 기반 시스템
        score = 50  # 기본 점수
        
        # PER 기반 점수
        if 0 < value_metrics.pe_ratio <= 10:
            score += 20
        elif 10 < value_metrics.pe_ratio <= 15:
            score += 10
        elif value_metrics.pe_ratio > 25:
            score -= 10
        
        # ROE 기반 점수
        if value_metrics.roe >= 0.15:
            score += 15
        elif value_metrics.roe >= 0.10:
            score += 10
        elif value_metrics.roe < 0.05:
            score -= 15
        
        # 성장률 기반 점수
        if value_metrics.revenue_growth > 10:
            score += 10
        elif value_metrics.revenue_growth < -10:
            score -= 15
        
        # 상승여력 기반 점수
        if upside_potential > 30:
            score += 15
        elif upside_potential > 15:
            score += 10
        elif upside_potential < 0:
            score -= 20
        
        # 등급 결정
        if score >= 80:
            grade = InvestmentGrade.STRONG_BUY
        elif score >= 70:
            grade = InvestmentGrade.BUY
        elif score >= 50:
            grade = InvestmentGrade.HOLD
        elif score >= 30:
            grade = InvestmentGrade.SELL
        else:
            grade = InvestmentGrade.STRONG_SELL
        
        confidence_score = min(max(score, 0), 100)
        
        return grade, confidence_score
    
    def _analyze_strengths_weaknesses(self, value_metrics: ValueMetrics) -> Tuple[List[str], List[str]]:
        """강점과 약점을 분석합니다."""
        strengths = []
        weaknesses = []
        
        # 성장성 평가
        if value_metrics.revenue_growth > 10:
            strengths.append(f"우수한 매출 성장률 ({value_metrics.revenue_growth:.1f}%)")
        elif value_metrics.revenue_growth < -10:
            weaknesses.append(f"저조한 성장성 (매출 {value_metrics.revenue_growth:.1f}%, 순이익 {value_metrics.income_growth:.1f}% 성장)")
        
        # 수익성 평가
        if value_metrics.roe >= 0.15 and value_metrics.roa >= 0.08:
            strengths.append(f"높은 수익성 (ROE {value_metrics.roe:.1%}, ROA {value_metrics.roa:.1%})")
        elif value_metrics.roe < 0.05:
            weaknesses.append(f"낮은 수익성 (ROE {value_metrics.roe:.1%}, ROA {value_metrics.roa:.1%})")
        
        # 재무 안정성 평가 (부채비율이 매우 낮으면 강점)
        if value_metrics.debt_to_equity < 0.3:
            strengths.append(f"우수한 재무 건전성 (부채비율 {value_metrics.debt_to_equity:.1f})")
        elif value_metrics.debt_to_equity > 1.0:
            weaknesses.append(f"높은 부채비율 ({value_metrics.debt_to_equity:.1f})")
        
        # 밸류에이션 평가
        if 0 < value_metrics.pe_ratio <= 15 and 0 < value_metrics.pb_ratio <= 2:
            strengths.append(f"매력적인 밸류에이션 (PER {value_metrics.pe_ratio:.1f}, PBR {value_metrics.pb_ratio:.1f})")
        elif value_metrics.pe_ratio > 30 or value_metrics.pb_ratio > 5:
            weaknesses.append(f"높은 밸류에이션 (PER {value_metrics.pe_ratio:.1f}, PBR {value_metrics.pb_ratio:.1f})")
        
        # 배당 관련
        if value_metrics.dividend_yield >= 0.03:
            strengths.append(f"매력적인 배당수익률 ({value_metrics.dividend_yield:.1%})")
        elif value_metrics.dividend_yield == 0:
            weaknesses.append("배당 미지급")
        
        return strengths, weaknesses
    
    def _identify_risks(self, stock_data: Dict, value_metrics: ValueMetrics) -> List[str]:
        """위험 요인을 식별합니다."""
        risks = []
        
        # 부채 위험
        if value_metrics.debt_to_equity > 1.0:
            risks.append("높은 부채 비율로 인한 재무 위험")
        
        # 밸류에이션 위험
        if value_metrics.pe_ratio > 30:
            risks.append("높은 PER로 인한 밸류에이션 위험")
        
        # 성장률 위험
        if value_metrics.revenue_growth < 0:
            risks.append("매출 감소로 인한 성장성 위험")
        
        if value_metrics.income_growth < 0:
            risks.append("순이익 감소로 인한 수익성 위험")
        
        # 섹터별 위험
        sector = stock_data.get('sector', '')
        if sector == 'Technology':
            risks.append("기술 변화 및 경쟁 심화 위험")
        elif sector == 'Healthcare':
            risks.append("규제 변화 및 임상 시험 실패 위험")
        elif sector == 'Financials':
            risks.append("금리 변동 및 신용 위험")
        
        # 시장 위험
        metrics = stock_data.get('financial_metrics', {})
        beta = metrics.get('beta', 1.0)
        if beta > 1.5:
            risks.append("높은 베타로 인한 시장 변동성 위험")
        
        return risks
    
    def _generate_detailed_analysis(self, stock_data: Dict, value_metrics: ValueMetrics, 
                                  investment_grade: InvestmentGrade) -> str:
        """상세 분석 텍스트를 생성합니다."""
        symbol = stock_data.get('symbol', 'N/A')
        company_name = stock_data.get('company_name', 'N/A')
        
        analysis = f"""
## {company_name} ({symbol}) 가치투자 분석

### 투자 등급: {investment_grade.value}

### 주요 재무 지표
- PER: {value_metrics.pe_ratio:.1f}
- PBR: {value_metrics.pb_ratio:.1f}
- PEG: {value_metrics.peg_ratio:.1f}
- ROE: {value_metrics.roe:.1%}
- 부채비율: {value_metrics.debt_to_equity:.1f}
- 배당수익률: {value_metrics.dividend_yield:.1%}

### 분석 결론
{investment_grade.value} 등급은 AI가 주요 재무지표와 시장 상황을 종합적으로 고려한 결과입니다.
가치투자 관점에서 이 종목의 장단점을 면밀히 검토하시기 바랍니다.
"""
        
        return analysis.strip()
    
    def create_analysis_summary_table(self, results: List[AnalysisResult]) -> Table:
        """분석 결과 요약 테이블을 생성합니다."""
        table = Table(title="가치투자 분석 결과 요약")
        
        table.add_column("종목", style="cyan")
        table.add_column("등급", style="bold")
        table.add_column("현재가", style="green")
        table.add_column("목표가", style="blue")
        table.add_column("상승여력", style="magenta")
        table.add_column("PER", style="yellow")
        table.add_column("PBR", style="yellow")
        table.add_column("ROE", style="yellow")
        
        for result in results:
            grade_color = self._get_grade_color(result.investment_grade)
            upside_color = "green" if result.upside_potential > 0 else "red"
            
            table.add_row(
                result.symbol,
                f"[{grade_color}]{result.investment_grade.value}[/{grade_color}]",
                f"${result.current_price:.2f}",
                f"${result.target_price:.2f}",
                f"[{upside_color}]{result.upside_potential:.1f}%[/{upside_color}]",
                f"{result.value_metrics.pe_ratio:.1f}",
                f"{result.value_metrics.pb_ratio:.1f}",
                f"{result.value_metrics.roe:.1%}"
            )
        
        return table
    
    def _get_grade_color(self, grade: InvestmentGrade) -> str:
        """투자 등급에 따른 색상을 반환합니다."""
        color_map = {
            InvestmentGrade.STRONG_BUY: "bright_green",
            InvestmentGrade.BUY: "green",
            InvestmentGrade.HOLD: "yellow",
            InvestmentGrade.SELL: "red",
            InvestmentGrade.STRONG_SELL: "bright_red"
        }
        return color_map.get(grade, "white")

# numpy 없이 표준편차 계산
def np_std(values):
    if len(values) <= 1:
        return 0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return variance ** 0.5

# numpy 대신 사용
import math
np = type('np', (), {'std': np_std})()