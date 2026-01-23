#!/usr/bin/env python3
"""
네이버 데이터랩 API 클라이언트

키워드 검색량 트렌드를 조회하고 구글 시트에 저장.

사용법:
    # 키워드 트렌드 조회
    python naver_datalab.py trend "키워드1,키워드2" [--days 30]

    # 결과를 구글 시트에 저장
    python naver_datalab.py trend "침대,책상,소파" --sheet "SHEET_URL" --tab "키워드트렌드"

예시:
    python naver_datalab.py trend "유아영어,화상영어" --days 90
    python naver_datalab.py trend "가구,인테리어" --sheet "https://docs.google.com/spreadsheets/d/xxx"
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv

# .env 로드
load_dotenv(Path(__file__).parent / '.env')

NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET')

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


def get_trend(keywords, days=30, time_unit='date', device='', gender='', ages=[]):
    """
    네이버 데이터랩 검색어 트렌드 API 호출

    Args:
        keywords: 키워드 리스트 (최대 5개 그룹, 각 그룹 최대 20개 키워드)
        days: 조회 기간 (일)
        time_unit: 'date' (일별), 'week' (주별), 'month' (월별)
        device: '' (전체), 'pc', 'mo' (모바일)
        gender: '' (전체), 'm' (남성), 'f' (여성)
        ages: 연령대 리스트 ['1' (0-12), '2' (13-18), '3' (19-24), '4' (25-29), ...]
    """

    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        print_color("❌ 네이버 API 키가 설정되지 않았습니다", Colors.RED)
        print_color("   .env 파일에 NAVER_CLIENT_ID, NAVER_CLIENT_SECRET 추가", Colors.YELLOW)
        sys.exit(1)

    url = "https://openapi.naver.com/v1/datalab/search"

    # 날짜 계산
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # 키워드 그룹 생성 (각 키워드를 별도 그룹으로)
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(',')]

    keyword_groups = []
    for kw in keywords[:5]:  # 최대 5개 그룹
        keyword_groups.append({
            "groupName": kw,
            "keywords": [kw]
        })

    body = {
        "startDate": start_date.strftime("%Y-%m-%d"),
        "endDate": end_date.strftime("%Y-%m-%d"),
        "timeUnit": time_unit,
        "keywordGroups": keyword_groups
    }

    if device:
        body["device"] = device
    if gender:
        body["gender"] = gender
    if ages:
        body["ages"] = ages

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", NAVER_CLIENT_ID)
    request.add_header("X-Naver-Client-Secret", NAVER_CLIENT_SECRET)
    request.add_header("Content-Type", "application/json")

    try:
        response = urllib.request.urlopen(request, data=json.dumps(body).encode("utf-8"))
        result = json.loads(response.read().decode("utf-8"))
        return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print_color(f"❌ API 오류: {e.code}", Colors.RED)
        print_color(error_body, Colors.RED)
        sys.exit(1)


def format_trend_data(api_result):
    """API 결과를 테이블 형식으로 변환"""

    if 'results' not in api_result:
        return []

    rows = []
    headers = ['키워드', '날짜', '검색지수', '수집일시']
    rows.append(headers)

    collected_at = datetime.now().strftime('%Y-%m-%d %H:%M')

    for group in api_result['results']:
        keyword = group['title']
        for data_point in group['data']:
            rows.append([
                keyword,
                data_point['period'],
                str(data_point['ratio']),
                collected_at
            ])

    return rows


def save_to_sheet(rows, sheet_url, tab_name):
    """구글 시트에 저장"""
    import subprocess

    # JSON 파일로 저장
    tmp_file = '/tmp/naver_trend_data.json'
    with open(tmp_file, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False)

    # gsheet_api.py 호출
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

    output_dir = Path('/Users/seoni/imi-workspace/30-knowledge/32-marketing/trends')
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    filename = f"trend_{timestamp}.md"
    filepath = output_dir / filename

    # 마크다운 생성
    md_content = f"# 키워드 트렌드 분석\n\n"
    md_content += f"**수집일시**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    md_content += f"**키워드**: {', '.join(keywords) if isinstance(keywords, list) else keywords}\n\n"
    md_content += "## 데이터\n\n"
    md_content += "| " + " | ".join(rows[0]) + " |\n"
    md_content += "| " + " | ".join(['---'] * len(rows[0])) + " |\n"
    for row in rows[1:]:
        md_content += "| " + " | ".join(row) + " |\n"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print_color(f"💾 로컬 저장: {filepath}", Colors.GREEN)
    return str(filepath)


def cmd_trend(args):
    """트렌드 조회 명령"""

    print_color(f"🔍 네이버 데이터랩 검색 트렌드 조회", Colors.BLUE)
    print_color(f"   키워드: {args.keywords}", Colors.BLUE)
    print_color(f"   기간: {args.days}일", Colors.BLUE)

    # API 호출
    result = get_trend(
        keywords=args.keywords,
        days=args.days,
        time_unit=args.time_unit,
        device=args.device
    )

    # 데이터 포맷팅
    rows = format_trend_data(result)

    if len(rows) <= 1:
        print_color("⚠️ 조회된 데이터가 없습니다", Colors.YELLOW)
        return

    print_color(f"✅ {len(rows)-1}개 데이터 포인트 수집", Colors.GREEN)

    # 로컬 저장
    keywords = [k.strip() for k in args.keywords.split(',')]
    local_path = save_to_local(rows, keywords)

    # 구글 시트 저장 (옵션)
    if args.sheet:
        tab_name = args.tab or 'Raw_트렌드'
        save_to_sheet(rows, args.sheet, tab_name)

    # JSON 출력
    output = {
        "status": "success",
        "keywords": keywords,
        "period_days": args.days,
        "data_points": len(rows) - 1,
        "local_file": local_path,
        "raw_result": result
    }

    print_json(output)


def main():
    parser = argparse.ArgumentParser(description='네이버 데이터랩 API 클라이언트')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # trend 명령
    trend_parser = subparsers.add_parser('trend', help='키워드 검색 트렌드 조회')
    trend_parser.add_argument('keywords', help='키워드 (쉼표로 구분, 최대 5개)')
    trend_parser.add_argument('--days', type=int, default=30, help='조회 기간 (기본: 30일)')
    trend_parser.add_argument('--time-unit', choices=['date', 'week', 'month'], default='date', help='시간 단위')
    trend_parser.add_argument('--device', choices=['', 'pc', 'mo'], default='', help='디바이스 (기본: 전체)')
    trend_parser.add_argument('--sheet', help='저장할 구글 시트 URL')
    trend_parser.add_argument('--tab', help='저장할 탭 이름 (기본: 키워드트렌드)')

    args = parser.parse_args()

    if args.command == 'trend':
        cmd_trend(args)


if __name__ == "__main__":
    main()
