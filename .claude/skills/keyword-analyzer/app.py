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

# 브랜드 컬러 (personal-branding-guide.md)
COLORS = {
    'primary': '#1E3A5F',
    'secondary': '#4A90D9',
    'background': '#FFFFFF',
    'text': '#333333',
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
st.set_page_config(page_title="키워드 분석 도구", page_icon="🔍", layout="wide")

# CSS 스타일
st.markdown(f"""
<style>
    .main > div {{ padding-top: 1rem; }}
    .stApp {{ background-color: #f8f9fa; }}

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

    [data-testid="stSidebar"] {{
        background-color: {COLORS['primary']};
    }}
    /* 사이드바 기본 텍스트만 흰색 (하위 요소 제외) */
    [data-testid="stSidebar"] > div > div > div {{
        color: white;
    }}
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {{
        color: white !important;
    }}
    /* 드롭다운 메뉴 (body에 렌더링됨) */
    [data-baseweb="popover"] [data-baseweb="menu"] {{
        background-color: white !important;
    }}
    [data-baseweb="popover"] li {{
        color: #333333 !important;
    }}
    [data-baseweb="popover"] li:hover {{
        background-color: #f0f7ff !important;
    }}
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] span,
    [data-testid="stSidebar"] [data-baseweb="input"] input {{
        color: #333333 !important;
        background-color: white !important;
    }}
    /* Selectbox 드롭다운 옵션 */
    [data-testid="stSidebar"] [data-baseweb="select"] div,
    [data-testid="stSidebar"] [data-baseweb="select"] svg {{
        color: #333333 !important;
    }}
    /* Multiselect 선택된 태그 */
    [data-testid="stSidebar"] [data-baseweb="tag"] {{
        background-color: {COLORS['secondary']} !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="tag"] span {{
        color: white !important;
    }}
    /* Checkbox */
    [data-testid="stSidebar"] .stCheckbox label span {{
        color: white !important;
    }}
    /* Date input */
    [data-testid="stSidebar"] [data-baseweb="input"] {{
        background-color: white !important;
    }}
    [data-testid="stSidebar"] .stDateInput input {{
        color: #333333 !important;
    }}
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stTextInput label {{
        color: white !important;
    }}

    .header-box {{
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 16px;
    }}
    .result-box {{
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 20px;
    }}
    .selected-box {{
        background: #f0f7ff;
        border: 1px solid {COLORS['secondary']};
        border-radius: 8px;
        padding: 16px;
        margin-top: 16px;
    }}
    .header-table {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 8px;
    }}
    .header-table th {{
        background: #f8f9fa;
        border: 1px solid #e0e0e0;
        padding: 8px;
        text-align: center;
        font-size: 13px;
        font-weight: 600;
    }}
    .header-table .group-header {{
        background: #e8f4f8;
    }}
</style>
""", unsafe_allow_html=True)

# ===== 사이드바 =====
with st.sidebar:
    # 사이드바 스타일
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1E3A5F 0%, #2C5282 100%);
            padding-top: 2rem;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            color: white !important;
        }
        [data-testid="stSidebar"] label {
            color: white !important;
        }
        [data-testid="stSidebar"] .stSelectbox label p,
        [data-testid="stSidebar"] .stTextInput label p,
        [data-testid="stSidebar"] .stMultiSelect label p {
            color: rgba(255,255,255,0.9) !important;
            font-size: 13px !important;
        }
        .sidebar-title {
            font-size: 24px;
            font-weight: 700;
            color: white !important;
            margin-bottom: 8px;
        }
        .sidebar-subtitle {
            font-size: 14px;
            color: rgba(255,255,255,0.7) !important;
            margin-bottom: 24px;
        }
        .menu-header {
            font-size: 16px;
            font-weight: 600;
            color: white !important;
            margin-top: 16px;
            margin-bottom: 8px;
        }
        .menu-divider {
            border-top: 1px solid rgba(255,255,255,0.2);
            margin: 16px 0;
        }
        /* 라디오 버튼 동그라미 숨기기 */
        [data-testid="stSidebar"] .stRadio > div {
            gap: 0 !important;
        }
        [data-testid="stSidebar"] .stRadio > div > label > div:first-child {
            display: none !important;
        }
        [data-testid="stSidebar"] .stRadio > div > label {
            padding: 8px 0 !important;
            cursor: pointer;
        }
        [data-testid="stSidebar"] .stRadio > div > label > div:last-child p {
            font-size: 15px !important;
            color: rgba(255,255,255,0.75) !important;
            font-weight: 400 !important;
            transition: all 0.15s ease;
        }
        [data-testid="stSidebar"] .stRadio > div > label:hover > div:last-child p {
            color: white !important;
            font-weight: 600 !important;
        }
        [data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] > div:last-child p {
            color: white !important;
            font-weight: 700 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="sidebar-title">키워드 분석</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-subtitle">Naver API 기반 분석 도구</p>', unsafe_allow_html=True)

    st.markdown('<div class="menu-divider"></div>', unsafe_allow_html=True)

    # 메뉴 선택 (session_state로 관리)
    st.markdown('<p class="menu-header">분석 도구</p>', unsafe_allow_html=True)
    if 'menu' not in st.session_state:
        st.session_state.menu = "네이버검색광고"

    menu = st.radio(
        "menu",
        ["네이버검색광고", "네이버데이터랩"],
        index=["네이버검색광고", "네이버데이터랩"].index(st.session_state.menu),
        key="menu_radio",
        label_visibility="collapsed"
    )
    st.session_state.menu = menu

    st.markdown('<div class="menu-divider"></div>', unsafe_allow_html=True)

    # 트렌드 설정 (트렌드 메뉴일 때만)
    if menu == "네이버데이터랩":
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
        dialog_period = st.selectbox(
            "기간",
            options=['1개월', '3개월', '1년'],
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

    st.markdown("---")

    # 확인 버튼
    if st.button("분석 시작", type="primary", use_container_width=True, key="start_analysis"):
        # 기간 매핑
        period_map = {'1개월': 30, '3개월': 90, '1년': 365}
        analysis_period = period_map[dialog_period]
        keywords = list(st.session_state.selected)[:5]

        result = get_trend(
            keywords=keywords,
            days=analysis_period,
            time_unit=dialog_unit,
            device=dialog_device,
            gender=dialog_gender,
            ages=[]
        )
        if result:
            st.session_state.trend_df = format_trend_results(result)
            st.session_state.trend_keywords = keywords
            # 히스토리에 저장 (analyzed=True)
            st.session_state.keyword_history.append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'keywords': keywords,
                'analyzed': True
            })
            st.session_state.selected = set()
            # 메뉴를 데이터랩으로 전환
            st.session_state.menu = "네이버데이터랩"
            st.rerun()

