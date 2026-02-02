#!/usr/bin/env python3
"""
네이버 키워드 분석 도구 - Streamlit v3
- 키워드 분석 (검색광고 API)
- 트렌드 분석 (데이터랩 API)

실행: streamlit run app.py
"""

import os
import json
import time
import hmac
import hashlib
import base64
import urllib.request
import urllib.parse
import urllib.error
import pandas as pd
import streamlit as st
import altair as alt
from datetime import datetime, timedelta
from pathlib import Path

# .env 로드
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / 'gsheet-handler' / 'scripts' / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    alt_path = Path('/Users/seoni/imi-workspace/.claude/skills/gsheet-handler/scripts/.env')
    load_dotenv(alt_path)

# API 설정
NAVER_AD_ACCESS_LICENSE = os.getenv('NAVER_AD_ACCESS_LICENSE')
NAVER_AD_SECRET_KEY = os.getenv('NAVER_AD_SECRET_KEY')
NAVER_AD_CUSTOMER_ID = os.getenv('NAVER_AD_CUSTOMER_ID')
NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET')

# 디자인 시스템 컬러 (DESIGN_GUIDE.md)
COLORS = {
    'bg': '#F0EFEA',           # Background
    'primary': '#1a1a1a',       # Primary (헤더, 사이드바, 텍스트)
    'accent': '#6366F1',        # Accent (CTA, 활성 상태)
    'success': '#10B981',       # Success (긍정 지표)
    'accent_hover': '#4F46E5',  # Accent hover
}

# 사용자 데이터 파일 경로
USER_DATA_PATH = Path(__file__).parent / 'user_data.json'

