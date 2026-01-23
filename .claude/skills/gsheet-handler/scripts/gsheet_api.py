#!/usr/bin/env python3
"""
Google Sheets API Handler

구글 시트 읽기/쓰기/업데이트를 위한 범용 스크립트.
기존 gspread OAuth 인증 (~/.config/gspread/) 활용.

사용법:
    # 시트 읽기
    python gsheet_api.py read <sheet_url> [--tab TAB_NAME] [--range A1:B10]

    # 시트 쓰기 (JSON 파일에서)
    python gsheet_api.py write <sheet_url> <json_file> [--tab TAB_NAME]

    # 시트 업데이트 (특정 셀)
    python gsheet_api.py update <sheet_url> --cell A1 --value "새 값"

    # 새 탭 생성
    python gsheet_api.py create-tab <sheet_url> --name "새탭" [--rows 100] [--cols 26]

    # 탭 목록 조회
    python gsheet_api.py list-tabs <sheet_url>

예시:
    python gsheet_api.py read "https://docs.google.com/spreadsheets/d/xxx" --tab "키워드트렌드"
    python gsheet_api.py write "https://docs.google.com/spreadsheets/d/xxx" data.json --tab "수집로그"
"""

import os
import sys
import re
import json
import argparse
from datetime import datetime
from pathlib import Path

# 색상 출력
class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'

def print_color(text, color):
    print(f"{color}{text}{Colors.NC}")

def print_json(data):
    """JSON 형식으로 출력 (Claude가 파싱하기 쉽게)"""
    print(json.dumps(data, ensure_ascii=False, indent=2))


def get_credentials():
    """OAuth 자격증명 가져오기"""
    import gspread
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = None
    creds_path = os.path.expanduser('~/.config/gspread/credentials.json')
    token_path = os.path.expanduser('~/.config/gspread/authorized_user.json')

    # 저장된 토큰 로드
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # 유효한 자격증명이 없으면 인증 진행
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_path):
                print_color(f"❌ OAuth 자격증명이 없습니다: {creds_path}", Colors.RED)
                print("\n설정 방법:")
                print("1. Google Cloud Console에서 OAuth 2.0 클라이언트 ID 생성")
                print("2. JSON 파일을 ~/.config/gspread/credentials.json에 저장")
                sys.exit(1)

            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # 토큰 저장
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return gspread.authorize(creds)


def extract_sheet_id(sheet_url):
    """URL에서 시트 ID 추출"""
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', sheet_url)
    if not match:
        raise ValueError(f"시트 URL이 올바르지 않습니다: {sheet_url}")
    return match.group(1)


def cmd_read(args):
    """시트 읽기"""
    gc = get_credentials()
    sheet_id = extract_sheet_id(args.sheet_url)
    spreadsheet = gc.open_by_key(sheet_id)

    # 탭 선택
    if args.tab:
        try:
            worksheet = spreadsheet.worksheet(args.tab)
        except:
            print_color(f"❌ 탭을 찾을 수 없습니다: {args.tab}", Colors.RED)
            print("사용 가능한 탭:", [ws.title for ws in spreadsheet.worksheets()])
            sys.exit(1)
    else:
        worksheet = spreadsheet.sheet1

    # 범위 지정 또는 전체
    if args.range:
        data = worksheet.get(args.range)
    else:
        data = worksheet.get_all_values()

    # 결과 출력
    result = {
        "sheet_id": sheet_id,
        "tab": worksheet.title,
        "range": args.range or "ALL",
        "row_count": len(data),
        "data": data
    }

    print_json(result)
    return result


