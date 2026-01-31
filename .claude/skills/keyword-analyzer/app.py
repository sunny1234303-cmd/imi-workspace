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
def get_trend(keywords, days=30, time_unit='date', device='', gender='', ages=[]):
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        st.error("데이터랩 API 키가 설정되지 않았습니다.")
        return None

    url = "https://openapi.naver.com/v1/datalab/search"

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

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", NAVER_CLIENT_ID)
    request.add_header("X-Naver-Client-Secret", NAVER_CLIENT_SECRET)
    request.add_header("Content-Type", "application/json")

    try:
        response = urllib.request.urlopen(request, data=json.dumps(body).encode("utf-8"))
        return json.loads(response.read().decode("utf-8"))
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

    return pd.DataFrame(data)


# ===== 페이지 설정 =====
st.set_page_config(page_title="키워드 분석 도구", page_icon="🔍", layout="wide")

# CSS 스타일
st.markdown(f"""
<style>
    .main > div {{ padding-top: 1rem; }}
    .stApp {{ background-color: #f8f9fa; }}

    [data-testid="stSidebar"] {{
        background-color: {COLORS['primary']};
    }}
    [data-testid="stSidebar"] * {{
        color: white !important;
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

    # 메뉴 선택
    st.markdown('<p class="menu-header">분석 도구</p>', unsafe_allow_html=True)
    menu = st.radio(
        "menu",
        ["네이버검색광고", "네이버데이터랩"],
        label_visibility="collapsed"
    )

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
            period = st.selectbox(
                "기간",
                options=[7, 30, 90, 180, 365],
                index=1,
                format_func=lambda x: f"{x}일"
            )
        with col2:
            time_unit = st.selectbox(
                "단위",
                options=['date', 'week', 'month'],
                format_func=lambda x: {'date': '일별', 'week': '주별', 'month': '월별'}[x]
            )

        st.markdown('<p class="menu-header">필터</p>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            device = st.selectbox(
                "디바이스",
                options=['', 'pc', 'mo'],
                format_func=lambda x: {'': '전체', 'pc': 'PC', 'mo': '모바일'}[x]
            )
        with col2:
            gender = st.selectbox(
                "성별",
                options=['', 'm', 'f'],
                format_func=lambda x: {'': '전체', 'm': '남', 'f': '여'}[x]
            )

        age_options = {
            '1': '0-12', '2': '13-18', '3': '19-24', '4': '25-29',
            '5': '30-34', '6': '35-39', '7': '40-44', '8': '45-49',
            '9': '50-54', '10': '55-59', '11': '60+'
        }

        ages = st.multiselect(
            "연령",
            options=list(age_options.keys()),
            format_func=lambda x: age_options[x],
            placeholder="전체"
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

# ===== 키워드 분석 페이지 =====
if menu == "네이버검색광고":
    st.markdown('<div class="header-box">', unsafe_allow_html=True)
    st.markdown("### 연관키워드 조회 기준")

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
            cols = st.columns([0.6, 2.5, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.7, 0.6])
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

        if st.session_state.selected:
            st.markdown('<div class="selected-box">', unsafe_allow_html=True)

            sel_col1, sel_col2 = st.columns([3, 1])
            with sel_col1:
                st.markdown(f"#### 선택한 키워드 ({len(st.session_state.selected)}개)")
            with sel_col2:
                if st.button("선택 초기화", use_container_width=True):
                    st.session_state.selected = set()
                    st.rerun()

            selected_df = df[df['연관키워드'].isin(st.session_state.selected)].drop(columns=['_총검색량'])
            kw_list = " | ".join([f"**{kw}**" for kw in st.session_state.selected])
            st.markdown(kw_list)

            st.markdown("---")

            exp_col1, exp_col2, _ = st.columns(3)
            with exp_col1:
                csv_selected = selected_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    "📥 선택 키워드 CSV",
                    csv_selected,
                    f"selected_keywords_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    "text/csv",
                    use_container_width=True
                )
            with exp_col2:
                keywords_only = '\n'.join(st.session_state.selected)
                st.download_button(
                    "📋 키워드만 TXT",
                    keywords_only,
                    "keywords.txt",
                    "text/plain",
                    use_container_width=True
                )

            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("키워드를 입력하고 '조회하기'를 클릭하세요.")


# ===== 트렌드 분석 페이지 =====
elif menu == "네이버데이터랩":
    st.markdown("### 📈 키워드 트렌드 분석")
    st.markdown("네이버 데이터랩 API를 통해 키워드별 검색 트렌드를 확인합니다.")

    # 트렌드 조회 실행
    if 'trend_btn' in dir() and trend_btn and trend_keywords.strip():
        keywords = [k.strip() for k in trend_keywords.split(',') if k.strip()][:5]
        with st.spinner("트렌드 조회 중..."):
            result = get_trend(
                keywords=keywords,
                days=period,
                time_unit=time_unit,
                device=device,
                gender=gender,
                ages=ages
            )
        if result:
            st.session_state.trend_df = format_trend_results(result)
            st.session_state.trend_keywords = keywords

    if st.session_state.trend_df is not None and len(st.session_state.trend_df) > 0:
        trend_df = st.session_state.trend_df

        st.markdown('<div class="result-box">', unsafe_allow_html=True)

        # 그래프
        st.markdown("#### 검색 트렌드 그래프")

        # Pivot for chart
        pivot_df = trend_df.pivot(index='날짜', columns='키워드', values='검색지수')

        # Streamlit 차트 (브랜드 컬러 적용)
        st.line_chart(
            pivot_df,
            use_container_width=True,
            color=[COLORS['primary'], COLORS['secondary'], '#34a853', '#ea4335', '#fbbc05'][:len(pivot_df.columns)]
        )

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