def load_user_data():
    """저장된 사용자 정보 로드"""
    if USER_DATA_PATH.exists():
        try:
            with open(USER_DATA_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None

def save_user_data(user_profile):
    """사용자 정보 저장"""
    try:
        with open(USER_DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(user_profile, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

# 차트 컬러
CHART_COLORS = ['#6366F1', '#10B981', '#F59E0B', '#EF4444']

# SVG 아이콘 (흰색)
ICONS = {
    'link': '''<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>''',
    'trend': '''<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>''',
    'chart': '''<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>''',
    'menu': '''<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>''',
    'close': '''<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>''',
    'panel_left': '''<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="3" x2="9" y2="21"/></svg>''',
    'panel_left_close': '''<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="3" x2="9" y2="21"/><polyline points="16 8 12 12 16 16"/></svg>''',
}

# ===== 검색광고 API =====
def generate_signature(timestamp, method, uri):
    message = f"{timestamp}.{method}.{uri}"
    signature = hmac.new(
        NAVER_AD_SECRET_KEY.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode('utf-8')


def api_request(method, uri, params=None, body=None):
    """네이버 검색광고 API 공통 요청 함수"""
    if not all([NAVER_AD_ACCESS_LICENSE, NAVER_AD_SECRET_KEY, NAVER_AD_CUSTOMER_ID]):
        st.error("검색광고 API 키가 설정되지 않았습니다.")
        return None

    timestamp = str(int(time.time() * 1000))
    signature = generate_signature(timestamp, method, uri)

    headers = {
        'X-Timestamp': timestamp,
        'X-API-KEY': NAVER_AD_ACCESS_LICENSE,
        'X-Customer': NAVER_AD_CUSTOMER_ID,
        'X-Signature': signature,
        'Content-Type': 'application/json'
    }

    url = "https://api.searchad.naver.com" + uri
    if params and method == 'GET':
        url += '?' + urllib.parse.urlencode(params)

    request = urllib.request.Request(url, method=method, headers=headers)
    if body:
        request.data = json.dumps(body).encode('utf-8')

    try:
        response = urllib.request.urlopen(request)
        return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        st.error(f"API 오류: {e.code}")
        return None


def get_campaigns():
    """캠페인 목록 조회"""
    return api_request('GET', '/ncc/campaigns')


def get_adgroups(campaign_id=None):
    """광고그룹 목록 조회"""
    if campaign_id:
        return api_request('GET', '/ncc/adgroups', {'nccCampaignId': campaign_id})
    return api_request('GET', '/ncc/adgroups')


def get_ad_keywords(adgroup_id):
    """광고 키워드 목록 조회"""
    return api_request('GET', '/ncc/keywords', {'nccAdgroupId': adgroup_id})


def get_stat_report(ids, fields, date_preset='LAST_7_DAYS', start_date=None, end_date=None):
    """통계 리포트 조회

    Args:
        ids: 조회할 ID 목록 (캠페인, 광고그룹, 키워드 등)
        fields: 조회할 필드 (impCnt, clkCnt, salesAmt, ctr, cpc, avgRnk 등)
        date_preset: TODAY, YESTERDAY, LAST_7_DAYS, LAST_14_DAYS, LAST_30_DAYS
        start_date: 직접 지정 시 시작일 (YYYY-MM-DD)
        end_date: 직접 지정 시 종료일 (YYYY-MM-DD)
    """
    if not all([NAVER_AD_ACCESS_LICENSE, NAVER_AD_SECRET_KEY, NAVER_AD_CUSTOMER_ID]):
        return None

    timestamp = str(int(time.time() * 1000))
    uri = "/stats"
    signature = generate_signature(timestamp, 'POST', uri)

    headers = {
        'X-Timestamp': timestamp,
        'X-API-KEY': NAVER_AD_ACCESS_LICENSE,
        'X-Customer': NAVER_AD_CUSTOMER_ID,
        'X-Signature': signature,
        'Content-Type': 'application/json'
    }

    body = {
        "ids": ids if isinstance(ids, list) else [ids],
        "fields": fields,
        "timeIncrement": "allDays"  # 일별 데이터
    }

    if start_date and end_date:
        body["datePreset"] = "CUSTOM"
        body["since"] = start_date
        body["until"] = end_date
    else:
        body["datePreset"] = date_preset

    url = "https://api.searchad.naver.com" + uri
    request = urllib.request.Request(url, method='POST', headers=headers)
    request.data = json.dumps(body).encode('utf-8')

    try:
        response = urllib.request.urlopen(request)
        return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        st.error(f"통계 API 오류: {e.code} - {error_body}")
        return None


def get_daily_stats(campaign_id, days=7):
    """캠페인의 일별 통계 데이터 조회"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # 일별 데이터를 위해 각 날짜별로 조회
    daily_data = []

    for i in range(days):
        date = end_date - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')

        result = get_stat_report(
            ids=[campaign_id],
            fields=["impCnt", "clkCnt", "salesAmt", "ctr"],
            start_date=date_str,
            end_date=date_str
        )

        if result and isinstance(result, list) and len(result) > 0:
            stat = result[0]
            daily_data.append({
                '날짜': date,
                '노출수': stat.get('impCnt', 0),
                '클릭수': stat.get('clkCnt', 0),
                '비용': stat.get('salesAmt', 0),
                'CTR': stat.get('ctr', 0)
            })
        else:
            # 데이터가 없는 경우 0으로 채움
            daily_data.append({
                '날짜': date,
                '노출수': 0,
                '클릭수': 0,
                '비용': 0,
                'CTR': 0
            })

    # 날짜순 정렬
    daily_data.sort(key=lambda x: x['날짜'])
    return daily_data


def get_bizmoney():
    """비즈머니(잔액) 조회"""
    return api_request('GET', '/billing/bizmoney')


def get_keyword_stats(keywords, include_related=False):
    if not all([NAVER_AD_ACCESS_LICENSE, NAVER_AD_SECRET_KEY, NAVER_AD_CUSTOMER_ID]):
        st.error("검색광고 API 키가 설정되지 않았습니다.")
        return None

    timestamp = str(int(time.time() * 1000))
    uri = "/keywordstool"
    signature = generate_signature(timestamp, 'GET', uri)

    headers = {
        'X-Timestamp': timestamp,
        'X-API-KEY': NAVER_AD_ACCESS_LICENSE,
        'X-Customer': NAVER_AD_CUSTOMER_ID,
        'X-Signature': signature,
        'Content-Type': 'application/json'
    }

    params = {
        'hintKeywords': ','.join(keywords) if isinstance(keywords, list) else keywords,
        'showDetail': '1'
    }
    if include_related:
        params['includeHintKeywords'] = '1'

    url = "https://api.searchad.naver.com" + uri + '?' + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, method='GET', headers=headers)

    try:
        response = urllib.request.urlopen(request)
        return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        st.error(f"API 오류: {e.code}")
        return None


# ===== 데이터랩 API =====
def get_trend(keywords, days=30, time_unit='date', device='', gender='', ages=[], custom_dates=None):
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        st.error("데이터랩 API 키가 설정되지 않았습니다.")
        return None

    url = "https://openapi.naver.com/v1/datalab/search"

    if custom_dates:
        start_date, end_date = custom_dates
    else:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(',')]

    keyword_groups = []
    for kw in keywords[:5]:
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

    # 디버깅: API 요청 정보 표시
    st.info(f"📡 API 요청: {body['startDate']} ~ {body['endDate']} | 단위: {time_unit} | 키워드: {[kg['groupName'] for kg in keyword_groups]}")

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", NAVER_CLIENT_ID)
    request.add_header("X-Naver-Client-Secret", NAVER_CLIENT_SECRET)
    request.add_header("Content-Type", "application/json")

    try:
        response = urllib.request.urlopen(request, data=json.dumps(body).encode("utf-8"))
        result = json.loads(response.read().decode("utf-8"))
        # 디버깅: 최고점 날짜 확인
        if result and 'results' in result:
            for group in result['results']:
                max_point = max(group['data'], key=lambda x: x['ratio'])
                st.caption(f"🔍 {group['title']}: 최고점 {max_point['period']} (지수: {max_point['ratio']})")
        return result
    except urllib.error.HTTPError as e:
        st.error(f"API 오류: {e.code}")
        return None


# ===== 유틸리티 =====
def parse_volume(value):
    if isinstance(value, str):
        return 10 if '< 10' in value else int(value.replace(',', ''))
    return value or 0


def normalize_competition(comp):
    if not comp or comp == '-':
        return '낮음'
    comp = str(comp).strip()
    mapping = {
        'HIGH': '높음', 'high': '높음', '높음': '높음',
        'MEDIUM': '중간', 'medium': '중간', '중간': '중간', '보통': '중간',
        'LOW': '낮음', 'low': '낮음', '낮음': '낮음',
    }
    return mapping.get(comp, '낮음')


def format_keyword_results(api_result):
    if not api_result or 'keywordList' not in api_result:
        return pd.DataFrame()

    data = []
    for kw in api_result['keywordList']:
        pc_qc = parse_volume(kw.get('monthlyPcQcCnt', 0))
        mo_qc = parse_volume(kw.get('monthlyMobileQcCnt', 0))
        total = pc_qc + mo_qc

        data.append({
            '연관키워드': kw.get('relKeyword', ''),
            'PC': pc_qc,
            '모바일': mo_qc,
            'PC_클릭': round(float(kw.get('monthlyAvePcClkCnt', 0) or 0), 1),
            '모바일_클릭': round(float(kw.get('monthlyAveMobileClkCnt', 0) or 0), 1),
            'PC_CTR': round(float(kw.get('monthlyAvePcCtr', 0) or 0), 2),
            '모바일_CTR': round(float(kw.get('monthlyAveMobileCtr', 0) or 0), 2),
            '경쟁정도': normalize_competition(kw.get('compIdx')),
            '광고수': int(float(kw.get('plAvgDepth', 0) or 0)),
            '_총검색량': total,
        })

    df = pd.DataFrame(data)
    df = df.sort_values(by='_총검색량', ascending=False, ignore_index=True)
    return df


def format_trend_results(api_result):
    if not api_result or 'results' not in api_result:
        return pd.DataFrame()

    data = []
    for group in api_result['results']:
        keyword = group['title']
        for point in group['data']:
            data.append({
                '키워드': keyword,
                '날짜': point['period'],
                '검색지수': point['ratio']
            })

    df = pd.DataFrame(data)
    if len(df) > 0:
        # 날짜를 datetime으로 변환하고 정렬
        df['날짜'] = pd.to_datetime(df['날짜'])
        df = df.sort_values(by='날짜')
    return df


# ===== 페이지 설정 =====
st.set_page_config(
    page_title="키워드 분석 도구",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== 온보딩 및 사이드바 상태 관리 =====
# 저장된 사용자 정보 확인 (영구 저장)
saved_user = load_user_data()
if 'onboarding_complete' not in st.session_state:
    # 저장된 사용자 정보가 있으면 온보딩 완료 상태로
    st.session_state.onboarding_complete = saved_user is not None
if 'user_profile' not in st.session_state:
    if saved_user:
        st.session_state.user_profile = saved_user
    else:
        st.session_state.user_profile = {
            'name': '',
            'occupation': '',
            'role': '',
            'age_group': ''
        }
if 'sidebar_expanded' not in st.session_state:
    st.session_state.sidebar_expanded = True

# CSS 스타일 (DESIGN_GUIDE.md 기반)
st.markdown(f"""
<style>
    /* === Global === */
    .main > div {{ padding-top: 1rem; }}
    .stApp {{ background-color: {COLORS['bg']}; }}

    /* Hide branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header[data-testid="stHeader"] {{
        background: transparent !important;
        visibility: hidden;
    }}

    /* 달력 요일 헤더 한글화 */
    [data-baseweb="calendar"] [role="columnheader"] {{
        font-size: 0 !important;
    }}
    [data-baseweb="calendar"] [role="columnheader"]:nth-child(1)::after {{ content: "일"; font-size: 14px; }}
    [data-baseweb="calendar"] [role="columnheader"]:nth-child(2)::after {{ content: "월"; font-size: 14px; }}
    [data-baseweb="calendar"] [role="columnheader"]:nth-child(3)::after {{ content: "화"; font-size: 14px; }}
    [data-baseweb="calendar"] [role="columnheader"]:nth-child(4)::after {{ content: "수"; font-size: 14px; }}
    [data-baseweb="calendar"] [role="columnheader"]:nth-child(5)::after {{ content: "목"; font-size: 14px; }}
    [data-baseweb="calendar"] [role="columnheader"]:nth-child(6)::after {{ content: "금"; font-size: 14px; }}
    [data-baseweb="calendar"] [role="columnheader"]:nth-child(7)::after {{ content: "토"; font-size: 14px; }}

    /* === Sidebar === */
    [data-testid="stSidebar"] {{
        background-color: {COLORS['primary']};
    }}
    [data-testid="stSidebar"] > div > div > div {{
        color: white;
    }}
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {{
        color: rgba(255, 255, 255, 0.7) !important;
    }}

    /* 드롭다운 메뉴 */
    [data-baseweb="popover"] [data-baseweb="menu"] {{
        background-color: white !important;
    }}
    [data-baseweb="popover"] li {{
        color: {COLORS['primary']} !important;
    }}
    [data-baseweb="popover"] li:hover {{
        background-color: rgba(99, 102, 241, 0.1) !important;
    }}

    /* 사이드바 입력 필드 */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] span,
    [data-testid="stSidebar"] [data-baseweb="input"] input {{
        color: {COLORS['primary']} !important;
        background-color: white !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="select"] div,
    [data-testid="stSidebar"] [data-baseweb="select"] svg {{
        color: {COLORS['primary']} !important;
    }}

    /* Multiselect 태그 */
    [data-testid="stSidebar"] [data-baseweb="tag"] {{
        background-color: {COLORS['accent']} !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="tag"] span {{
        color: white !important;
    }}

    /* Checkbox */
    [data-testid="stSidebar"] .stCheckbox label span {{
        color: rgba(255, 255, 255, 0.7) !important;
    }}

    /* Date input */
    [data-testid="stSidebar"] [data-baseweb="input"] {{
        background-color: white !important;
    }}
    [data-testid="stSidebar"] .stDateInput input {{
        color: {COLORS['primary']} !important;
    }}
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stTextInput label {{
        color: rgba(255, 255, 255, 0.7) !important;
    }}

    /* === Metrics === */
    [data-testid="stMetricValue"] {{
        font-size: 32px;
        font-weight: 300;
    }}
    [data-testid="stMetricLabel"] {{
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: rgba(26, 26, 26, 0.6);
    }}

    /* === Buttons === */
    .stButton button {{
        background-color: {COLORS['accent']};
        color: white;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: 500;
        border: none;
        transition: all 0.2s;
    }}
    .stButton button:hover {{
        background-color: {COLORS['accent_hover']};
        transform: translateY(-1px);
    }}
    .stButton button[kind="secondary"] {{
        background-color: transparent;
        border: 1px solid {COLORS['primary']};
        color: {COLORS['primary']};
    }}
    .stButton button[kind="secondary"]:hover {{
        background-color: {COLORS['primary']};
        color: white;
    }}

    /* === Input === */
    .stTextInput input, .stSelectbox select {{
        border: 1px solid rgba(0, 0, 0, 0.1);
        border-radius: 6px;
    }}
    .stTextInput input:focus, .stSelectbox select:focus {{
        border-color: {COLORS['accent']};
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }}

    /* === Cards === */
    .header-box {{
        background: transparent;
        border: 1px solid rgba(0, 0, 0, 0.06);
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 20px;
    }}
    .result-box {{
        background: transparent;
        border: 1px solid rgba(0, 0, 0, 0.06);
        border-radius: 8px;
        padding: 24px;
    }}
    .selected-box {{
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid {COLORS['accent']};
        border-radius: 8px;
        padding: 16px;
        margin-top: 16px;
    }}

    /* Card hover effect */
    .stat-card {{
        background: transparent;
        padding: 24px;
        border-radius: 8px;
        border: 1px solid rgba(0, 0, 0, 0.06);
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    .stat-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
    }}

    /* === Tables === */
    .header-table {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 8px;
    }}
    .header-table th {{
        background: {COLORS['bg']};
        border: 1px solid rgba(0, 0, 0, 0.06);
        padding: 12px;
        text-align: center;
        font-size: 12px;
        font-weight: 600;
        color: rgba(26, 26, 26, 0.6);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .header-table .group-header {{
        background: rgba(99, 102, 241, 0.08);
    }}

    /* DataFrame */
    .dataframe thead th {{
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: rgba(26, 26, 26, 0.6);
    }}
    .dataframe tbody tr:hover {{
        background: rgba(99, 102, 241, 0.02);
    }}

    /* === Badge === */
    .badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;
    }}
    .badge-success {{
        background: rgba(16, 185, 129, 0.1);
        color: {COLORS['success']};
    }}
    .badge-accent {{
        background: rgba(99, 102, 241, 0.1);
        color: {COLORS['accent']};
    }}
</style>
""", unsafe_allow_html=True)

# ===== 온보딩 페이지 =====
if not st.session_state.onboarding_complete:
    # 온보딩 CSS
    st.markdown(f"""
    <style>
        /* 온보딩 전용 스타일 */
        .onboarding-container {{
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 48px 24px;
        }}

        .hello-section {{
            text-align: center;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            position: relative;
            padding-bottom: 25vh;
        }}

        .hello-text {{
            font-size: 180px;
            font-weight: 700;
            color: #1a1a1a;
            letter-spacing: -6px;
            animation: fadeInUp 1s ease-out;
            transition: color 0.3s ease;
            cursor: default;
        }}

        .hello-text:hover {{
            color: #888888;
        }}

        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .hello-subtitle {{
            font-size: 28px;
            color: rgba(26, 26, 26, 0.6);
            margin-top: 24px;
            animation: fadeInUp 1s ease-out 0.3s both;
        }}

        .setup-section {{
            max-width: 400px;
            width: 100%;
            animation: fadeInUp 1s ease-out 0.6s both;
        }}

        /* 스크롤 인터랙션 - 폼 영역 (CSS scroll-driven animation) */
        @keyframes growOnScroll {{
            from {{
                transform: scale(0.7) translateY(80px);
                opacity: 0;
            }}
            to {{
                transform: scale(1) translateY(0);
                opacity: 1;
            }}
        }}

        .scroll-grow-container {{
            animation: growOnScroll linear both;
            animation-timeline: view();
            animation-range: entry 0% cover 40%;
            transform-origin: center top;
        }}

        /* 폴백 - scroll-timeline 미지원 브라우저 */
        @supports not (animation-timeline: view()) {{
            .scroll-grow-container {{
                animation: fadeInUp 0.8s ease-out 0.5s both;
            }}
        }}

        .setup-title {{
            font-size: 24px;
            font-weight: 500;
            color: {COLORS['primary']};
            text-align: center;
            margin-bottom: 8px;
        }}

        .setup-subtitle {{
            font-size: 14px;
            color: rgba(26, 26, 26, 0.6);
            text-align: center;
            margin-bottom: 32px;
        }}

        .setup-form {{
            background: transparent;
            padding: 0;
            border: none;
            box-shadow: none;
            /* 스크롤 인터랙션 */
            animation: growOnScroll linear both;
            animation-timeline: view();
            animation-range: entry 0% cover 50%;
            transform-origin: center top;
        }}

        /* 폴백 - scroll-timeline 미지원 브라우저 */
        @supports not (animation-timeline: view()) {{
            .setup-form {{
                animation: fadeInUp 0.8s ease-out 0.8s both;
            }}
        }}

        /* 모던 입력 필드 스타일 */
        .setup-form .stTextInput > div > div,
        .setup-form .stSelectbox > div > div {{
            background: transparent !important;
            border: none !important;
            border-bottom: 1px solid rgba(26, 26, 26, 0.15) !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            padding: 8px 0 !important;
        }}

        .setup-form .stTextInput input,
        .setup-form .stSelectbox [data-baseweb="select"] {{
            background: transparent !important;
            border: none !important;
            padding-left: 0 !important;
            font-size: 16px !important;
        }}

        .setup-form .stTextInput input:focus {{
            box-shadow: none !important;
            border-bottom: 2px solid #1a1a1a !important;
        }}

        .setup-form label {{
            font-size: 13px !important;
            font-weight: 500 !important;
            color: rgba(26, 26, 26, 0.5) !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
        }}

        .setup-form .stTextInput,
        .setup-form .stSelectbox {{
            margin-bottom: 32px !important;
        }}

        /* 버튼 스타일 */
        .setup-form .stButton > button,
        .setup-form .stButton button[kind="primary"],
        .setup-form .stButton button[kind="secondary"],
        .setup-form div[data-testid="stButton"] button {{
            background: #1a1a1a !important;
            background-color: #1a1a1a !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 12px 32px !important;
            font-weight: 500 !important;
            margin-top: 24px !important;
            transition: background 0.2s ease !important;
        }}

        .setup-form .stButton > button:hover,
        .setup-form .stButton button:hover,
        .setup-form div[data-testid="stButton"] button:hover {{
            background: #6366F1 !important;
            background-color: #6366F1 !important;
        }}

        /* 건너뛰기 버튼 */
        .setup-form .stButton:last-child button {{
            background: transparent !important;
            color: rgba(26, 26, 26, 0.4) !important;
            margin-top: 8px !important;
        }}

        .setup-form .stButton:last-child button:hover {{
            color: #1a1a1a !important;
            background: transparent !important;
        }}

        .scroll-indicator {{
            position: fixed;
            bottom: 40px;
            left: 50%;
            transform: translateX(-50%);
            animation: bounce 2s infinite;
            z-index: 100;
            color: rgba(26, 26, 26, 0.3);
        }}

        @keyframes bounce {{
            0%, 20%, 50%, 80%, 100% {{ transform: translateX(-50%) translateY(0); }}
            40% {{ transform: translateX(-50%) translateY(-10px); }}
            60% {{ transform: translateX(-50%) translateY(-5px); }}
        }}

        /* 온보딩 시 사이드바 최소화 */
        [data-testid="stSidebar"] {{
            width: 0 !important;
            min-width: 0 !important;
            transform: translateX(-100%) !important;
        }}
        [data-testid="collapsedControl"] {{
            opacity: 0 !important;
            pointer-events: none !important;
        }}
    </style>
    """, unsafe_allow_html=True)

    # 로고 (왼쪽 상단)
    st.markdown("""
    <div class="logo-section" style="
        position: fixed;
        top: 24px;
        left: 32px;
        z-index: 1000;
        animation: fadeInUp 0.8s ease-out;
    ">
        <div style="
            display: flex;
            align-items: center;
            gap: 8px;
        ">
            <svg width="32" height="32" viewBox="0 0 40 40" fill="none">
                <circle cx="20" cy="20" r="18" fill="#1a1a1a"/>
                <path d="M12 20C12 15.5817 15.5817 12 20 12C24.4183 12 28 15.5817 28 20" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
                <circle cx="20" cy="20" r="4" fill="white"/>
                <path d="M20 24V28" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
            </svg>
            <span style="
                font-size: 18px;
                font-weight: 600;
                color: #1a1a1a;
                letter-spacing: -0.5px;
            ">Aha AI</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Hello 섹션 (전체 화면)
    st.markdown("""
    <div class="hello-section">
        <div class="hello-text">Hello.</div>
        <div class="hello-subtitle">마케터를 위한 올인원 AI 업무플로우입니다.</div>
        <div class="scroll-indicator">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 5v14M19 12l-7 7-7-7"/>
            </svg>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 설정 섹션 (스크롤 후) - CSS scroll-driven animation 적용
    st.markdown("""
    <div id="setup-grow-section" class="scroll-grow-container" style="padding-top: 80px; padding-bottom: 40px;">
        <div class="setup-title">몇 가지 설정이 필요해요</div>
        <div class="setup-subtitle">더 나은 서비스를 위해 간단한 정보를 입력해주세요</div>
    </div>
    """, unsafe_allow_html=True)

    # 입력 폼
    with st.container():
        col_left, col_center, col_right = st.columns([1, 2, 1])

        with col_center:
            st.markdown('<div class="setup-form">', unsafe_allow_html=True)

            # 이름
            user_name = st.text_input(
                "이름",
                placeholder="홍길동",
                key="onboard_name"
            )

            # 직업
            user_occupation = st.selectbox(
                "직업",
                options=['', '마케터', '기획자', '개발자', '디자이너', '사업가', '학생', '프리랜서', '기타'],
                key="onboard_occupation"
            )

            # 직무
            user_role = st.text_input(
                "직무 / 담당 업무",
                placeholder="퍼포먼스 마케팅, 브랜드 마케팅 등",
                key="onboard_role"
            )

            # 연령대
            user_age = st.selectbox(
                "연령대",
                options=['', '20대', '30대', '40대', '50대 이상'],
                key="onboard_age"
            )

            st.markdown("")

            # 시작하기 버튼
            if st.button("시작하기", type="primary", use_container_width=True, key="start_btn"):
                if user_name.strip():
                    user_profile = {
                        'name': user_name,
                        'occupation': user_occupation,
                        'role': user_role,
                        'age_group': user_age
                    }
                    st.session_state.user_profile = user_profile
                    st.session_state.onboarding_complete = True
                    # 파일에 영구 저장
                    save_user_data(user_profile)
                    st.rerun()
                else:
                    st.warning("이름을 입력해주세요")

            # 건너뛰기
            if st.button("건너뛰기", use_container_width=True, key="skip_btn"):
                # 건너뛰기도 기본 프로필로 저장
                default_profile = {'name': 'Guest', 'occupation': '', 'role': '', 'age_group': ''}
                st.session_state.user_profile = default_profile
                st.session_state.onboarding_complete = True
                save_user_data(default_profile)
                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# ===== 사이드바 표시 (온보딩 완료 후) =====
sidebar_width = "280px" if st.session_state.sidebar_expanded else "72px"

st.markdown(f"""
<style>
    /* 사이드바 크기 조절 */
    [data-testid="stSidebar"] {{
        width: {sidebar_width} !important;
        min-width: {sidebar_width} !important;
        max-width: {sidebar_width} !important;
        transform: translateX(0) !important;
        display: block !important;
        visibility: visible !important;
        transition: width 0.3s ease, min-width 0.3s ease, max-width 0.3s ease !important;
    }}

    [data-testid="stSidebar"] > div:first-child {{
        width: {sidebar_width} !important;
        transition: width 0.3s ease !important;
    }}

    /* Streamlit 기본 토글 버튼 숨기기 */
    [data-testid="collapsedControl"] {{
        display: none !important;
    }}

    /* Streamlit 사이드바 닫기 버튼(X) 숨기기 */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="baseButton-header"],
    button[kind="header"] {{
        display: none !important;
    }}

    /* 커스텀 토글 버튼 */
    .sidebar-toggle {{
        position: fixed;
        top: 16px;
        left: calc({sidebar_width} + 16px);
        z-index: 1000;
        background: {COLORS['primary']};
        border: none;
        border-radius: 8px;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        color: white;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }}
    .sidebar-toggle:hover {{
        background: {COLORS['accent']};
        transform: scale(1.05);
    }}
    .sidebar-toggle svg {{
        stroke: white;
    }}
</style>
""", unsafe_allow_html=True)

# ===== 사이드바 =====
is_expanded = st.session_state.sidebar_expanded

with st.sidebar:
    # 사이드바 스타일
    nav_padding = "12px 16px" if is_expanded else "12px"
    nav_justify = "flex-start" if is_expanded else "center"
    toggle_justify = "flex-end" if is_expanded else "center"
    toggle_padding = "16px" if is_expanded else "8px"

    st.markdown(f"""
    <style>
        /* 사이드바 기본 스타일 */
        [data-testid="stSidebar"] {{
            background-color: {COLORS['primary']} !important;
            padding-top: 1rem;
        }}
        [data-testid="stSidebar"] > div:first-child {{
            background-color: {COLORS['primary']} !important;
        }}
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
            color: rgba(255, 255, 255, 0.7) !important;
        }}
        [data-testid="stSidebar"] label {{
            color: rgba(255, 255, 255, 0.7) !important;
        }}
        [data-testid="stSidebar"] .stSelectbox label p,
        [data-testid="stSidebar"] .stTextInput label p,
        [data-testid="stSidebar"] .stMultiSelect label p {{
            color: rgba(255,255,255,0.7) !important;
            font-size: 13px !important;
        }}
        .menu-header {{
            font-size: 11px;
            font-weight: 600;
            color: rgba(255,255,255,0.4) !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 0 8px;
            margin-bottom: 8px;
        }}
        .menu-divider {{
            border-top: 1px solid rgba(255,255,255,0.1);
            margin: 12px 8px;
        }}

        /* 토글 버튼 (확장 시 - 우측 정렬) */
        .toggle-btn-right {{
            display: flex;
            justify-content: flex-end;
            padding: 4px 8px;
        }}
        .toggle-btn-right button {{
            background: transparent !important;
            border: none !important;
            color: rgba(255, 255, 255, 0.6) !important;
            font-size: 24px !important;
            padding: 8px 12px !important;
            border-radius: 8px !important;
            min-height: 40px !important;
        }}
        .toggle-btn-right button:hover {{
            background: rgba(255, 255, 255, 0.08) !important;
            color: white !important;
        }}

        /* 토글 버튼 (축소 시 - 중앙 정렬) */
        .toggle-btn-center {{
            display: flex;
            justify-content: center;
            padding: 8px 0;
        }}
        .toggle-btn-center button {{
            background: transparent !important;
            border: none !important;
            color: rgba(255, 255, 255, 0.7) !important;
            font-size: 24px !important;
            padding: 10px !important;
            border-radius: 8px !important;
            min-height: 44px !important;
        }}
        .toggle-btn-center button:hover {{
            background: rgba(255, 255, 255, 0.08) !important;
            color: white !important;
        }}

        /* 네비게이션 버튼 래퍼 */
        .nav-wrapper {{
            position: relative;
            margin: 0 8px 4px 8px;
        }}

        /* SVG 아이콘 + 라벨 오버레이 */
        .nav-display {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: {nav_padding};
            border-radius: 8px;
            pointer-events: none;
            justify-content: {nav_justify};
        }}
        .nav-display svg {{
            stroke: rgba(255, 255, 255, 0.7);
            flex-shrink: 0;
        }}
        .nav-display span {{
            color: rgba(255, 255, 255, 0.7);
            font-size: 14px;
            font-weight: 400;
            white-space: nowrap;
        }}

        /* Streamlit 버튼 스타일 오버라이드 */
        [data-testid="stSidebar"] .stButton > button {{
            background: transparent !important;
            border: none !important;
            border-radius: 8px !important;
            color: rgba(255, 255, 255, 0.7) !important;
            text-align: left !important;
            padding: {nav_padding} !important;
            font-size: 14px !important;
            font-weight: 400 !important;
            transition: all 0.2s ease !important;
            justify-content: {nav_justify} !important;
            width: 100% !important;
        }}
        [data-testid="stSidebar"] .stButton > button:hover {{
            background: rgba(255, 255, 255, 0.08) !important;
            color: white !important;
        }}
        [data-testid="stSidebar"] .stButton > button:focus {{
            box-shadow: none !important;
        }}
        [data-testid="stSidebar"] .stButton > button[kind="primary"] {{
            background: rgba(99, 102, 241, 0.2) !important;
            color: white !important;
            font-weight: 500 !important;
        }}

        /* 아이콘 버튼 (축소 시) */
        .icon-btn {{
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 12px;
            margin: 4px 8px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .icon-btn:hover {{
            background: rgba(255, 255, 255, 0.08);
        }}
        .icon-btn[data-active="true"] {{
            background: rgba(99, 102, 241, 0.2);
        }}
        .icon-btn svg {{
            stroke: rgba(255, 255, 255, 0.7);
        }}
        .icon-btn:hover svg,
        .icon-btn[data-active="true"] svg {{
            stroke: white;
        }}

        /* 축소 시 버튼 스타일 */
        {"" if is_expanded else '''
        [data-testid="stSidebar"] .nav-wrapper + div .stButton > button {
            opacity: 0 !important;
            position: absolute !important;
            width: 56px !important;
            height: 44px !important;
            top: -44px !important;
            left: 8px !important;
            z-index: 10 !important;
        }
        [data-testid="stSidebar"] .nav-wrapper + div {
            height: 0 !important;
            overflow: visible !important;
        }
        '''}
    </style>
    """, unsafe_allow_html=True)

    # 토글 버튼
    if is_expanded:
        # 확장 시: 우측 정렬
        st.markdown('<div class="toggle-btn-right">', unsafe_allow_html=True)
        if st.button("⊟", key="toggle_sidebar", help="사이드바 접기"):
            st.session_state.sidebar_expanded = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # 축소 시: 중앙 정렬
        st.markdown('<div class="toggle-btn-center">', unsafe_allow_html=True)
        if st.button("⊞", key="toggle_sidebar", help="사이드바 펼치기"):
            st.session_state.sidebar_expanded = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="menu-divider"></div>', unsafe_allow_html=True)

    # 메뉴 선택 (session_state로 관리)
    if is_expanded:
        st.markdown('<p class="menu-header">NAVER</p>', unsafe_allow_html=True)
    if 'menu' not in st.session_state:
        st.session_state.menu = "연관키워드"

    # 메뉴 아이템 (SVG 아이콘 사용)
    menu_items = [
        ("연관키워드", "link"),
        ("트렌드 분석", "trend"),
        ("광고 현황", "chart")
    ]

    # 메뉴 버튼 생성 - st.columns로 아이콘과 버튼 배치
    for item, icon_key in menu_items:
        is_active = st.session_state.menu == item
        icon_svg = ICONS[icon_key]
        btn_type = "primary" if is_active else "secondary"

        if is_expanded:
            # 확장 시: 아이콘 + 텍스트
            col_icon, col_text = st.columns([1, 5])
            with col_icon:
                st.markdown(f'<div style="padding:8px 0; text-align:center;">{icon_svg}</div>', unsafe_allow_html=True)
            with col_text:
                if st.button(item, key=f"nav_{item}", use_container_width=True, type=btn_type):
                    st.session_state.menu = item
                    st.rerun()
        else:
            # 축소 시: 아이콘만 표시 (nav-wrapper로 감싸기)
            st.markdown(f'''
            <div class="nav-wrapper">
                <div class="icon-btn" data-active="{str(is_active).lower()}">
                    {icon_svg}
                </div>
            </div>
            ''', unsafe_allow_html=True)
            # 투명 버튼 오버레이
            if st.button(" ", key=f"nav_{item}", use_container_width=True):
                st.session_state.menu = item
                st.rerun()

    menu_clean = st.session_state.menu

    if is_expanded:
        st.markdown('<div class="menu-divider"></div>', unsafe_allow_html=True)

    # 트렌드 설정 (트렌드 메뉴 + 사이드바 확장 시에만)
    if menu_clean == "트렌드 분석" and is_expanded:
        st.markdown('<p class="menu-header">조회 설정</p>', unsafe_allow_html=True)

        trend_keywords = st.text_input(
            "키워드",
            placeholder="키워드1, 키워드2",
            help="쉼표로 구분 (최대 5개)"
        )

        col1, col2 = st.columns(2)
        with col1:
            period_option = st.selectbox(
                "기간",
                options=['1개월', '3개월', '1년', '직접입력'],
                index=0
            )
        with col2:
            time_unit = st.selectbox(
                "단위",
                options=['date', 'week', 'month'],
                format_func=lambda x: {'date': '일', 'week': '주', 'month': '월'}[x]
            )

        # 직접입력 선택 시 달력으로 날짜 선택
        if period_option == '직접입력':
            col_date1, col_date2 = st.columns(2)
            with col_date1:
                start_date = st.date_input(
                    "시작일",
                    value=datetime.now() - timedelta(days=30),
                    max_value=datetime.now()
                )
            with col_date2:
                end_date = st.date_input(
                    "종료일",
                    value=datetime.now(),
                    max_value=datetime.now()
                )
            period = (end_date - start_date).days
            custom_dates = (start_date, end_date)
        else:
            period_map = {'1개월': 30, '3개월': 90, '1년': 365}
            period = period_map[period_option]
            custom_dates = None

        st.markdown('<p class="menu-header">필터</p>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            device = st.selectbox(
                "선택",
                options=['', 'pc', 'mo'],
                format_func=lambda x: {'': '전체', 'pc': 'PC', 'mo': '모바일'}[x]
            )
        with col2:
            gender = st.selectbox(
                "성별",
                options=['', 'm', 'f'],
                format_func=lambda x: {'': '전체', 'm': '남', 'f': '여'}[x]
            )

        all_ages = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']
        age_options = {
            '1': '0-12', '2': '13-18', '3': '19-24', '4': '25-29',
            '5': '30-34', '6': '35-39', '7': '40-44', '8': '45-49',
            '9': '50-54', '10': '55-59', '11': '60+'
        }

        select_all_ages = st.checkbox("전체 연령 선택", value=False)

        if select_all_ages:
            ages = all_ages
            st.caption(f"선택됨: 모든 연령대 (11개)")
        else:
            ages = st.multiselect(
                "범위",
                options=all_ages,
                format_func=lambda x: age_options[x],
                placeholder="선택하세요"
            )

        st.markdown("")
        trend_btn = st.button("조회하기", type="primary", use_container_width=True)

    # ===== 개인설정 (하단 고정) =====
    if is_expanded:
        # 하단 여백 확보
        st.markdown('<div style="flex: 1;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="menu-divider"></div>', unsafe_allow_html=True)

        user_name = st.session_state.user_profile.get('name', '')
        user_role = st.session_state.user_profile.get('role', '')

        if user_name:
            st.markdown(f"""
            <div style="padding: 12px 8px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="width: 36px; height: 36px; background: {COLORS['accent']}; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 500; font-size: 14px;">
                        {user_name[0].upper() if user_name else '?'}
                    </div>
                    <div>
                        <div style="color: white; font-size: 14px; font-weight: 500;">{user_name}</div>
                        <div style="color: rgba(255,255,255,0.5); font-size: 12px;">{user_role if user_role else '마케터'}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ===== 메인 콘텐츠 =====

# 세션 상태
if 'results_df' not in st.session_state:
    st.session_state.results_df = None
if 'selected' not in st.session_state:
    st.session_state.selected = set()
if 'trend_df' not in st.session_state:
    st.session_state.trend_df = None
# 새로운 세션 상태: 히스토리 & 팝업
if 'keyword_history' not in st.session_state:
    st.session_state.keyword_history = []  # [{timestamp, keywords, analyzed}]
if 'auto_show_trend' not in st.session_state:
    st.session_state.auto_show_trend = False


# ===== 분석 팝업 (st.dialog 사용) =====
@st.dialog("📊 트렌드 분석 설정")
def show_analysis_dialog():
    """트렌드 분석 옵션 선택 팝업"""
    st.markdown(f"**{len(st.session_state.selected)}개 키워드**를 분석합니다.")
    st.caption(", ".join(list(st.session_state.selected)[:5]))

    st.markdown("---")

    # 분석 옵션
    st.markdown("**분석 옵션**")

    d_col1, d_col2 = st.columns(2)
    with d_col1:
        dialog_period_option = st.selectbox(
            "기간",
            options=['1개월', '3개월', '1년', '직접입력'],
            index=0,
            key="dialog_period"
        )
    with d_col2:
        dialog_unit = st.selectbox(
            "단위",
            options=['date', 'week', 'month'],
            format_func=lambda x: {'date': '일', 'week': '주', 'month': '월'}[x],
            key="dialog_unit"
        )

    # 직접입력 선택 시 날짜 선택
    if dialog_period_option == '직접입력':
        d_date1, d_date2 = st.columns(2)
        with d_date1:
            dialog_start_date = st.date_input(
                "시작일",
                value=datetime.now() - timedelta(days=30),
                max_value=datetime.now(),
                key="dialog_start_date"
            )
        with d_date2:
            dialog_end_date = st.date_input(
                "종료일",
                value=datetime.now(),
                max_value=datetime.now(),
                key="dialog_end_date"
            )
        dialog_custom_dates = (dialog_start_date, dialog_end_date)
        dialog_period = dialog_period_option
    else:
        dialog_custom_dates = None
        dialog_period = dialog_period_option

    d_col3, d_col4 = st.columns(2)
    with d_col3:
        dialog_device = st.selectbox(
            "디바이스",
            options=['', 'pc', 'mo'],
            format_func=lambda x: {'': '전체', 'pc': 'PC', 'mo': '모바일'}[x],
            key="dialog_device"
        )
    with d_col4:
        dialog_gender = st.selectbox(
            "성별",
            options=['', 'm', 'f'],
            format_func=lambda x: {'': '전체', 'm': '남', 'f': '여'}[x],
            key="dialog_gender"
        )

    # 연령 선택
    st.markdown("**연령**")
    dialog_all_ages = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']
    dialog_age_options = {
        '1': '0-12', '2': '13-18', '3': '19-24', '4': '25-29',
        '5': '30-34', '6': '35-39', '7': '40-44', '8': '45-49',
        '9': '50-54', '10': '55-59', '11': '60+'
    }

    dialog_select_all_ages = st.checkbox("전체 연령 선택", value=False, key="dialog_all_ages")

    if dialog_select_all_ages:
        dialog_ages = dialog_all_ages
        st.caption(f"선택됨: 모든 연령대 (11개)")
    else:
        dialog_ages = st.multiselect(
            "연령 범위",
            options=dialog_all_ages,
            format_func=lambda x: dialog_age_options[x],
            placeholder="선택하세요",
            key="dialog_ages"
        )

    st.markdown("---")

    # 확인 버튼
    if st.button("분석 시작", type="primary", use_container_width=True, key="start_analysis"):
        # 기간 매핑
        period_map = {'1개월': 30, '3개월': 90, '1년': 365}
        if dialog_period == '직접입력':
            analysis_period = (dialog_custom_dates[1] - dialog_custom_dates[0]).days
        else:
            analysis_period = period_map[dialog_period]
        keywords = list(st.session_state.selected)[:5]

        result = get_trend(
            keywords=keywords,
            days=analysis_period,
            time_unit=dialog_unit,
            device=dialog_device,
            gender=dialog_gender,
            ages=dialog_ages,
            custom_dates=dialog_custom_dates
        )
        if result:
            st.session_state.trend_df = format_trend_results(result)
            st.session_state.trend_keywords = keywords
            # 분석 조건 저장
            st.session_state.trend_options = {
                'period': dialog_period,
                'time_unit': dialog_unit,
                'device': dialog_device,
                'gender': dialog_gender,
                'ages': dialog_ages,
                'age_labels': [dialog_age_options[a] for a in dialog_ages] if dialog_ages else [],
                'custom_dates': dialog_custom_dates
            }
            # 히스토리에 저장 (analyzed=True)
            st.session_state.keyword_history.append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'keywords': keywords,
                'analyzed': True
            })
            st.session_state.selected = set()
            # 메뉴를 데이터랩으로 전환
            st.session_state.menu = "📈  트렌드 분석"
            st.rerun()

# ===== 키워드 분석 페이지 =====
if menu_clean == "연관키워드":

    # ===== 연동 키워드 바 (상단 고정) =====
    if st.session_state.selected:
        st.markdown(f"""
        <style>
            .linked-keywords-bar {{
                background: {COLORS['primary']};
                border-radius: 8px;
                padding: 16px 24px;
                margin-bottom: 20px;
                color: white;
            }}
            .linked-keywords-bar .title {{
                font-size: 13px;
                font-weight: 500;
                margin-bottom: 8px;
                color: rgba(255,255,255,0.6);
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .linked-keywords-bar .keywords {{
                font-size: 14px;
                font-weight: 400;
            }}
            .linked-keywords-bar .keyword-tag {{
                display: inline-block;
                background: {COLORS['accent']};
                padding: 4px 12px;
                border-radius: 12px;
                margin-right: 8px;
                margin-bottom: 4px;
                font-size: 12px;
                font-weight: 500;
            }}
        </style>
        """, unsafe_allow_html=True)

        selected_list = list(st.session_state.selected)[:5]
        tags_html = "".join([f'<span class="keyword-tag">{kw}</span>' for kw in selected_list])
        extra = f' <span style="color:rgba(255,255,255,0.6)">+{len(st.session_state.selected) - 5}개</span>' if len(st.session_state.selected) > 5 else ''

        st.markdown(f"""
        <div class="linked-keywords-bar">
            <div class="title">🔗 연동 키워드 ({len(st.session_state.selected)}개)</div>
            <div class="keywords">{tags_html}{extra}</div>
        </div>
        """, unsafe_allow_html=True)

        # 액션 버튼
        btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1, 1, 1, 3])
        with btn_col1:
            if st.button("💾 저장", use_container_width=True):
                st.session_state.keyword_history.append({
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'keywords': list(st.session_state.selected),
                    'analyzed': False
                })
                st.toast("✅ 히스토리에 저장됨")
        with btn_col2:
            if st.button("📊 분석진행", type="primary", use_container_width=True):
                show_analysis_dialog()
        with btn_col3:
            if st.button("🗑️ 초기화", use_container_width=True):
                st.session_state.selected = set()
                st.rerun()

        st.markdown("")

    # ===== 검색 박스 =====
    st.markdown("### 연관키워드 조회")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        keywords_input = st.text_input(
            "키워드",
            placeholder="검색할 키워드 입력",
            label_visibility="collapsed"
        )
    with col2:
        include_related = st.checkbox("연관 키워드 포함", value=True)
    with col3:
        search_btn = st.button("조회하기", type="primary", use_container_width=True)

    if search_btn and keywords_input.strip():
        keywords = [k.strip() for k in keywords_input.replace('\n', ',').split(',') if k.strip()][:5]
        with st.spinner("조회 중..."):
            result = get_keyword_stats(keywords, include_related)
        if result:
            st.session_state.results_df = format_keyword_results(result)
            st.session_state.selected = set()

    if st.session_state.results_df is not None and len(st.session_state.results_df) > 0:
        df = st.session_state.results_df

        st.markdown('<div class="result-box">', unsafe_allow_html=True)

        top_col1, top_col2, top_col3 = st.columns([4, 1, 1])
        with top_col1:
            st.markdown(f"#### 연관키워드 조회 결과 ({len(df)}개)")
        with top_col2:
            csv = df.drop(columns=['_총검색량']).to_csv(index=False, encoding='utf-8-sig')
            st.download_button("다운로드", csv, "keywords.csv", "text/csv", use_container_width=True)
        with top_col3:
            filter_comp = st.selectbox("경쟁정도", ["전체", "높음", "중간", "낮음"], label_visibility="collapsed")

        if filter_comp != "전체":
            df = df[df['경쟁정도'] == filter_comp]

        st.markdown("---")

        # 2단 헤더 - st.columns 비율과 동일하게 맞춤
        st.markdown("""
        <table class="header-table" style="width:100%; table-layout:fixed;">
            <tr>
                <th rowspan="2" style="width:6%"></th>
                <th rowspan="2" style="width:22%">연관키워드</th>
                <th colspan="2" class="group-header" style="width:16%">월간검색수</th>
                <th colspan="2" class="group-header" style="width:16%">월평균클릭수</th>
                <th colspan="2" class="group-header" style="width:16%">월평균클릭률</th>
                <th rowspan="2" style="width:12%">경쟁정도</th>
                <th rowspan="2" style="width:6%">광고수</th>
            </tr>
            <tr>
                <th style="width:8%">PC</th>
                <th style="width:8%">모바일</th>
                <th style="width:8%">PC</th>
                <th style="width:8%">모바일</th>
                <th style="width:8%">PC</th>
                <th style="width:8%">모바일</th>
            </tr>
        </table>
        """, unsafe_allow_html=True)

        for idx, row in df.iterrows():
            cols = st.columns([0.6, 2.2, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.2, 0.6])
            kw = row['연관키워드']
            is_selected = kw in st.session_state.selected

            with cols[0]:
                if is_selected:
                    if st.button("✓", key=f"sel_{idx}", type="primary"):
                        st.session_state.selected.discard(kw)
                        st.rerun()
                else:
                    if st.button("추가", key=f"add_{idx}"):
                        st.session_state.selected.add(kw)
                        st.rerun()

            cols[1].markdown(f"{'**' + kw + '**' if is_selected else kw}")
            cols[2].markdown(f"<div style='text-align:center'>{row['PC']:,}</div>", unsafe_allow_html=True)
            cols[3].markdown(f"<div style='text-align:center'>{row['모바일']:,}</div>", unsafe_allow_html=True)
            cols[4].markdown(f"<div style='text-align:center'>{row['PC_클릭']}</div>", unsafe_allow_html=True)
            cols[5].markdown(f"<div style='text-align:center'>{row['모바일_클릭']}</div>", unsafe_allow_html=True)
            cols[6].markdown(f"<div style='text-align:center'>{row['PC_CTR']}%</div>", unsafe_allow_html=True)
            cols[7].markdown(f"<div style='text-align:center'>{row['모바일_CTR']}%</div>", unsafe_allow_html=True)

            comp = row['경쟁정도']
            if comp == '높음':
                cols[8].markdown("<div style='text-align:center'>🔴 높음</div>", unsafe_allow_html=True)
            elif comp == '중간':
                cols[8].markdown("<div style='text-align:center'>🟡 중간</div>", unsafe_allow_html=True)
            else:
                cols[8].markdown("<div style='text-align:center'>🟢 낮음</div>", unsafe_allow_html=True)

            cols[9].markdown(f"<div style='text-align:center'>{row['광고수']}</div>", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ===== 트렌드 결과 표시 (분석 후 같은 페이지에서 표시) =====
    if st.session_state.get('auto_show_trend', False) and st.session_state.trend_df is not None:
        st.markdown("---")
        st.markdown("### 📈 트렌드 분석 결과")

        trend_df = st.session_state.trend_df

        # 그래프
        chart_df = trend_df.copy()
        chart_df['검색지수'] = chart_df['검색지수'].round(0).astype(int)
        chart_df['날짜_표시'] = chart_df['날짜'].dt.strftime('%Y. %m. %d.')

        chart_colors = CHART_COLORS
        nearest = alt.selection_point(nearest=True, on='mouseover', fields=['날짜'], empty=False)

        line = alt.Chart(chart_df).mark_line().encode(
            x=alt.X('날짜:T', title='날짜', axis=alt.Axis(format='%m/%d')),
            y=alt.Y('검색지수:Q', title='검색지수'),
            color=alt.Color('키워드:N', scale=alt.Scale(range=chart_colors),
                          legend=alt.Legend(orient='top', labelLimit=200))
        )
        points = line.mark_point(size=80).encode(
            opacity=alt.condition(nearest, alt.value(1), alt.value(0))
        ).add_params(nearest)

        chart = alt.layer(line, points).properties(height=350).interactive()
        st.altair_chart(chart, use_container_width=True)

        # 결과 닫기 버튼
        if st.button("결과 닫기", key="close_trend"):
            st.session_state.auto_show_trend = False
            st.rerun()

    # ===== 키워드 히스토리 =====
    if st.session_state.keyword_history:
        st.markdown("---")
        st.markdown("### 📜 히스토리")

        for i, entry in enumerate(reversed(st.session_state.keyword_history)):
            idx = len(st.session_state.keyword_history) - 1 - i
            status = "📊 분석완료" if entry.get('analyzed', False) else "💾 저장됨"

            hist_col1, hist_col2, hist_col3 = st.columns([2, 3, 1])
            with hist_col1:
                st.caption(entry['timestamp'])
            with hist_col2:
                st.markdown(f"{status} | {', '.join(entry['keywords'][:3])}{'...' if len(entry['keywords']) > 3 else ''}")
            with hist_col3:
                if not entry.get('analyzed', False):
                    if st.button("불러오기", key=f"restore_{idx}"):
                        st.session_state.selected = set(entry['keywords'])
                        st.rerun()

        if st.button("히스토리 초기화", key="clear_history"):
            st.session_state.keyword_history = []
            st.rerun()

    else:
        st.info("키워드를 입력하고 '조회하기'를 클릭하세요.")


# ===== 트렌드 분석 페이지 =====
elif menu_clean == "트렌드 분석":
    st.markdown("### 키워드 트렌드 분석")
    st.markdown("네이버 데이터랩 API를 통해 키워드별 검색 트렌드를 확인합니다.")

    # 분석 조건 표시 바 (조회한 경우에만 표시)
    if st.session_state.get('trend_options') and st.session_state.get('trend_keywords'):
        opts = st.session_state.trend_options
        keywords = st.session_state.trend_keywords

        # 조건 라벨 매핑
        unit_label = {'date': '일간', 'week': '주간', 'month': '월간'}.get(opts.get('time_unit', ''), '')
        device_label = {'': '전체', 'pc': 'PC', 'mo': '모바일'}.get(opts.get('device', ''), '전체')
        gender_label = {'': '전체', 'm': '남성', 'f': '여성'}.get(opts.get('gender', ''), '전체')

        # 연령 표시
        age_labels = opts.get('age_labels', [])
        if len(age_labels) == 11:
            age_display = "전체"
        elif len(age_labels) > 0:
            age_display = ", ".join(age_labels[:3]) + ("..." if len(age_labels) > 3 else "")
        else:
            age_display = "전체"

        # 기간 표시
        custom_dates = opts.get('custom_dates')
        if custom_dates:
            period_display = f"{custom_dates[0].strftime('%Y.%m.%d')} ~ {custom_dates[1].strftime('%Y.%m.%d')}"
        else:
            period_display = opts.get('period', '')

        st.markdown(f"""
        <style>
            .analysis-info-bar {{
                background: transparent;
                border: none;
                border-left: 4px solid {COLORS['accent']};
                border-radius: 0;
                padding: 16px 20px;
                margin-bottom: 20px;
            }}
            .analysis-info-bar .info-title {{
                font-size: 13px;
                font-weight: 500;
                color: rgba(26, 26, 26, 0.6);
                margin-bottom: 12px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .analysis-info-bar .info-content {{
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
            }}
            .analysis-info-bar .info-item {{
                background: {COLORS['bg']};
                border: 1px solid rgba(0, 0, 0, 0.06);
                border-radius: 12px;
                padding: 4px 12px;
                font-size: 13px;
                color: {COLORS['primary']};
            }}
            .analysis-info-bar .info-label {{
                color: rgba(26, 26, 26, 0.5);
                margin-right: 4px;
            }}
            .analysis-info-bar .keyword-tags {{
                margin-top: 12px;
            }}
            .analysis-info-bar .keyword-tag {{
                display: inline-block;
                background: {COLORS['accent']};
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                margin-right: 6px;
                font-size: 12px;
                font-weight: 500;
            }}
        </style>
        """, unsafe_allow_html=True)

        keyword_tags = "".join([f'<span class="keyword-tag">{kw}</span>' for kw in keywords])

        st.markdown(f"""
        <div class="analysis-info-bar">
            <div class="info-title">현재 분석 조건</div>
            <div class="info-content">
                <span class="info-item"><span class="info-label">기간</span>{period_display}</span>
                <span class="info-item"><span class="info-label">단위</span>{unit_label}</span>
                <span class="info-item"><span class="info-label">디바이스</span>{device_label}</span>
                <span class="info-item"><span class="info-label">성별</span>{gender_label}</span>
                <span class="info-item"><span class="info-label">연령</span>{age_display}</span>
            </div>
            <div class="keyword-tags">{keyword_tags}</div>
        </div>
        """, unsafe_allow_html=True)

    # 트렌드 조회 실행
    if trend_btn and trend_keywords.strip():
        keywords = [k.strip() for k in trend_keywords.split(',') if k.strip()][:5]
        with st.spinner("트렌드 조회 중..."):
            result = get_trend(
                keywords=keywords,
                days=period,
                time_unit=time_unit,
                device=device,
                gender=gender,
                ages=ages,
                custom_dates=custom_dates
            )
        if result:
            st.session_state.trend_df = format_trend_results(result)
            st.session_state.trend_keywords = keywords
            # 분석 조건 저장
            age_labels_map = {
                '1': '0-12', '2': '13-18', '3': '19-24', '4': '25-29',
                '5': '30-34', '6': '35-39', '7': '40-44', '8': '45-49',
                '9': '50-54', '10': '55-59', '11': '60+'
            }
            st.session_state.trend_options = {
                'period': period_option,
                'time_unit': time_unit,
                'device': device,
                'gender': gender,
                'ages': ages,
                'age_labels': [age_labels_map[a] for a in ages] if ages else [],
                'custom_dates': custom_dates
            }

    if st.session_state.trend_df is not None and len(st.session_state.trend_df) > 0:
        trend_df = st.session_state.trend_df

        st.markdown('<div class="result-box">', unsafe_allow_html=True)

        # 그래프
        st.markdown("#### 검색 트렌드 그래프")

        # 검색지수를 정수로 변환
        chart_df = trend_df.copy()
        chart_df['검색지수'] = chart_df['검색지수'].round(0).astype(int)
        chart_df['날짜_표시'] = chart_df['날짜'].dt.strftime('%Y. %m. %d.')

        # Altair 차트 (툴팁 커스터마이징)
        chart_colors = CHART_COLORS

        # hover selection
        nearest = alt.selection_point(nearest=True, on='mouseover', fields=['날짜'], empty=False)

        # 기본 라인
        line = alt.Chart(chart_df).mark_line().encode(
            x=alt.X('날짜:T', title='날짜', axis=alt.Axis(format='%m/%d')),
            y=alt.Y('검색지수:Q', title='검색지수'),
            color=alt.Color('키워드:N', scale=alt.Scale(range=chart_colors),
                          legend=alt.Legend(orient='top', labelLimit=200))
        )

        # hover 시에만 포인트 표시
        points = line.mark_point(size=80).encode(
            opacity=alt.condition(nearest, alt.value(1), alt.value(0))
        ).add_params(nearest)

        # 툴팁용 투명 셀렉터
        selectors = alt.Chart(chart_df).mark_point(size=1, opacity=0).encode(
            x='날짜:T',
            tooltip=[
                alt.Tooltip('날짜_표시:N', title=''),
                alt.Tooltip('키워드:N', title=''),
                alt.Tooltip('검색지수:Q', title='', format='d')
            ]
        ).add_params(nearest)

        chart = alt.layer(line, points, selectors).properties(height=400).interactive()

        st.altair_chart(chart, use_container_width=True)

        st.markdown("---")

        # 통계 요약
        st.markdown("#### 키워드별 통계")
        stats_data = []
        for kw in trend_df['키워드'].unique():
            kw_data = trend_df[trend_df['키워드'] == kw]['검색지수']
            stats_data.append({
                '키워드': kw,
                '평균': round(kw_data.mean(), 1),
                '최대': round(kw_data.max(), 1),
                '최소': round(kw_data.min(), 1),
            })

        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df, use_container_width=True, hide_index=True)

        st.markdown("---")

        # 데이터 다운로드
        col1, col2 = st.columns(2)
        with col1:
            csv = trend_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                "📥 트렌드 데이터 CSV",
                csv,
                f"trend_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                "text/csv",
                use_container_width=True
            )

        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("왼쪽 사이드바에서 키워드와 조건을 입력하고 '트렌드 조회' 버튼을 클릭하세요.")

        st.markdown("---")
        st.markdown("**사용 방법:**")
        st.markdown("""
        1. **키워드**: 비교할 키워드 입력 (최대 5개, 쉼표로 구분)
        2. **기간**: 분석 기간 선택
        3. **시간 단위**: 일별/주별/월별
        4. **디바이스**: PC/모바일/전체
        5. **성별/연령**: 타겟 세분화 (선택사항)
        """)


