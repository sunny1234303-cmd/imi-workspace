#!/usr/bin/env python3
"""
네이버 검색광고 API 클라이언트

키워드 도구를 사용하여 월간 검색량, 예상 CPC, 경쟁 강도 등을 조회.

사용법:
    # 키워드 분석
    python naver_searchad.py keyword "키워드1,키워드2"

    # 연관 키워드 포함
    python naver_searchad.py keyword "침대" --include-related

    # 구글 시트 저장
    python naver_searchad.py keyword "가구,침대" --sheet "SHEET_URL" --tab "키워드분석"

예시:
    python naver_searchad.py keyword "침대,소파,책상"
    python naver_searchad.py keyword "뷰티" --include-related --sheet "https://docs.google.com/..."
"""

import os
import sys
import json
import time
import hmac
import hashlib
import base64
import argparse
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# .env 로드
load_dotenv(Path(__file__).parent / '.env')

NAVER_AD_ACCESS_LICENSE = os.getenv('NAVER_AD_ACCESS_LICENSE')
NAVER_AD_SECRET_KEY = os.getenv('NAVER_AD_SECRET_KEY')
NAVER_AD_CUSTOMER_ID = os.getenv('NAVER_AD_CUSTOMER_ID')

BASE_URL = "https://api.searchad.naver.com"

# 색상 출력
class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'

def print_color(text, color):
    print(f"{color}{text}{Colors.NC}", file=sys.stderr)

def print_json(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))


def generate_signature(timestamp, method, uri):
    """HMAC-SHA256 서명 생성"""
    secret_key = NAVER_AD_SECRET_KEY
    message = f"{timestamp}.{method}.{uri}"

    signature = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()

    return base64.b64encode(signature).decode('utf-8')


def api_request(method, uri, params=None):
    """네이버 검색광고 API 요청"""

    if not all([NAVER_AD_ACCESS_LICENSE, NAVER_AD_SECRET_KEY, NAVER_AD_CUSTOMER_ID]):
        print_color("❌ 네이버 검색광고 API 키가 설정되지 않았습니다", Colors.RED)
        print_color("   .env 파일에 NAVER_AD_ACCESS_LICENSE, NAVER_AD_SECRET_KEY, NAVER_AD_CUSTOMER_ID 추가", Colors.YELLOW)
        sys.exit(1)

    timestamp = str(int(time.time() * 1000))
    signature = generate_signature(timestamp, method, uri)

    headers = {
        'X-Timestamp': timestamp,
        'X-API-KEY': NAVER_AD_ACCESS_LICENSE,
        'X-Customer': NAVER_AD_CUSTOMER_ID,
        'X-Signature': signature,
        'Content-Type': 'application/json'
    }

    url = BASE_URL + uri
    if params and method == 'GET':
        url += '?' + urllib.parse.urlencode(params)

    request = urllib.request.Request(url, method=method, headers=headers)

    try:
        response = urllib.request.urlopen(request)
        return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print_color(f"❌ API 오류: {e.code}", Colors.RED)
        print_color(error_body, Colors.RED)
        return None


def get_keyword_stats(keywords, include_related=False):
    """
    키워드 도구 API 호출

    Returns:
        - relKeyword: 연관 키워드
        - monthlyPcQcCnt: PC 월간 검색수
        - monthlyMobileQcCnt: 모바일 월간 검색수
        - monthlyAvePcClkCnt: PC 월평균 클릭수
        - monthlyAveMobileClkCnt: 모바일 월평균 클릭수
        - monthlyAvePcCtr: PC 월평균 클릭률
        - monthlyAveMobileCtr: 모바일 월평균 클릭률
        - plAvgDepth: 월평균 노출 광고수
        - compIdx: 경쟁정도 (높음/중간/낮음)
    """

    uri = "/keywordstool"

    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(',')]

    params = {
        'hintKeywords': ','.join(keywords),
        'showDetail': '1'
    }

    if include_related:
        params['includeHintKeywords'] = '1'

    result = api_request('GET', uri, params)
    return result


