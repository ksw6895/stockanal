#!/bin/bash
echo "🚀 프로젝트 환경 시작 중..."
source venv/bin/activate
echo "✅ 가상환경 활성화 완료!"
echo "📦 설치된 패키지 목록:"
pip list
echo ""
echo "💡 작업을 마치면 'deactivate' 명령어로 가상환경을 종료하세요." 