def cmd_write(args):
    """시트 쓰기 (JSON 파일에서)"""
    gc = get_credentials()
    sheet_id = extract_sheet_id(args.sheet_url)
    spreadsheet = gc.open_by_key(sheet_id)

    # JSON 파일 로드
    with open(args.json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 데이터 형식 확인 및 변환
    if isinstance(data, dict):
        # dict인 경우: headers와 rows로 분리된 형식 지원
        if 'headers' in data and 'rows' in data:
            rows = [data['headers']] + data['rows']
        elif 'data' in data:
            rows = data['data']
        else:
            # dict를 키-값 쌍으로 변환
            rows = [['키', '값']] + [[k, str(v)] for k, v in data.items()]
    elif isinstance(data, list):
        if data and isinstance(data[0], dict):
            # dict 리스트: 첫 번째 항목의 키를 헤더로
            headers = list(data[0].keys())
            rows = [headers] + [[str(item.get(h, '')) for h in headers] for item in data]
        else:
            rows = data
    else:
        print_color(f"❌ 지원하지 않는 JSON 형식", Colors.RED)
        sys.exit(1)

    # 탭 선택 또는 생성
    if args.tab:
        try:
            worksheet = spreadsheet.worksheet(args.tab)
        except:
            # 탭이 없으면 생성
            worksheet = spreadsheet.add_worksheet(
                title=args.tab,
                rows=len(rows)+10,
                cols=len(rows[0]) if rows else 10
            )
            print_color(f"✅ 새 탭 생성: {args.tab}", Colors.GREEN)
    else:
        worksheet = spreadsheet.sheet1

    # 데이터 쓰기
    if rows:
        worksheet.clear()
        worksheet.update(f'A1:{chr(64+len(rows[0]))}{len(rows)}', rows)

    result = {
        "status": "success",
        "sheet_id": sheet_id,
        "tab": worksheet.title,
        "rows_written": len(rows),
        "timestamp": datetime.now().isoformat()
    }

    print_color(f"✅ 시트 업데이트 완료: {len(rows)}행", Colors.GREEN)
    print_json(result)
    return result


def cmd_update(args):
    """특정 셀 업데이트"""
    gc = get_credentials()
    sheet_id = extract_sheet_id(args.sheet_url)
    spreadsheet = gc.open_by_key(sheet_id)

    if args.tab:
        worksheet = spreadsheet.worksheet(args.tab)
    else:
        worksheet = spreadsheet.sheet1

    worksheet.update(args.cell, args.value)

    result = {
        "status": "success",
        "sheet_id": sheet_id,
        "tab": worksheet.title,
        "cell": args.cell,
        "value": args.value,
        "timestamp": datetime.now().isoformat()
    }

    print_color(f"✅ 셀 업데이트: {args.cell} = {args.value}", Colors.GREEN)
    print_json(result)
    return result


def cmd_append(args):
    """행 추가 (기존 데이터 뒤에)"""
    gc = get_credentials()
    sheet_id = extract_sheet_id(args.sheet_url)
    spreadsheet = gc.open_by_key(sheet_id)

    if args.tab:
        try:
            worksheet = spreadsheet.worksheet(args.tab)
        except:
            worksheet = spreadsheet.add_worksheet(title=args.tab, rows=100, cols=26)
    else:
        worksheet = spreadsheet.sheet1

    # JSON 파일에서 데이터 로드
    with open(args.json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 리스트 형태로 변환
    if isinstance(data, dict):
        if 'rows' in data:
            rows = data['rows']
        else:
            rows = [[str(v) for v in data.values()]]
    elif isinstance(data, list):
        if data and isinstance(data[0], dict):
            rows = [[str(v) for v in item.values()] for item in data]
        else:
            rows = data if isinstance(data[0], list) else [data]
    else:
        rows = [[str(data)]]

    # 기존 데이터 끝에 추가
    for row in rows:
        worksheet.append_row(row)

    result = {
        "status": "success",
        "sheet_id": sheet_id,
        "tab": worksheet.title,
        "rows_appended": len(rows),
        "timestamp": datetime.now().isoformat()
    }

    print_color(f"✅ {len(rows)}행 추가 완료", Colors.GREEN)
    print_json(result)
    return result


def cmd_create_tab(args):
    """새 탭 생성"""
    gc = get_credentials()
    sheet_id = extract_sheet_id(args.sheet_url)
    spreadsheet = gc.open_by_key(sheet_id)

    try:
        worksheet = spreadsheet.add_worksheet(
            title=args.name,
            rows=args.rows,
            cols=args.cols
        )

        result = {
            "status": "success",
            "sheet_id": sheet_id,
            "tab_created": args.name,
            "rows": args.rows,
            "cols": args.cols
        }

        print_color(f"✅ 새 탭 생성: {args.name}", Colors.GREEN)
        print_json(result)
        return result

    except Exception as e:
        print_color(f"❌ 탭 생성 실패: {e}", Colors.RED)
        sys.exit(1)


def cmd_list_tabs(args):
    """탭 목록 조회"""
    gc = get_credentials()
    sheet_id = extract_sheet_id(args.sheet_url)
    spreadsheet = gc.open_by_key(sheet_id)

    tabs = []
    for ws in spreadsheet.worksheets():
        tabs.append({
            "title": ws.title,
            "id": ws.id,
            "row_count": ws.row_count,
            "col_count": ws.col_count
        })

    result = {
        "sheet_id": sheet_id,
        "sheet_title": spreadsheet.title,
        "tab_count": len(tabs),
        "tabs": tabs
    }

    print_json(result)
    return result


def main():
    parser = argparse.ArgumentParser(description='Google Sheets API Handler')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # read 명령
    read_parser = subparsers.add_parser('read', help='시트 읽기')
    read_parser.add_argument('sheet_url', help='구글 시트 URL')
    read_parser.add_argument('--tab', help='탭 이름 (기본: 첫 번째 탭)')
    read_parser.add_argument('--range', help='셀 범위 (예: A1:B10)')

    # write 명령
    write_parser = subparsers.add_parser('write', help='시트 쓰기 (JSON에서)')
    write_parser.add_argument('sheet_url', help='구글 시트 URL')
    write_parser.add_argument('json_file', help='JSON 데이터 파일 경로')
    write_parser.add_argument('--tab', help='탭 이름 (없으면 생성)')

    # update 명령
    update_parser = subparsers.add_parser('update', help='특정 셀 업데이트')
    update_parser.add_argument('sheet_url', help='구글 시트 URL')
    update_parser.add_argument('--tab', help='탭 이름')
    update_parser.add_argument('--cell', required=True, help='셀 주소 (예: A1)')
    update_parser.add_argument('--value', required=True, help='새 값')

    # append 명령
    append_parser = subparsers.add_parser('append', help='행 추가')
    append_parser.add_argument('sheet_url', help='구글 시트 URL')
    append_parser.add_argument('json_file', help='JSON 데이터 파일 경로')
    append_parser.add_argument('--tab', help='탭 이름')

    # create-tab 명령
    create_tab_parser = subparsers.add_parser('create-tab', help='새 탭 생성')
    create_tab_parser.add_argument('sheet_url', help='구글 시트 URL')
    create_tab_parser.add_argument('--name', required=True, help='탭 이름')
    create_tab_parser.add_argument('--rows', type=int, default=100, help='행 수 (기본: 100)')
    create_tab_parser.add_argument('--cols', type=int, default=26, help='열 수 (기본: 26)')

    # list-tabs 명령
    list_tabs_parser = subparsers.add_parser('list-tabs', help='탭 목록 조회')
    list_tabs_parser.add_argument('sheet_url', help='구글 시트 URL')

    args = parser.parse_args()

    try:
        if args.command == 'read':
            cmd_read(args)
        elif args.command == 'write':
            cmd_write(args)
        elif args.command == 'update':
            cmd_update(args)
        elif args.command == 'append':
            cmd_append(args)
        elif args.command == 'create-tab':
            cmd_create_tab(args)
        elif args.command == 'list-tabs':
            cmd_list_tabs(args)
    except ImportError:
        print_color("❌ 필요한 패키지가 없습니다", Colors.RED)
        print("pip install gspread google-auth-oauthlib google-auth")
        sys.exit(1)
    except Exception as e:
        print_color(f"❌ 오류: {e}", Colors.RED)
        sys.exit(1)


if __name__ == "__main__":
    main()
