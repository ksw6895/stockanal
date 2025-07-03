from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import json
import asyncio
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv

# 로컬 모듈 import
from modules.stock_data_collector import StockDataCollector
from modules.gemini_client import GeminiClient
from modules.value_analyzer import ValueAnalyzer
from modules.report_generator import ReportGenerator

# 환경 변수 로드
load_dotenv()

app = FastAPI(title="AI 주식 가치투자 분석 시스템", version="1.0.0")

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 전역 변수로 컴포넌트 초기화
stock_collector = None
gemini_client = None
value_analyzer = None
report_generator = None

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 초기화"""
    global stock_collector, gemini_client, value_analyzer, report_generator
    
    print("🚀 애플리케이션 초기화 시작...")
    
    try:
        print("📊 주식 데이터 수집기 초기화...")
        stock_collector = StockDataCollector()
        print("✅ 주식 데이터 수집기 초기화 완료")
        
        print("📈 가치 분석기 초기화...")
        value_analyzer = ValueAnalyzer()
        print("✅ 가치 분석기 초기화 완료")
        
        print("📝 보고서 생성기 초기화...")
        report_generator = ReportGenerator()
        print("✅ 보고서 생성기 초기화 완료")
        
        # Gemini API 클라이언트 초기화
        print("🤖 Gemini API 클라이언트 초기화...")
        api_key = os.getenv('GOOGLE_API_KEY')
        if api_key:
            print(f"🔑 API 키 발견 (길이: {len(api_key)})")
            gemini_client = GeminiClient(api_key)
            print("✅ Gemini 클라이언트 초기화 완료")
            
            # 연결 테스트
            print("🔍 Gemini API 연결 테스트...")
            if gemini_client.test_connection():
                print("✅ Gemini API 연결 성공")
            else:
                print("⚠️ Gemini API 연결 실패")
        else:
            print("⚠️ Google API 키가 설정되지 않았습니다.")
            print("📋 환경변수 확인:")
            for key in os.environ:
                if 'GOOGLE' in key or 'API' in key:
                    print(f"  - {key}: {'*' * len(os.environ[key]) if os.environ[key] else 'None'}")
            
        print("🎉 애플리케이션 초기화 완료!")
            
    except Exception as e:
        print(f"❌ 초기화 중 오류: {str(e)}")
        import traceback
        print(f"📋 상세 오류:")
        traceback.print_exc()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """메인 페이지"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/analyze", response_class=HTMLResponse)
async def analyze_page(request: Request):
    """분석 페이지"""
    return templates.TemplateResponse("analyze.html", {"request": request})

@app.post("/api/analyze")
async def analyze_stock(
    symbol: str = Form(...),
    depth: str = Form(default="comprehensive")
):
    """주식 분석 API"""
    try:
        # 상세한 초기화 상태 확인
        print(f"🔍 API 호출 - Symbol: {symbol}")
        print(f"🔍 stock_collector: {stock_collector is not None}")
        print(f"🔍 gemini_client: {gemini_client is not None}")
        print(f"🔍 value_analyzer: {value_analyzer is not None}")
        
        if not all([stock_collector, gemini_client, value_analyzer]):
            error_details = {
                "stock_collector": stock_collector is not None,
                "gemini_client": gemini_client is not None,
                "value_analyzer": value_analyzer is not None
            }
            print(f"❌ 초기화 실패 상세: {error_details}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "시스템이 초기화되지 않았습니다.",
                    "details": error_details
                }
            )
        
        # 1. 주식 데이터 수집
        symbol = symbol.upper().strip()
        print(f"🔍 Validating symbol: {symbol}")
        
        validation_result = stock_collector.validate_symbol(symbol)
        print(f"🔍 Validation result for {symbol}: {validation_result}")
        
        if not validation_result:
            print(f"❌ Symbol validation failed for: {symbol}")
            return JSONResponse(
                status_code=400,
                content={"error": f"유효하지 않은 종목 코드: {symbol}"}
            )
        
        stock_data = stock_collector.get_stock_data(symbol)
        
        # 2. 가치투자 분석
        analysis_result = value_analyzer.analyze_stock(stock_data, gemini_client)
        
        # 3. AI 심층 분석
        prompt = generate_analysis_prompt(depth)
        ai_analysis = gemini_client.generate_analysis(
            prompt=prompt,
            stock_data=stock_data,
            thinking_enabled=True
        )
        
        # 4. 결과 반환
        return JSONResponse(content={
            "success": True,
            "symbol": symbol,
            "company_name": analysis_result.company_name,
            "current_price": analysis_result.current_price,
            "target_price": analysis_result.target_price,
            "upside_potential": analysis_result.upside_potential,
            "investment_grade": analysis_result.investment_grade.value,
            "confidence_score": analysis_result.confidence_score,
            "key_strengths": analysis_result.key_strengths,
            "key_weaknesses": analysis_result.key_weaknesses,
            "risks": analysis_result.risks,
            "financial_metrics": {
                "pe_ratio": analysis_result.value_metrics.pe_ratio,
                "pb_ratio": analysis_result.value_metrics.pb_ratio,
                "roe": analysis_result.value_metrics.roe,
                "roa": analysis_result.value_metrics.roa,
                "debt_to_equity": analysis_result.value_metrics.debt_to_equity,
                "dividend_yield": analysis_result.value_metrics.dividend_yield,
                "revenue_growth": analysis_result.value_metrics.revenue_growth,
                "income_growth": analysis_result.value_metrics.income_growth
            },
            "ai_analysis": ai_analysis,
            "analysis_date": analysis_result.analysis_date
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"분석 중 오류 발생: {str(e)}"}
        )