# ===== 키워드 분석 페이지 =====
if menu == "네이버검색광고":

    # ===== 연동 키워드 바 (상단 고정) =====
    if st.session_state.selected:
        st.markdown("""
        <style>
            .linked-keywords-bar {
                background: linear-gradient(135deg, #1E3A5F 0%, #2C5282 100%);
                border-radius: 10px;
                padding: 16px 20px;
                margin-bottom: 16px;
                color: white;
            }
            .linked-keywords-bar .title {
                font-size: 14px;
                font-weight: 600;
                margin-bottom: 8px;
                color: rgba(255,255,255,0.8);
            }
            .linked-keywords-bar .keywords {
                font-size: 15px;
                font-weight: 500;
            }
            .linked-keywords-bar .keyword-tag {
                display: inline-block;
                background: rgba(255,255,255,0.2);
                padding: 4px 12px;
                border-radius: 20px;
                margin-right: 8px;
                margin-bottom: 4px;
                font-size: 14px;
            }
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
    st.markdown('<div class="header-box">', unsafe_allow_html=True)
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

    st.markdown('</div>', unsafe_allow_html=True)

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

        top_col1, top_col2, top_col3, top_col4 = st.columns([3, 1, 1, 1])
        with top_col1:
            st.markdown(f"#### 연관키워드 조회 결과 ({len(df)}개)")
        with top_col2:
            if st.button("전체추가", use_container_width=True):
                st.session_state.selected = set(df['연관키워드'].tolist())
                st.rerun()
        with top_col3:
            csv = df.drop(columns=['_총검색량']).to_csv(index=False, encoding='utf-8-sig')
            st.download_button("다운로드", csv, "keywords.csv", "text/csv", use_container_width=True)
        with top_col4:
            filter_comp = st.selectbox("경쟁정도", ["전체", "높음", "중간", "낮음"], label_visibility="collapsed")

        if filter_comp != "전체":
            df = df[df['경쟁정도'] == filter_comp]

        st.markdown("---")

        # 2단 헤더
        st.markdown("""
        <table class="header-table">
            <tr>
                <th rowspan="2" style="width:60px"></th>
                <th rowspan="2" style="width:200px">연관키워드</th>
                <th colspan="2" class="group-header">월간검색수</th>
                <th colspan="2" class="group-header">월평균클릭수</th>
                <th colspan="2" class="group-header">월평균클릭률</th>
                <th rowspan="2" style="width:70px">경쟁정도</th>
                <th rowspan="2" style="width:50px">광고수</th>
            </tr>
            <tr>
                <th style="width:70px">PC</th>
                <th style="width:70px">모바일</th>
                <th style="width:70px">PC</th>
                <th style="width:70px">모바일</th>
                <th style="width:70px">PC</th>
                <th style="width:70px">모바일</th>
            </tr>
        </table>
        """, unsafe_allow_html=True)

        for idx, row in df.iterrows():
            cols = st.columns([0.5, 3.5, 0.7, 0.7, 0.7, 0.7, 0.6, 0.6, 0.6, 0.5])
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
            cols[2].write(f"{row['PC']:,}")
            cols[3].write(f"{row['모바일']:,}")
            cols[4].write(f"{row['PC_클릭']}")
            cols[5].write(f"{row['모바일_클릭']}")
            cols[6].write(f"{row['PC_CTR']}%")
            cols[7].write(f"{row['모바일_CTR']}%")

            comp = row['경쟁정도']
            if comp == '높음':
                cols[8].markdown("🔴 높음")
            elif comp == '중간':
                cols[8].markdown("🟡 중간")
            else:
                cols[8].markdown("🟢 낮음")

            cols[9].write(row['광고수'])

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

        chart_colors = [COLORS['primary'], COLORS['secondary'], '#34a853', '#ea4335', '#fbbc05']
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
elif menu == "네이버데이터랩":
    st.markdown("### 📈 키워드 트렌드 분석")
    st.markdown("네이버 데이터랩 API를 통해 키워드별 검색 트렌드를 확인합니다.")

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
        chart_colors = [COLORS['primary'], COLORS['secondary'], '#34a853', '#ea4335', '#fbbc05']

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
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.info("👈 왼쪽 사이드바에서 키워드와 조건을 입력하고 '트렌드 조회' 버튼을 클릭하세요.")

        st.markdown("---")
        st.markdown("**사용 방법:**")
        st.markdown("""
        1. **키워드**: 비교할 키워드 입력 (최대 5개, 쉼표로 구분)
        2. **기간**: 분석 기간 선택
        3. **시간 단위**: 일별/주별/월별
        4. **디바이스**: PC/모바일/전체
        5. **성별/연령**: 타겟 세분화 (선택사항)
        """)
        st.markdown('</div>', unsafe_allow_html=True)
