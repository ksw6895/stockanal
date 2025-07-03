# 🚀 AI 기반 주식 가치투자 분석 시스템

Gemini 2.5 Flash를 활용한 실시간 주식 가치투자 평가 웹 애플리케이션

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FYOUR_USERNAME%2Fai-stock-analyzer)

🌐 **[Live Demo](https://ai-stock-analyzer.vercel.app)** | 📖 **[Documentation](#사용법)**

## 📋 목차

- [개요](#개요)
- [주요 기능](#주요-기능)
- [시스템 요구사항](#시스템-요구사항)
- [로컬 설치 가이드](#로컬-설치-가이드)
- [Vercel 배포 가이드](#vercel-배포-가이드)
- [사용법](#사용법)
- [분석 예시](#분석-예시)
- [프로젝트 구조](#프로젝트-구조)
- [기술 스택](#기술-스택)
- [문제 해결](#문제-해결)
- [기여하기](#기여하기)
- [라이선스](#라이선스)

## 🎯 개요

이 프로그램은 Google의 최신 AI 모델인 **Gemini 2.5 Flash**를 활용하여 주식의 가치투자 관점에서의 종합적인 분석을 제공합니다. 워렌 버핏과 벤저민 그레이엄의 가치투자 철학을 바탕으로 한 분석 알고리즘과 AI의 심층 분석을 결합하여 신뢰할 수 있는 투자 인사이트를 제공합니다.

### ✨ 특징

- 🤖 **최신 AI 모델**: Gemini 2.5 Flash의 사고 기능(Thinking)을 활용한 심층 분석
- 📊 **실시간 데이터**: yfinance를 통한 실시간 주식 데이터 수집
- 💎 **가치투자 철학**: 워렌 버핏, 벤저민 그레이엄의 투자 원칙 적용
- 📈 **다양한 분석**: 개별 종목, 비교 분석, 포트폴리오 분석 지원
- 📄 **다양한 보고서**: Markdown, HTML, JSON 형식의 상세 보고서 생성
- 🎨 **사용자 친화적**: Rich 라이브러리를 활용한 아름다운 CLI 인터페이스

## 🔧 주요 기능

### 🌐 웹 기반 분석
- **개별 종목 분석**: 실시간 재무 데이터 수집 및 AI 기반 종합 평가
- **종목 비교 분석**: 최대 5개 종목 동시 비교 및 투자 우선순위 제시
- **실시간 차트**: Chart.js를 활용한 인터랙티브 비교 차트
- **반응형 디자인**: 모바일, 태블릿, 데스크톱 모든 환경 지원

### 🤖 AI 기반 분석
- **Gemini 2.5 Flash**: 최신 AI 모델의 사고 기능 활용
- **가치투자 철학**: 워렌 버핏, 벤저민 그레이엄 원칙 자동 적용
- **실시간 등급 결정**: AI가 직접 투자 등급과 신뢰도 산정
- **심층 분석**: 종합적인 투자 의견 및 위험 요인 분석

### 📊 핵심 분석 지표
- **밸류에이션**: PER, PBR, PEG 비율
- **수익성**: ROE, ROA, 순이익률
- **성장성**: 매출/순이익 성장률
- **안정성**: 부채비율, 현금흐름
- **배당**: 배당수익률 및 안정성

## 💻 시스템 요구사항

- **Python**: 3.9 이상
- **운영체제**: Windows, macOS, Linux
- **인터넷 연결**: 실시간 데이터 수집 및 AI 분석을 위해 필요
- **Google API 키**: Gemini API 사용을 위해 필요

## 🛠 로컬 설치 가이드

### 1. 저장소 클론 및 환경 설정

```bash
# 프로젝트 클론
git clone https://github.com/YOUR_USERNAME/ai-stock-analyzer.git
cd ai-stock-analyzer

# Python 가상환경 생성 (권장)
python -m venv venv

# 가상환경 활성화
# Windows:
venv\\Scripts\\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

```bash
# .env.example 파일을 복사하여 .env 파일 생성
cp .env.example .env
```

`.env` 파일에 Google API 키 설정:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 4. 로컬 서버 실행

```bash
# FastAPI 웹 서버 실행
python app.py

# 또는 uvicorn으로 실행
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

브라우저에서 `http://localhost:8000` 접속

## 🚀 Vercel 배포 가이드

### 1. Vercel에 배포하기

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FYOUR_USERNAME%2Fai-stock-analyzer)

### 2. 수동 배포 방법

1. **GitHub 저장소 생성**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/ai-stock-analyzer.git
   git push -u origin main
   ```

2. **Vercel 프로젝트 생성**
   - [Vercel 대시보드](https://vercel.com)에 로그인
   - "New Project" 클릭
   - GitHub 저장소 연결
   - 프로젝트 배포

3. **환경 변수 설정**
   - Vercel 프로젝트 Settings → Environment Variables
   - `GOOGLE_API_KEY` 추가

### 3. 자동 배포 설정

GitHub에 푸시할 때마다 자동으로 배포됩니다:

```bash
git add .
git commit -m "Update features"
git push origin main
```

## 🚀 사용법

### 🌐 웹 인터페이스 (권장)

1. **홈페이지 접속**
   - 로컬: `http://localhost:8000`
   - 배포된 사이트: `https://your-app.vercel.app`

2. **개별 종목 분석**
   - 네비게이션에서 "개별 분석" 클릭
   - 종목 코드 입력 (예: AAPL, MSFT)
   - 분석 깊이 선택
   - "분석 시작" 버튼 클릭

3. **종목 비교 분석**
   - 네비게이션에서 "비교 분석" 클릭
   - 여러 종목 코드를 쉼표로 구분하여 입력
   - 비교 분석 결과 및 차트 확인

### 📱 모바일 지원

- **반응형 디자인**: 모든 기기에서 최적화된 경험
- **터치 인터페이스**: 모바일 친화적인 버튼과 입력
- **빠른 분석**: 홈페이지에서 바로 종목 코드 입력 가능

### 🖥️ CLI 모드 (로컬에서만)

기존 CLI 인터페이스도 계속 지원됩니다:

```bash
# 기존 CLI 모드 실행
python main.py

# 단일 종목 분석
python main.py --symbol AAPL

# 여러 종목 비교 분석
python main.py --symbols "AAPL,MSFT,GOOGL"
```

## 📊 분석 예시

### 개별 종목 분석 결과

```
📊 AAPL - Apple Inc. 가치투자 분석 결과

등급: Buy
현재가: $150.50
목표가: $165.00
상승여력: 9.6%

📈 주요 재무 지표
- PER: 25.3
- PBR: 12.5
- ROE: 26.4%
- 부채비율: 1.73

✅ 주요 강점
• 우수한 수익성 (ROE 26.4%, ROA 18.2%)
• 강력한 브랜드 파워와 생태계
• 안정적인 현금 창출 능력

⚠️ 주요 위험
• 높은 밸류에이션 (PER 25.3)
• 중국 시장 의존도
```

### 비교 분석 결과

```
📊 종목별 비교 요약

| 종목 | 등급 | 상승여력 | PER | ROE |
|------|------|----------|-----|-----|
| AAPL | Buy  | 9.6%     | 25.3| 26.4%|
| MSFT | Strong Buy| 15.2%| 28.1| 34.2%|
| GOOGL| Hold | 3.8%     | 22.4| 18.9%|
```

## 📁 프로젝트 구조

```
ai-stock-analyzer/
├── app.py                       # FastAPI 웹 애플리케이션
├── main.py                      # CLI 모드 (로컬 전용)
├── requirements.txt             # 의존성 패키지
├── vercel.json                  # Vercel 배포 설정
├── .env.example                 # 환경변수 예시
├── .gitignore                   # Git 제외 파일
├── README.md                    # 프로젝트 문서
├── modules/                     # 코어 모듈
│   ├── __init__.py
│   ├── stock_data_collector.py  # 주식 데이터 수집
│   ├── gemini_client.py         # Gemini API 클라이언트
│   ├── value_analyzer.py        # AI 기반 가치투자 분석
│   └── report_generator.py      # 보고서 생성 (CLI용)
├── templates/                   # HTML 템플릿
│   ├── base.html               # 기본 레이아웃
│   ├── index.html              # 홈페이지
│   ├── analyze.html            # 개별 분석 페이지
│   ├── compare.html            # 비교 분석 페이지
│   └── reports.html            # 보고서 관리
├── static/                     # 정적 파일
│   ├── css/                    # 사용자 정의 CSS
│   └── js/                     # 사용자 정의 JavaScript
└── reports/                    # 생성된 보고서 (CLI 모드)
    └── .gitkeep               # Git 디렉터리 유지
```

## 🔧 기술 스택

### 🌐 웹 프레임워크
- **FastAPI**: 현대적이고 빠른 Python 웹 프레임워크
- **Uvicorn**: ASGI 서버
- **Jinja2**: HTML 템플릿 엔진

### 🎨 프론트엔드
- **Bootstrap 5**: 반응형 UI 프레임워크
- **Chart.js**: 인터랙티브 차트 라이브러리
- **Font Awesome**: 아이콘 라이브러리
- **Vanilla JavaScript**: 가벼운 클라이언트 사이드 로직

### 🤖 AI & API
- **Google Gemini 2.5 Flash**: 최신 AI 모델을 통한 심층 분석
- **google-genai**: 공식 Google Gen AI Python SDK

### 📊 데이터 수집 & 분석
- **yfinance**: 실시간 주식 데이터 수집
- **pandas**: 데이터 처리 및 분석
- **numpy**: 수치 계산

### 🚀 배포 & 인프라
- **Vercel**: 서버리스 배포 플랫폼
- **GitHub**: 코드 관리 및 자동 배포
- **Python 3.9+**: 런타임 환경

### 🛠️ 개발 도구
- **python-dotenv**: 환경변수 관리
- **rich**: CLI 인터페이스 (로컬 모드)
- **requests**: HTTP 요청 처리

## 🔍 분석 방법론

### 가치투자 핵심 지표

1. **밸류에이션 지표**
   - PER (Price-to-Earnings Ratio): 주가수익비율
   - PBR (Price-to-Book Ratio): 주가순자산비율
   - PEG (Price/Earnings to Growth): PER 대비 성장률

2. **수익성 지표**
   - ROE (Return on Equity): 자기자본수익률
   - ROA (Return on Assets): 총자산수익률
   - 순이익률

3. **안정성 지표**
   - 부채비율 (Debt-to-Equity)
   - 유동비율 (Current Ratio)
   - 이자보상배율

4. **성장성 지표**
   - 매출 성장률
   - 순이익 성장률
   - 영업현금흐름 성장률

### AI 분석 프로세스

1. **데이터 수집**: 실시간 재무 데이터 및 주가 정보
2. **정량 분석**: 수학적 모델을 통한 객관적 평가
3. **AI 분석**: Gemini 2.5 Flash를 통한 정성적 분석
4. **종합 평가**: 정량·정성 분석 결합한 최종 투자 의견

## ❗ 문제 해결

### 자주 발생하는 문제

#### 1. API 키 오류
```
❌ Google API 키가 설정되지 않았습니다.
```
**해결방법**: `.env` 파일에서 `GOOGLE_API_KEY` 확인

#### 2. 종목 코드 오류
```
❌ 유효하지 않은 종목 코드: ABC
```
**해결방법**: 올바른 티커 심볼 사용 (예: AAPL, MSFT)

#### 3. 네트워크 연결 오류
```
❌ 데이터 수집 실패: Connection timeout
```
**해결방법**: 인터넷 연결 확인 후 재시도

#### 4. 패키지 설치 오류
```bash
# 패키지 업데이트
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### 로그 확인

프로그램 실행 시 `stock_analyzer.log` 파일에 상세한 로그가 기록됩니다.

```bash
# 로그 파일 확인
tail -f stock_analyzer.log
```

## 🤝 기여하기

이 프로젝트에 기여하고 싶으시다면:

1. 이슈를 확인하거나 새로운 이슈를 생성하세요
2. 기능 개선이나 버그 수정을 위한 브랜치를 생성하세요
3. 코드 변경 후 테스트를 진행하세요
4. Pull Request를 제출하세요

### 개발 환경 설정

```bash
# 개발용 패키지 추가 설치
pip install pytest black flake8 mypy

# 코드 포맷팅
black *.py modules/*.py

# 린트 검사
flake8 *.py modules/*.py

# 타입 검사
mypy *.py modules/*.py
```

## ⚠️ 주의사항

1. **투자 책임**: 본 프로그램은 투자 참고용으로만 사용하시기 바랍니다. 모든 투자 결정과 그에 따른 결과는 사용자 본인의 책임입니다.

2. **데이터 정확성**: 실시간 데이터이지만 지연이나 오류가 있을 수 있습니다. 중요한 투자 결정 시에는 공식 금융 데이터를 추가로 확인하시기 바랍니다.

3. **API 제한**: Google Gemini API에는 사용량 제한이 있을 수 있습니다. 과도한 사용 시 일시적으로 서비스가 제한될 수 있습니다.

4. **개인정보 보호**: API 키는 절대 공유하지 마시고, `.env` 파일을 버전 관리 시스템에 커밋하지 마세요.

## 📞 지원

- **이슈 리포트**: GitHub Issues를 통해 버그 리포트나 기능 요청
- **문의사항**: 프로젝트 관련 질문이나 제안사항

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

---

**🎯 Happy Investing! 현명한 가치투자를 위한 여정을 시작하세요!**