@app.post("/api/compare")
async def compare_stocks(
    symbols: str = Form(...),
    depth: str = Form(default="comprehensive")
):
    """주식 비교 분석 API"""
    try:
        if not all([stock_collector, gemini_client, value_analyzer]):
            return JSONResponse(
                status_code=500,
                content={"error": "시스템이 초기화되지 않았습니다."}
            )
        
        # 종목 코드 파싱
        symbol_list = [s.strip().upper() for s in symbols.split(',')]
        symbol_list = [s for s in symbol_list if s]  # 빈 문자열 제거
        
        if len(symbol_list) < 2:
            return JSONResponse(
                status_code=400,
                content={"error": "비교를 위해서는 최소 2개의 종목이 필요합니다."}
            )
        
        if len(symbol_list) > 5:
            return JSONResponse(
                status_code=400,
                content={"error": "최대 5개의 종목까지 비교 가능합니다."}
            )
        
        # 1. 데이터 수집 및 분석
        results = []
        stock_data_dict = {}
        
        for symbol in symbol_list:
            if not stock_collector.validate_symbol(symbol):
                return JSONResponse(
                    status_code=400,
                    content={"error": f"유효하지 않은 종목 코드: {symbol}"}
                )
            
            stock_data = stock_collector.get_stock_data(symbol)
            stock_data_dict[symbol] = stock_data
            
            analysis_result = value_analyzer.analyze_stock(stock_data, gemini_client)
            
            results.append({
                "symbol": symbol,
                "company_name": analysis_result.company_name,
                "current_price": analysis_result.current_price,
                "target_price": analysis_result.target_price,
                "upside_potential": analysis_result.upside_potential,
                "investment_grade": analysis_result.investment_grade.value,
                "confidence_score": analysis_result.confidence_score,
                "financial_metrics": {
                    "pe_ratio": analysis_result.value_metrics.pe_ratio,
                    "pb_ratio": analysis_result.value_metrics.pb_ratio,
                    "roe": analysis_result.value_metrics.roe,
                    "roa": analysis_result.value_metrics.roa,
                    "debt_to_equity": analysis_result.value_metrics.debt_to_equity,
                    "dividend_yield": analysis_result.value_metrics.dividend_yield,
                    "revenue_growth": analysis_result.value_metrics.revenue_growth,
                    "income_growth": analysis_result.value_metrics.income_growth
                }
            })
        
        # 2. AI 비교 분석
        comparison_analysis = gemini_client.generate_comparison_analysis(stock_data_dict)
        
        return JSONResponse(content={
            "success": True,
            "symbols": symbol_list,
            "results": results,
            "comparison_analysis": comparison_analysis,
            "analysis_date": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"비교 분석 중 오류 발생: {str(e)}"}
        )

@app.get("/api/validate/{symbol}")
async def validate_symbol(symbol: str):
    """종목 코드 유효성 검사 API"""
    try:
        if not stock_collector:
            print(f"❌ validate_symbol: stock_collector가 None입니다.")
            return JSONResponse(
                status_code=500,
                content={"error": "시스템이 초기화되지 않았습니다. 관리자에게 문의하세요."}
            )
        
        symbol = symbol.upper().strip()
        is_valid = stock_collector.validate_symbol(symbol)
        
        suggestions = []
        if not is_valid:
            suggestions = stock_collector.search_similar_symbols(symbol)
        
        return JSONResponse(content={
            "valid": is_valid,
            "symbol": symbol,
            "suggestions": suggestions
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"검증 중 오류 발생: {str(e)}"}
        )

@app.get("/compare", response_class=HTMLResponse)
async def compare_page(request: Request):
    """비교 분석 페이지"""
    return templates.TemplateResponse("compare.html", {"request": request})

@app.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request):
    """보고서 목록 페이지"""
    return templates.TemplateResponse("reports.html", {"request": request})

def generate_analysis_prompt(depth: str) -> str:
    """분석 깊이에 따른 프롬프트 생성"""
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
2. 재무 분석 (3년간 트렌드)
3. 비즈니스 분석 (경쟁우위, 해자)
4. 위험 분석 (시장/신용/유동성 위험)
5. 투자 전략 (장기 관점)
6. ESG 요소 고려사항

각 항목을 구체적인 근거와 함께 분석하고, 
최종적으로 명확한 투자 의견을 제시해주세요.
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)