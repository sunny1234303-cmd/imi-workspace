#!/usr/bin/env python3
"""
네이버 키워드 분석 도구 - Streamlit 프로토타입

실행: streamlit run app.py
"""

import os
import sys
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
    # 대체 경로 시도
    alt_path = Path('/Users/seoni/imi-workspace/.claude/skills/gsheet-handler/scripts/.env')
    load_dotenv(alt_path)

# API 설정
NAVER_AD_ACCESS_LICENSE = os.getenv('NAVER_AD_ACCESS_LICENSE')
NAVER_AD_SECRET_KEY = os.getenv('NAVER_AD_SECRET_KEY')
NAVER_AD_CUSTOMER_ID = os.getenv('NAVER_AD_CUSTOMER_ID')
BASE_URL = "https://api.searchad.naver.com"

# 브랜드 컬러 (personal-branding-guide.md)
COLORS = {
    'primary': '#1E3A5F',      # 네이비 블루
    'secondary': '#4A90D9',    # 스카이 블루
    'background': '#FFFFFF',   # 화이트
    'text': '#333333',         # 다크 그레이
}


def generate_signature(timestamp, method, uri):
    """HMAC-SHA256 서명 생성"""
    message = f"{timestamp}.{method}.{uri}"
    signature = hmac.new(
        NAVER_AD_SECRET_KEY.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode('utf-8')


def get_keyword_stats(keywords, include_related=False):
    """네이버 검색광고 API 호출"""
    if not all([NAVER_AD_ACCESS_LICENSE, NAVER_AD_SECRET_KEY, NAVER_AD_CUSTOMER_ID]):
        st.error("API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")
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
        st.error(f"API 오류: {e.code} - {e.read().decode('utf-8')}")
        return None


def parse_volume(value):
    """검색량 파싱 ("< 10" 처리)"""
    if isinstance(value, str):
        return 10 if '< 10' in value else int(value.replace(',', ''))
    return value or 0


def format_results(api_result):
    """API 결과를 DataFrame으로 변환"""
    if not api_result or 'keywordList' not in api_result:
        return pd.DataFrame()

    data = []
    for kw in api_result['keywordList']:
        pc_qc = parse_volume(kw.get('monthlyPcQcCnt', 0))
        mo_qc = parse_volume(kw.get('monthlyMobileQcCnt', 0))

        data.append({
            '키워드': kw.get('relKeyword', ''),
            'PC검색량': pc_qc,
            '모바일검색량': mo_qc,
            '총검색량': pc_qc + mo_qc,
            'PC클릭수': round(float(kw.get('monthlyAvePcClkCnt', 0) or 0), 1),
            '모바일클릭수': round(float(kw.get('monthlyAveMobileClkCnt', 0) or 0), 1),
            'PC클릭률': round(float(kw.get('monthlyAvePcCtr', 0) or 0), 2),
            '모바일클릭률': round(float(kw.get('monthlyAveMobileCtr', 0) or 0), 2),
            '경쟁정도': kw.get('compIdx', '-'),
            '노출광고수': int(float(kw.get('plAvgDepth', 0) or 0)),
        })

    return pd.DataFrame(data)


# 페이지 설정
st.set_page_config(
    page_title="키워드 분석 도구",
    page_icon="🔍",
    layout="wide"
)

# 커스텀 CSS
st.markdown(f"""
<style>
    .stApp {{
        background-color: {COLORS['background']};
    }}
    h1, h2, h3 {{
        color: {COLORS['primary']} !important;
    }}
    .stButton > button {{
        background-color: {COLORS['secondary']};
        color: white;
        border: none;
    }}
    .stButton > button:hover {{
        background-color: {COLORS['primary']};
    }}
    .selected-keyword {{
        background-color: #E3F2FD;
        padding: 8px 12px;
        border-radius: 4px;
        margin: 4px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .add-btn {{
        background-color: {COLORS['secondary']};
        color: white;
        border: none;
        padding: 4px 12px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
    }}
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'results_df' not in st.session_state:
    st.session_state.results_df = None
if 'selected_keywords' not in st.session_state:
    st.session_state.selected_keywords = []

# 헤더
st.title("🔍 네이버 키워드 분석 도구")

# 레이아웃: 3열
col_input, col_results, col_selected = st.columns([1, 2.5, 1.5])

# 왼쪽: 입력 패널
with col_input:
    st.subheader("키워드 입력")

    keywords_input = st.text_area(
        "분석할 키워드",
        placeholder="침대\n소파\n책상",
        height=120,
        help="쉼표 또는 줄바꿈으로 구분 (최대 5개)"
    )

    include_related = st.checkbox("연관 키워드 포함", value=True)

    if st.button("🔍 분석 시작", type="primary", use_container_width=True):
        if keywords_input.strip():
            keywords = [k.strip() for k in keywords_input.replace('\n', ',').split(',') if k.strip()][:5]

            with st.spinner("분석 중..."):
                result = get_keyword_stats(keywords, include_related)

            if result:
                st.session_state.results_df = format_results(result)
                st.success(f"{len(st.session_state.results_df)}개 키워드 분석 완료")
        else:
            st.warning("키워드를 입력하세요")

# 중앙: 결과 테이블
with col_results:
    if st.session_state.results_df is not None and len(st.session_state.results_df) > 0:
        df = st.session_state.results_df

        st.subheader(f"연관키워드 조회 결과 ({len(df)}개)")

        # 필터
        col_filter1, col_filter2 = st.columns(2)
        with col_filter1:
            comp_filter = st.multiselect(
                "경쟁정도",
                options=['높음', '중간', '낮음'],
                default=['높음', '중간', '낮음']
            )
        with col_filter2:
            sort_by = st.selectbox(
                "정렬",
                options=['총검색량', 'PC검색량', '모바일검색량', '경쟁정도'],
                index=0
            )

        # 필터 적용
        filtered_df = df[df['경쟁정도'].isin(comp_filter)]
        if sort_by == '경쟁정도':
            order = {'높음': 0, '중간': 1, '낮음': 2}
            filtered_df = filtered_df.sort_values(by='경쟁정도', key=lambda x: x.map(order))
        else:
            filtered_df = filtered_df.sort_values(by=sort_by, ascending=False)

        # 테이블 표시 (행별로)
        st.markdown("---")

        # 헤더
        header_cols = st.columns([0.8, 2, 1, 1, 1, 1, 1, 1])
        headers = ['', '키워드', 'PC검색량', '모바일', 'PC클릭수', '모바일', '경쟁정도', '광고수']
        for col, header in zip(header_cols, headers):
            col.markdown(f"**{header}**")

        # 데이터 행
        for idx, row in filtered_df.iterrows():
            cols = st.columns([0.8, 2, 1, 1, 1, 1, 1, 1])

            # 추가 버튼
            kw = row['키워드']
            is_selected = kw in st.session_state.selected_keywords

            with cols[0]:
                if is_selected:
                    st.markdown("✅")
                else:
                    if st.button("추가", key=f"add_{idx}", type="secondary"):
                        if kw not in st.session_state.selected_keywords:
                            st.session_state.selected_keywords.append(kw)
                            st.rerun()

            cols[1].write(kw)
            cols[2].write(f"{row['PC검색량']:,}")
            cols[3].write(f"{row['모바일검색량']:,}")
            cols[4].write(f"{row['PC클릭수']}")
            cols[5].write(f"{row['모바일클릭수']}")

            # 경쟁정도 색상
            comp = row['경쟁정도']
            if comp == '높음':
                cols[6].markdown(f"🔴 {comp}")
            elif comp == '중간':
                cols[6].markdown(f"🟡 {comp}")
            else:
                cols[6].markdown(f"🟢 {comp}")

            cols[7].write(f"{row['노출광고수']}")

    else:
        st.info("왼쪽에서 키워드를 입력하고 분석을 시작하세요.")

# 오른쪽: 선택한 키워드
with col_selected:
    st.subheader("📋 선택한 키워드")
    st.caption(f"{len(st.session_state.selected_keywords)}개 선택됨")

    if st.session_state.selected_keywords:
        # 선택한 키워드 목록
        for kw in st.session_state.selected_keywords:
            col_kw, col_del = st.columns([4, 1])

            # 선택한 키워드 정보 표시
            if st.session_state.results_df is not None:
                kw_data = st.session_state.results_df[st.session_state.results_df['키워드'] == kw]
                if len(kw_data) > 0:
                    vol = kw_data.iloc[0]['총검색량']
                    col_kw.markdown(f"**{kw}** ({vol:,})")
                else:
                    col_kw.markdown(f"**{kw}**")
            else:
                col_kw.markdown(f"**{kw}**")

            # 삭제 버튼
            if col_del.button("❌", key=f"del_{kw}"):
                st.session_state.selected_keywords.remove(kw)
                st.rerun()

        st.markdown("---")

        # 전체 삭제
        if st.button("전체 삭제", use_container_width=True):
            st.session_state.selected_keywords = []
            st.rerun()

        st.markdown("---")

        # 내보내기 옵션
        st.subheader("💾 내보내기")

        # CSV 다운로드
        if st.session_state.results_df is not None:
            selected_df = st.session_state.results_df[
                st.session_state.results_df['키워드'].isin(st.session_state.selected_keywords)
            ]

            csv = selected_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                "📥 CSV 다운로드",
                csv,
                f"keywords_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                "text/csv",
                use_container_width=True
            )

            # 클립보드 복사용 텍스트
            keywords_text = '\n'.join(st.session_state.selected_keywords)
            st.text_area("키워드 복사", keywords_text, height=100)

    else:
        st.caption("왼쪽 테이블에서 '추가' 버튼을 클릭하여\n키워드를 선택하세요.")