# ===== 광고 운영 현황 페이지 =====
elif menu_clean == "광고 현황":
    # 세션 상태 초기화
    if 'campaigns' not in st.session_state:
        st.session_state.campaigns = None
    if 'selected_campaign_id' not in st.session_state:
        st.session_state.selected_campaign_id = None
    if 'adgroups' not in st.session_state:
        st.session_state.adgroups = None
    if 'selected_adgroup_id' not in st.session_state:
        st.session_state.selected_adgroup_id = None
    if 'ad_keywords' not in st.session_state:
        st.session_state.ad_keywords = None
    if 'bizmoney' not in st.session_state:
        st.session_state.bizmoney = None

    # ===== 캠페인 상세 뷰 =====
    if st.session_state.selected_campaign_id and st.session_state.campaigns:
        selected_campaign = next(
            (c for c in st.session_state.campaigns if c.get('nccCampaignId') == st.session_state.selected_campaign_id),
            None
        )

        if selected_campaign:
            campaign_id = selected_campaign.get('nccCampaignId')
            campaign_name = selected_campaign.get('name', '')

            # 캠페인 유형 매핑
            campaign_type = {
                'WEB_SITE': '웹사이트',
                'SHOPPING': '쇼핑',
                'BRAND_SEARCH': '브랜드검색/신제품검색',
                'POWER_CONTENTS': '파워콘텐츠'
            }.get(selected_campaign.get('campaignTp'), selected_campaign.get('campaignTp', '-'))

            # 상태 매핑
            if selected_campaign.get('userLock'):
                campaign_status = "사용자 OFF"
                status_color = "#ff6b6b"
            elif selected_campaign.get('status') == 'ELIGIBLE':
                campaign_status = "노출가능"
                status_color = "#51cf66"
            else:
                campaign_status = selected_campaign.get('status', '-')
                status_color = "#868e96"

            # 상단 네비게이션
            st.markdown(f"""
            <style>
                .campaign-detail-header {{
                    background: transparent;
                    border: none;
                    border-radius: 0;
                    padding: 24px 0;
                    margin-bottom: 20px;
                }}
                .breadcrumb {{
                    color: {COLORS['accent']};
                    font-size: 13px;
                    cursor: pointer;
                    margin-bottom: 8px;
                }}
                .breadcrumb:hover {{
                    text-decoration: underline;
                }}
                .campaign-title {{
                    font-size: 18px;
                    font-weight: 500;
                    color: {COLORS['primary']};
                }}
                .campaign-info-panel {{
                    background: {COLORS['bg']};
                    border: 1px solid rgba(0, 0, 0, 0.06);
                    border-radius: 8px;
                    padding: 20px;
                }}
                .info-row {{
                    display: flex;
                    justify-content: space-between;
                    padding: 12px 0;
                    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
                }}
                .info-row:last-child {{
                    border-bottom: none;
                }}
                .info-label {{
                    color: rgba(26, 26, 26, 0.6);
                    font-size: 13px;
                }}
                .info-value {{
                    font-weight: 500;
                    font-size: 14px;
                    color: {COLORS['primary']};
                }}
            </style>
            """, unsafe_allow_html=True)

            # 뒤로 가기 버튼
            if st.button("← 모든 캠페인", key="back_to_campaigns"):
                st.session_state.selected_campaign_id = None
                st.session_state.adgroups = None
                st.session_state.selected_adgroup_id = None
                st.session_state.ad_keywords = None
                st.rerun()

            # 캠페인 제목
            st.markdown(f"### {campaign_type} 캠페인: {campaign_name}")

            # 상단 레이아웃: 성과 그래프 + 캠페인 정보
            col_graph, col_info = st.columns([3, 1])

            with col_graph:
                # 성과 그래프 영역
                st.markdown(f"**캠페인 : {campaign_name}**")

                # 지표 선택 + 기간 선택
                metric_col1, metric_col2, metric_col3 = st.columns([1, 1, 2])
                with metric_col1:
                    primary_metric = st.selectbox(
                        "지표",
                        options=['노출수', '클릭수', '비용', 'CTR'],
                        label_visibility="collapsed",
                        key="primary_metric"
                    )
                with metric_col2:
                    period_days = st.selectbox(
                        "기간",
                        options=[7, 14, 30],
                        format_func=lambda x: f"최근 {x}일",
                        label_visibility="collapsed",
                        key="stat_period"
                    )

                # 세션 상태에 통계 데이터 저장
                if 'campaign_stats' not in st.session_state:
                    st.session_state.campaign_stats = None
                if 'campaign_stats_id' not in st.session_state:
                    st.session_state.campaign_stats_id = None

                # 통계 데이터 조회 버튼
                if st.button("📊 성과 조회", key="load_stats"):
                    with st.spinner("성과 데이터 조회 중..."):
                        stats = get_daily_stats(campaign_id, days=period_days)
                        st.session_state.campaign_stats = stats
                        st.session_state.campaign_stats_id = campaign_id

                # 그래프 표시
                if st.session_state.campaign_stats and st.session_state.campaign_stats_id == campaign_id:
                    stats_df = pd.DataFrame(st.session_state.campaign_stats)

                    if len(stats_df) > 0 and stats_df[primary_metric].sum() > 0:
                        # 지표 매핑
                        metric_map = {
                            '노출수': '노출수',
                            '클릭수': '클릭수',
                            '비용': '비용',
                            'CTR': 'CTR'
                        }

                        # Altair 차트
                        chart_df = stats_df.copy()
                        chart_df['날짜_표시'] = chart_df['날짜'].dt.strftime('%m/%d')

                        # 호버 선택
                        nearest = alt.selection_point(nearest=True, on='mouseover', fields=['날짜'], empty=False)

                        # 라인 차트
                        line = alt.Chart(chart_df).mark_line(
                            color=COLORS['accent'],
                            strokeWidth=2
                        ).encode(
                            x=alt.X('날짜:T', title='', axis=alt.Axis(format='%m/%d')),
                            y=alt.Y(f'{primary_metric}:Q', title=primary_metric)
                        )

                        # 포인트 (호버 시)
                        points = line.mark_point(size=80, color=COLORS['accent']).encode(
                            opacity=alt.condition(nearest, alt.value(1), alt.value(0))
                        ).add_params(nearest)

                        # 툴팁용 투명 셀렉터
                        selectors = alt.Chart(chart_df).mark_point(size=1, opacity=0).encode(
                            x='날짜:T',
                            tooltip=[
                                alt.Tooltip('날짜_표시:N', title='날짜'),
                                alt.Tooltip(f'{primary_metric}:Q', title=primary_metric, format=',.0f')
                            ]
                        ).add_params(nearest)

                        chart = alt.layer(line, points, selectors).properties(height=250).interactive()
                        st.altair_chart(chart, use_container_width=True)

                        # 기간 요약 지표
                        sum_cols = st.columns(4)
                        with sum_cols[0]:
                            total_imp = stats_df['노출수'].sum()
                            st.metric("총 노출수", f"{total_imp:,.0f}")
                        with sum_cols[1]:
                            total_clk = stats_df['클릭수'].sum()
                            st.metric("총 클릭수", f"{total_clk:,.0f}")
                        with sum_cols[2]:
                            total_cost = stats_df['비용'].sum()
                            st.metric("총 비용", f"{total_cost:,.0f}원")
                        with sum_cols[3]:
                            avg_ctr = (total_clk / total_imp * 100) if total_imp > 0 else 0
                            st.metric("평균 CTR", f"{avg_ctr:.2f}%")
                    else:
                        st.info("조회 기간에 성과 데이터가 없습니다.")
                else:
                    # 조회 전 안내
                    st.info("'성과 조회' 버튼을 클릭하여 데이터를 불러오세요")

            with col_info:
                # 캠페인 정보 패널
                st.markdown("**캠페인 정보**")

                # ON/OFF 상태
                is_on = not selected_campaign.get('userLock', False) and selected_campaign.get('status') == 'ELIGIBLE'
                st.markdown(f"""
                <div class="campaign-info-panel">
                    <div class="info-row">
                        <span class="info-label">상태</span>
                        <span class="info-value" style="color: {status_color};">{campaign_status}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">캠페인 유형</span>
                        <span class="info-value">{campaign_type}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">일 예산</span>
                        <span class="info-value">{selected_campaign.get('dailyBudget', 0):,}원</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")

            # 광고그룹 섹션
            st.markdown("#### 광고그룹")

            # 광고그룹 자동 로드 (최초 1회)
            if st.session_state.adgroups is None:
                with st.spinner("광고그룹 불러오는 중..."):
                    st.session_state.adgroups = get_adgroups(campaign_id)

            if st.session_state.adgroups:
                adgroups = st.session_state.adgroups

                # 광고그룹 테이블 헤더
                st.markdown("""
                <table class="header-table">
                    <tr>
                        <th style="width:60px">ON/OFF</th>
                        <th style="width:80px">상태</th>
                        <th>광고그룹 이름</th>
                        <th style="width:100px">입찰가</th>
                        <th style="width:100px">노출수</th>
                        <th style="width:100px">클릭수</th>
                        <th style="width:80px">클릭률</th>
                    </tr>
                </table>
                """, unsafe_allow_html=True)

                for idx, ag in enumerate(adgroups):
                    ag_id = ag.get('nccAdgroupId', '')
                    ag_name = ag.get('name', '')
                    ag_bid = ag.get('bidAmt', 0)

                    # 상태 판단
                    if ag.get('userLock'):
                        ag_status = "⏸️ 중지"
                        ag_on = False
                    elif ag.get('status') == 'ELIGIBLE':
                        ag_status = "🟢 노출가능"
                        ag_on = True
                    else:
                        ag_status = f"⚪ {ag.get('status', '-')}"
                        ag_on = False

                    # 행 표시
                    cols = st.columns([0.6, 0.8, 2.5, 1, 1, 1, 0.8])

                    with cols[0]:
                        st.markdown("🟢" if ag_on else "⚪")
                    with cols[1]:
                        st.markdown(ag_status)
                    with cols[2]:
                        # 광고그룹명 클릭 시 키워드 조회
                        if st.button(ag_name, key=f"ag_{idx}", use_container_width=True):
                            st.session_state.selected_adgroup_id = ag_id
                            with st.spinner("키워드 불러오는 중..."):
                                st.session_state.ad_keywords = get_ad_keywords(ag_id)
                            st.rerun()
                    with cols[3]:
                        st.markdown(f"{ag_bid:,}원" if ag_bid else "-")
                    with cols[4]:
                        st.markdown("-")  # 노출수 placeholder
                    with cols[5]:
                        st.markdown("-")  # 클릭수 placeholder
                    with cols[6]:
                        st.markdown("-")  # 클릭률 placeholder

                # 선택된 광고그룹의 키워드 표시
                if st.session_state.selected_adgroup_id and st.session_state.ad_keywords:
                    selected_ag = next(
                        (ag for ag in adgroups if ag.get('nccAdgroupId') == st.session_state.selected_adgroup_id),
                        None
                    )
                    if selected_ag:
                        st.markdown("---")
                        st.markdown(f"#### 🔑 키워드: {selected_ag.get('name', '')}")

                        keywords = st.session_state.ad_keywords

                        if keywords:
                            keyword_data = []
                            for kw in keywords:
                                if kw.get('userLock'):
                                    kw_status = "⏸️ 중지"
                                elif kw.get('status') == 'ELIGIBLE':
                                    kw_status = "🟢 운영 중"
                                else:
                                    kw_status = f"⚪ {kw.get('status', '-')}"

                                bid = kw.get('bidAmt', 0)

                                keyword_data.append({
                                    '키워드': kw.get('keyword', ''),
                                    '상태': kw_status,
                                    '입찰가': f"{bid:,}원" if bid else '그룹 설정',
                                    '품질지수': kw.get('qualityIndex', '-'),
                                    '매칭타입': kw.get('keywordPlusType', 'EXACT')
                                })

                            keyword_df = pd.DataFrame(keyword_data)
                            st.dataframe(keyword_df, use_container_width=True, hide_index=True)

                            # CSV 다운로드
                            csv = keyword_df.to_csv(index=False, encoding='utf-8-sig')
                            st.download_button(
                                "📥 키워드 CSV 다운로드",
                                csv,
                                f"keywords_{selected_ag.get('name', '')}_{datetime.now().strftime('%Y%m%d')}.csv",
                                "text/csv"
                            )

                        # 키워드 닫기 버튼
                        if st.button("키워드 닫기", key="close_keywords"):
                            st.session_state.selected_adgroup_id = None
                            st.session_state.ad_keywords = None
                            st.rerun()

            else:
                st.info("광고그룹이 없습니다.")

    # ===== 캠페인 목록 뷰 (기본) =====
    else:
        st.markdown("### 네이버 광고 운영 현황")
        st.markdown("네이버 검색광고 계정의 캠페인, 광고그룹, 키워드 현황을 확인합니다.")

        # 페이지 진입 시 자동으로 데이터 로드
        if st.session_state.campaigns is None:
            with st.spinner("캠페인 데이터 불러오는 중..."):
                st.session_state.campaigns = get_campaigns()
                st.session_state.bizmoney = get_bizmoney()
            if st.session_state.campaigns:
                st.rerun()

        # 비즈머니 정보
        if st.session_state.bizmoney:
            bm = st.session_state.bizmoney
            st.markdown(f"""
            <div style="background: {COLORS['primary']}; color: white; padding: 24px; border-radius: 8px; margin: 20px 0;">
                <div style="font-size: 13px; color: rgba(255,255,255,0.6); text-transform: uppercase; letter-spacing: 0.5px;">비즈머니 잔액</div>
                <div style="font-size: 32px; font-weight: 300; margin-top: 8px;">{bm.get('bizmoney', 0):,.0f}원</div>
                <div style="font-size: 13px; margin-top: 12px; color: rgba(255,255,255,0.5);">
                    환불 가능: {bm.get('refundableAmount', 0):,.0f}원 |
                    예치금: {bm.get('budgetLock', 0):,.0f}원
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 캠페인 목록
        if st.session_state.campaigns:
            campaigns = st.session_state.campaigns

            st.markdown("---")
            st.markdown("#### 캠페인 목록")
            st.caption("캠페인명을 클릭하면 상세 정보를 확인할 수 있습니다.")

            # 캠페인 상태별 분류
            active_campaigns = [c for c in campaigns if c.get('status') == 'ELIGIBLE' and c.get('userLock') == False]
            paused_campaigns = [c for c in campaigns if c.get('userLock') == True or c.get('status') == 'PAUSED']

            # 요약 카드
            summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
            with summary_col1:
                st.metric("전체 캠페인", len(campaigns))
            with summary_col2:
                st.metric("운영 중", len(active_campaigns))
            with summary_col3:
                st.metric("일시 중지", len(paused_campaigns))
            with summary_col4:
                total_budget = sum(c.get('dailyBudget', 0) for c in active_campaigns if c.get('dailyBudget'))
                st.metric("일 예산 합계", f"{total_budget:,}원")

            st.markdown("")

            # 캠페인 테이블 (클릭 가능)
            st.markdown(f"""
            <style>
                .campaign-row {{
                    padding: 16px 0;
                    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
                }}
                /* 캠페인명 버튼을 링크 스타일로 변경 */
                .campaign-link-btn button {{
                    background: transparent !important;
                    border: none !important;
                    color: {COLORS['accent']} !important;
                    padding: 0 !important;
                    font-weight: 500 !important;
                    text-align: left !important;
                    box-shadow: none !important;
                }}
                .campaign-link-btn button:hover {{
                    text-decoration: underline;
                    background: transparent !important;
                    border: none !important;
                    box-shadow: none !important;
                }}
                .campaign-link-btn button:focus {{
                    box-shadow: none !important;
                    outline: none !important;
                }}
            </style>
            """, unsafe_allow_html=True)

            # 테이블 헤더
            header_cols = st.columns([0.5, 0.8, 2.5, 1, 1, 1])
            with header_cols[0]:
                st.markdown("**ON/OFF**")
            with header_cols[1]:
                st.markdown("**상태**")
            with header_cols[2]:
                st.markdown("**캠페인명**")
            with header_cols[3]:
                st.markdown("**유형**")
            with header_cols[4]:
                st.markdown("**일 예산**")
            with header_cols[5]:
                st.markdown("**입찰전략**")

            st.markdown("---")

            for idx, c in enumerate(campaigns):
                campaign_id = c.get('nccCampaignId', '')
                campaign_name = c.get('name', '')

                # 상태 표시
                if c.get('userLock'):
                    status = "⏸️ 중지"
                    is_on = False
                elif c.get('status') == 'ELIGIBLE':
                    status = "🟢 노출가능"
                    is_on = True
                elif c.get('status') == 'PAUSED':
                    status = "⏸️ 중지"
                    is_on = False
                else:
                    status = f"⚪ {c.get('status', '-')}"
                    is_on = False

                # 캠페인 유형
                campaign_type = {
                    'WEB_SITE': '웹사이트',
                    'SHOPPING': '쇼핑',
                    'BRAND_SEARCH': '브랜드검색',
                    'POWER_CONTENTS': '파워콘텐츠'
                }.get(c.get('campaignTp'), c.get('campaignTp', '-'))

                # 행 표시
                cols = st.columns([0.5, 0.8, 2.5, 1, 1, 1])

                with cols[0]:
                    st.markdown("🟢" if is_on else "⚪")
                with cols[1]:
                    st.markdown(status)
                with cols[2]:
                    # 캠페인명 클릭 시 상세 페이지로 이동 (링크 스타일)
                    st.markdown('<div class="campaign-link-btn">', unsafe_allow_html=True)
                    if st.button(campaign_name, key=f"camp_{idx}"):
                        st.session_state.selected_campaign_id = campaign_id
                        st.session_state.adgroups = None
                        st.session_state.selected_adgroup_id = None
                        st.session_state.ad_keywords = None
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with cols[3]:
                    st.markdown(campaign_type)
                with cols[4]:
                    budget = c.get('dailyBudget', 0)
                    st.markdown(f"{budget:,}원" if budget else "무제한")
                with cols[5]:
                    bid_strategy = c.get('bidStrategy', {}).get('type', '-') if c.get('bidStrategy') else '-'
                    st.markdown(bid_strategy)

        else:
            st.warning("캠페인 데이터를 불러올 수 없습니다. API 설정을 확인해주세요.")
