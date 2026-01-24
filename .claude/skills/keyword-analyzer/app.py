#!/usr/bin/env python3
"""
네이버 키워드 분석 도구 - Streamlit 프로토타입 v2

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
from datetime import datetime
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
BASE_URL = "https://api.searchad.naver.com"


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
        st.error("API 키가 설정되지 않았습니다.")
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

    url = BASE_URL + uri + '?' + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, method='GET', headers=headers)

    try:
        response = urllib.request.urlopen(request)
        return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        st.error(f"API 오류: {e.code}")
        return None


def parse_volume(value):
    if isinstance(value, str):
        return 10 if '< 10' in value else int(value.replace(',', ''))
    return value or 0


def normalize_competition(comp):
    """경쟁정도 정규화"""
    if not comp or comp == '-':
        return '낮음'
    comp = str(comp).strip()
    # 영문 → 한글 변환
    mapping = {
        'HIGH': '높음', 'high': '높음', '높음': '높음',
        'MEDIUM': '중간', 'medium': '중간', '중간': '중간', '보통': '중간',
        'LOW': '낮음', 'low': '낮음', '낮음': '낮음',
    }
    return mapping.get(comp, '낮음')


def format_results(api_result):
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
    # 총검색량 기준 내림차순 정렬 (확실하게)
    df = df.sort_values(by='_총검색량', ascending=False, ignore_index=True)
    return df


# 페이지 설정
st.set_page_config(page_title="키워드 분석 도구", page_icon="🔍", layout="wide")

# CSS 스타일
st.markdown("""
<style>
    .main > div { padding-top: 1rem; }
    .stApp { background-color: #f8f9fa; }

    /* 헤더 스타일 */
    .header-box {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 16px;
    }

    /* 결과 테이블 컨테이너 */
    .result-box {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 20px;
    }

    /* 선택 키워드 박스 */
    .selected-box {
        background: #f0f7ff;
        border: 1px solid #4A90D9;
        border-radius: 8px;
        padding: 16px;
        margin-top: 16px;
    }

    /* 버튼 스타일 */
    .stButton > button {
        font-size: 13px;
    }

    div[data-testid="stHorizontalBlock"] {
        align-items: center;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태
if 'results_df' not in st.session_state:
    st.session_state.results_df = None
if 'selected' not in st.session_state:
    st.session_state.selected = set()

# ===== 상단: 검색 영역 =====
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

# 검색 실행
if search_btn and keywords_input.strip():
    keywords = [k.strip() for k in keywords_input.replace('\n', ',').split(',') if k.strip()][:5]
    with st.spinner("조회 중..."):
        result = get_keyword_stats(keywords, include_related)
    if result:
        st.session_state.results_df = format_results(result)
        st.session_state.selected = set()

# ===== 결과 영역 =====
if st.session_state.results_df is not None and len(st.session_state.results_df) > 0:
    df = st.session_state.results_df

    st.markdown('<div class="result-box">', unsafe_allow_html=True)

    # 상단 바: 결과 개수 + 버튼들
    top_col1, top_col2, top_col3, top_col4 = st.columns([3, 1, 1, 1])
    with top_col1:
        st.markdown(f"#### 연관키워드 조회 결과 ({len(df)}개)")
    with top_col2:
        if st.button("전체추가", use_container_width=True):
            st.session_state.selected = set(df['연관키워드'].tolist())
            st.rerun()
    with top_col3:
        # CSV 다운로드
        csv = df.drop(columns=['_총검색량']).to_csv(index=False, encoding='utf-8-sig')
        st.download_button("다운로드", csv, "keywords.csv", "text/csv", use_container_width=True)
    with top_col4:
        filter_comp = st.selectbox("경쟁정도", ["전체", "높음", "중간", "낮음"], label_visibility="collapsed")

    # 필터 적용
    if filter_comp != "전체":
        df = df[df['경쟁정도'] == filter_comp]

    st.markdown("---")

    # 테이블 헤더
    header = st.columns([0.6, 2.5, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.7, 0.6])
    header[0].markdown("**　**")
    header[1].markdown("**연관키워드**")
    header[2].markdown("**PC**")
    header[3].markdown("**모바일**")
    header[4].markdown("**PC클릭**")
    header[5].markdown("**모바일**")
    header[6].markdown("**PC CTR**")
    header[7].markdown("**모바일**")
    header[8].markdown("**경쟁**")
    header[9].markdown("**광고**")

    # 데이터 행
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

    # ===== 선택한 키워드 영역 =====
    if st.session_state.selected:
        st.markdown('<div class="selected-box">', unsafe_allow_html=True)

        sel_col1, sel_col2 = st.columns([3, 1])
        with sel_col1:
            st.markdown(f"#### 선택한 키워드 ({len(st.session_state.selected)}개)")
        with sel_col2:
            if st.button("선택 초기화", use_container_width=True):
                st.session_state.selected = set()
                st.rerun()

        # 선택한 키워드 데이터
        selected_df = df[df['연관키워드'].isin(st.session_state.selected)].drop(columns=['_총검색량'])

        # 키워드 목록 표시
        kw_list = " | ".join([f"**{kw}**" for kw in st.session_state.selected])
        st.markdown(kw_list)

        st.markdown("---")

        # 내보내기
        exp_col1, exp_col2, exp_col3 = st.columns(3)
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