def format_keyword_data(api_result):
    """API 결과를 테이블 형식으로 변환"""

    if not api_result or 'keywordList' not in api_result:
        return []

    rows = []
    headers = [
        '키워드', 'PC검색량', '모바일검색량', '총검색량',
        'PC클릭수', '모바일클릭수', 'PC클릭률', '모바일클릭률',
        '경쟁강도', '노출광고수', '수집일시'
    ]
    rows.append(headers)

    collected_at = datetime.now().strftime('%Y-%m-%d %H:%M')

    for kw in api_result['keywordList']:
        pc_qc = kw.get('monthlyPcQcCnt', 0) or 0
        mo_qc = kw.get('monthlyMobileQcCnt', 0) or 0

        # "< 10" 같은 값 처리
        if isinstance(pc_qc, str):
            pc_qc = 10 if '< 10' in pc_qc else int(pc_qc.replace(',', ''))
        if isinstance(mo_qc, str):
            mo_qc = 10 if '< 10' in mo_qc else int(mo_qc.replace(',', ''))

        rows.append([
            kw.get('relKeyword', ''),
            str(pc_qc),
            str(mo_qc),
            str(pc_qc + mo_qc),
            str(kw.get('monthlyAvePcClkCnt', 0) or 0),
            str(kw.get('monthlyAveMobileClkCnt', 0) or 0),
            str(kw.get('monthlyAvePcCtr', 0) or 0),
            str(kw.get('monthlyAveMobileCtr', 0) or 0),
            kw.get('compIdx', '-'),
            str(kw.get('plAvgDepth', 0) or 0),
            collected_at
        ])

    return rows


def save_to_sheet(rows, sheet_url, tab_name):
    """구글 시트에 저장"""
    import subprocess

    tmp_file = '/tmp/naver_keyword_data.json'
    with open(tmp_file, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False)

    script_dir = Path(__file__).parent
    cmd = [
        '/Library/Developer/CommandLineTools/usr/bin/python3',
        str(script_dir / 'gsheet_api.py'),
        'write',
        sheet_url,
        tmp_file,
        '--tab', tab_name
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print_color(f"✅ 구글 시트 저장 완료: {tab_name}", Colors.GREEN)
    else:
        print_color(f"❌ 시트 저장 실패: {result.stderr}", Colors.RED)


def save_to_local(rows, keywords):
    """로컬 마크다운 파일로 저장"""

    output_dir = Path('/Users/seoni/imi-workspace/30-knowledge/32-marketing/keywords')
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    filename = f"keyword_analysis_{timestamp}.md"
    filepath = output_dir / filename

    md_content = f"# 키워드 분석 결과\n\n"
    md_content += f"**수집일시**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    md_content += f"**분석 키워드**: {', '.join(keywords) if isinstance(keywords, list) else keywords}\n\n"
    md_content += "## 데이터\n\n"
    md_content += "| " + " | ".join(rows[0][:6]) + " |\n"  # 주요 컬럼만
    md_content += "| " + " | ".join(['---'] * 6) + " |\n"
    for row in rows[1:]:
        md_content += "| " + " | ".join(row[:6]) + " |\n"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print_color(f"💾 로컬 저장: {filepath}", Colors.GREEN)
    return str(filepath)


def cmd_keyword(args):
    """키워드 분석 명령"""

    print_color(f"🔍 네이버 검색광고 키워드 분석", Colors.BLUE)
    print_color(f"   키워드: {args.keywords}", Colors.BLUE)
    print_color(f"   연관키워드 포함: {args.include_related}", Colors.BLUE)

    # API 호출
    result = get_keyword_stats(
        keywords=args.keywords,
        include_related=args.include_related
    )

    if not result:
        print_color("❌ API 호출 실패", Colors.RED)
        return

    # 데이터 포맷팅
    rows = format_keyword_data(result)

    if len(rows) <= 1:
        print_color("⚠️ 조회된 데이터가 없습니다", Colors.YELLOW)
        return

    print_color(f"✅ {len(rows)-1}개 키워드 분석 완료", Colors.GREEN)

    # 로컬 저장
    keywords = [k.strip() for k in args.keywords.split(',')]
    local_path = save_to_local(rows, keywords)

    # 구글 시트 저장 (옵션)
    if args.sheet:
        tab_name = args.tab or 'Raw_키워드'
        save_to_sheet(rows, args.sheet, tab_name)

    # 요약 출력
    print_color("\n📊 주요 키워드 요약:", Colors.BLUE)
    for row in rows[1:6]:  # 상위 5개만
        total = int(row[3]) if row[3].isdigit() else 0
        print_color(f"   {row[0]}: 월 {total:,}회 검색, 경쟁 {row[8]}", Colors.NC)

    # JSON 출력
    output = {
        "status": "success",
        "keywords": keywords,
        "keyword_count": len(rows) - 1,
        "local_file": local_path,
        "raw_result": result
    }

    print_json(output)


def main():
    parser = argparse.ArgumentParser(description='네이버 검색광고 API 클라이언트')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # keyword 명령
    kw_parser = subparsers.add_parser('keyword', help='키워드 분석')
    kw_parser.add_argument('keywords', help='키워드 (쉼표로 구분)')
    kw_parser.add_argument('--include-related', action='store_true', help='연관 키워드 포함')
    kw_parser.add_argument('--sheet', help='저장할 구글 시트 URL')
    kw_parser.add_argument('--tab', help='저장할 탭 이름 (기본: 키워드분석)')

    args = parser.parse_args()

    if args.command == 'keyword':
        cmd_keyword(args)


if __name__ == "__main__":
    main()
