# 네이버 키워드 분석 도구 v2 - 설계 문서

> 작성일: 2026-01-24
> 최종 업데이트: 2026-02-02
> 상태: **개발 중** (v3.9 온보딩 페이지 + 사이드바 아이콘)

---

## 현재 진행 상황

### 완료된 기능
- [x] Streamlit 웹앱 기본 구조
- [x] 네이버 검색광고 API 연동 (연관키워드 조회)
- [x] 네이버 데이터랩 API 연동 (트렌드 분석)
- [x] 2단 테이블 헤더 (PC/모바일 그룹핑)
- [x] 키워드 선택 및 CSV 내보내기
- [x] 트렌드 그래프 표시
- [x] 사이드바 메뉴 (네이버검색광고/네이버데이터랩)
- [x] 브랜드 컬러 적용

#### v3.1 업데이트 (2026-01-31)
- [x] 네이버 데이터랩 트렌드 버튼 로직 수정 (dir() 체크 제거)
- [x] 사이드바 입력 텍스트 색상 수정 (흰색→검정색)
- [x] 기간 옵션 변경: 1개월, 3개월, 1년, 직접입력
- [x] 직접입력 시 달력으로 시작일/종료일 선택 기능
- [x] 단위 옵션: 일/주/월
- [x] UI 라벨 변경 (디바이스→선택, 연령→범위)
- [x] 전체 연령 선택 체크박스 추가
- [x] 달력 요일 헤더 한글화 (일/월/화/수/목/금/토)

#### v3.2 업데이트 (2026-01-31)
- [x] 트렌드 데이터 날짜 정렬 수정 (datetime 변환으로 시간순 정렬)
- [x] Altair 차트로 변경 (Streamlit 기본 차트 → Altair)
- [x] 툴팁 커스터마이징 (날짜: "2025. 01. 31." 형식, 검색지수: 정수)
- [x] 차트 레전드 키워드 잘림 수정 (labelLimit=200)
- [x] 호버 시에만 포인트 표시 (alt.selection_point 활용)
- [x] API 요청 정보 디버깅 표시 (기간, 단위, 키워드)
- [x] 최고점 날짜 표시 (각 키워드별 최대값 확인용)

#### v3.3 업데이트 (2026-01-31)
- [x] 사이드바 하단 UI 요소 텍스트 색상 수정 (Selectbox, Multiselect, Checkbox, DateInput 등)
- [x] 드롭다운 메뉴 스타일링 (흰 배경 + 검정 텍스트)
- [x] 키워드 테이블 컬럼 너비 조정 (키워드 컬럼 확대: 2.5 → 3.5)

#### v3.4 업데이트 (2026-01-31)
- [x] "선택한 키워드" → "연동 키워드"로 명칭 변경
- [x] 저장 버튼: 히스토리에 날짜·시간과 함께 저장
- [x] 분석진행 버튼: 팝업(Dialog) 열림 → 옵션 선택 → 트렌드 조회 실행
- [x] 분석 옵션 팝업: 기간, 단위, 디바이스, 성별 선택 가능
- [x] 분석 완료 시 같은 페이지에서 트렌드 그래프 표시
- [x] 히스토리: 저장됨/분석완료 상태 구분, 불러오기 기능

#### v3.5 업데이트 (2026-02-01)
- [x] 사이드바에 "광고 운영 현황" 메뉴 추가
- [x] 네이버 검색광고 API 캠페인/광고그룹/키워드 조회 함수 구현
- [x] 비즈머니 잔액 조회 및 표시
- [x] 캠페인 목록 테이블 (상태, 유형, 일 예산)
- [x] 캠페인 선택 시 광고그룹 드릴다운 조회
- [x] 광고그룹 선택 시 키워드 목록 조회
- [x] 키워드별 입찰가, 품질지수, 매칭타입 표시
- [x] 키워드 CSV 다운로드 기능

#### v3.6 업데이트 (2026-02-01)
- [x] 캠페인 목록에서 캠페인명 클릭 시 상세 페이지로 전환
- [x] 캠페인 상세 페이지 UI 구현 (네이버 검색광고 관리 시스템 스타일)
  - [x] "← 모든 캠페인" 뒤로 가기 버튼
  - [x] 캠페인 정보 패널 (상태, 유형, 일 예산)
  - [x] 성과 그래프 (노출수/클릭수/비용/CTR 선택 가능)
  - [x] 기간 선택 (7일/14일/30일)
  - [x] 기간별 요약 지표 (총 노출수, 클릭수, 비용, 평균 CTR)
- [x] 광고그룹 자동 로드 (캠페인 상세 진입 시)
- [x] 광고그룹명 클릭 시 키워드 목록 조회
- [x] 키워드 닫기 기능
- [x] 통계 API 함수 개선 (`get_stat_report`, `get_daily_stats`)

#### v3.7 업데이트 (2026-02-01)
- [x] DESIGN_GUIDE.md 기반 디자인 시스템 적용
- [x] 4색 컬러 팔레트 적용
  - Background: `#F0EFEA`
  - Primary: `#1a1a1a` (사이드바, 텍스트)
  - Accent: `#6366F1` (CTA, 활성 상태)
  - Success: `#10B981` (긍정 지표)
- [x] 사이드바 스타일 업데이트 (인디고 활성 메뉴)
- [x] 버튼 호버 애니메이션 (`translateY(-1px)`)
- [x] 카드/테이블 미니멀 스타일 (subtle border)
- [x] Altair 차트 컬러 통일 (`CHART_COLORS`)
- [x] 메트릭 스타일 (32px, font-weight: 300)
- [x] 연동 키워드 바/분석 조건 바 스타일 개선
- [x] 비즈머니 패널/캠페인 상세 뷰 스타일 개선

#### v3.8 업데이트 (2026-02-01)
- [x] 사이드바 메뉴 구조 개선 - NAVER 그룹핑
  - 그룹 헤더: "NAVER"
  - 하위 메뉴: 연관키워드, 트렌드 분석, 광고 현황
- [x] 메뉴 이름 간소화 (네이버 접두어 제거)
  - "네이버 검색광고" → "연관키워드"
  - "네이버데이터랩" → "트렌드 분석"
  - "광고 운영 현황" → "광고 현황"
- [x] 하위 메뉴 스타일 적용
  - 들여쓰기 (padding-left: 36px)
  - 좌측 border 인디케이터
  - 호버 시 subtle 배경 + border 색상 변경
  - 선택 시 인디고 배경 + border

#### v3.9 업데이트 (2026-02-02)
- [x] 온보딩 페이지 구현 (Apple 스타일)
  - "Hello." 그라데이션 애니메이션 (인디고 → 그린 무한 반복)
  - fadeInUp 애니메이션으로 순차 등장
  - 사용자 정보 입력 폼 (이름, 직업, 직무, 연령대)
  - 건너뛰기 옵션
  - 온보딩 완료 시 세션 상태 저장
- [x] 사이드바 메뉴 아이콘 추가
  - 🔗 연관키워드
  - 📈 트렌드 분석
  - 📊 광고 현황
- [x] 사이드바 접힘 시 아이콘만 표시되도록 CSS 스타일링

### 남은 이슈
- [ ] 일반 브라우저 캐시 문제 (시크릿 모드에서는 정상 작동)
- [ ] 정렬 기능 확인 필요
- [ ] 경쟁정도 필터 값 확인

### 참고사항 (데이터랩 API)
- 네이버 데이터랩 API는 **상대지수**를 반환 (기준값 100)
- 조회 조건(기간, 단위, 비교 키워드)이 다르면 값도 달라짐
- 웹사이트와 동일한 값을 얻으려면 동일한 조건으로 조회 필요

### 실행 방법
```bash
cd ~/.claude/skills/keyword-analyzer
streamlit run app.py --server.port 8501
```

### 파일 위치
- 앱: `.claude/skills/keyword-analyzer/app.py`
- 의존성: `.claude/skills/keyword-analyzer/requirements.txt`
- API 키: `.claude/skills/gsheet-handler/scripts/.env`
- 디자인 가이드: `10-projects/13-performance-marketing/DESIGN_GUIDE.md`

---

## 개요

네이버 검색광고 API를 활용한 키워드 분석 도구.
기존 gsheet-handler 스킬의 키워드 분석 기능을 확장하여 **키워드 선택 기능** 추가.

## 요구사항

1. 키워드 입력 → 연관 키워드 조회
2. 네이버 키워드 도구처럼 테이블로 결과 표시
   - 키워드, PC검색량, 모바일검색량, PC클릭수, 모바일클릭수, PC클릭률, 모바일클릭률, 경쟁정도, 노출광고수
3. 각 키워드에 "추가" 버튼 → 클릭하면 "선택한 키워드" 목록에 추가
4. 선택한 키워드만 저장/내보내기

## 활용 시나리오

- **터미널 CLI**: Claude 서브에이전트로 자동화
- **웹 앱**: 브라우저에서 직접 사용
- **Google Sheets**: 템플릿으로 활용

---

## 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                    Core Layer (Python)                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│  │  models.py  │ │ naver_api.py│ │ analyzer.py │        │
│  │ 데이터 모델  │ │ API 클라이언트│ │ 분석 서비스  │        │
│  └─────────────┘ └─────────────┘ └─────────────┘        │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   Adapter Layer                          │
│  ┌─────────────────┐ ┌─────────────────┐                │
│  │ gsheet_adapter  │ │  json_adapter   │                │
│  │ 구글 시트 저장   │ │ JSON 출력       │                │
│  └─────────────────┘ └─────────────────┘                │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                     UI Layer                             │
│  ┌──────────┐  ┌──────────────┐  ┌─────────────┐        │
│  │   CLI    │  │  Streamlit   │  │ Apps Script │        │
│  │ 터미널    │  │   웹 앱      │  │ Google Sheet│        │
│  └──────────┘  └──────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────┘
```

---

## 파일 구조

```
.claude/skills/keyword-analyzer/
├── SKILL.md                      # 스킬 문서 (Claude 참조)
├── requirements.txt              # Python 의존성
│
├── keyword_analyzer/             # Python 패키지
│   ├── __init__.py
│   │
│   ├── core/                     # 핵심 로직 (플랫폼 무관)
│   │   ├── __init__.py
│   │   ├── models.py            # 데이터 모델 (KeywordStats)
│   │   ├── naver_api.py         # API 클라이언트 클래스
│   │   └── analyzer.py          # 분석 서비스
│   │
│   ├── adapters/                 # 출력 어댑터
│   │   ├── __init__.py
│   │   ├── base.py              # 어댑터 인터페이스
│   │   ├── gsheet_adapter.py    # 구글 시트 저장
│   │   └── json_adapter.py      # JSON 출력
│   │
│   ├── cli/                      # CLI 인터페이스
│   │   ├── __init__.py
│   │   └── main.py              # CLI 엔트리포인트
│   │
│   └── web/                      # 웹 인터페이스
│       └── app.py               # Streamlit 앱
│
├── apps_script/                  # Google Sheets 스크립트 (기존 유지)
│   ├── Code.gs
│   └── Config.gs
│
└── .env.example                  # 환경변수 템플릿
```

---

## 핵심 모듈 설계

### 1. 데이터 모델 (core/models.py)

```python
from dataclasses import dataclass, field
from typing import List
from datetime import datetime

@dataclass
class KeywordStats:
    """키워드 통계 데이터 모델"""
    keyword: str
    pc_search_volume: int
    mobile_search_volume: int
    total_search_volume: int
    pc_click_count: float
    mobile_click_count: float
    pc_ctr: float
    mobile_ctr: float
    competition_level: str  # "높음", "중간", "낮음"
    ad_exposure_count: float
    collected_at: datetime = field(default_factory=datetime.now)

    @property
    def is_golden_keyword(self) -> bool:
        """황금 키워드: 검색량 높고 경쟁 낮음"""
        return (self.total_search_volume >= 1000 and
                self.competition_level in ["낮음", "중간"])

@dataclass
class KeywordAnalysisResult:
    """분석 결과 컨테이너"""
    query_keywords: List[str]
    results: List[KeywordStats]
    include_related: bool
    collected_at: datetime = field(default_factory=datetime.now)
```

### 2. API 클라이언트 (core/naver_api.py)

```python
@dataclass
class NaverAdAPIConfig:
    access_license: str
    secret_key: str
    customer_id: str
    base_url: str = "https://api.searchad.naver.com"

class NaverSearchAdClient:
    """네이버 검색광고 API 클라이언트"""

    @classmethod
    def from_env(cls) -> 'NaverSearchAdClient':
        """환경변수에서 설정 로드"""
        ...

    def get_keyword_stats(self, keywords: List[str],
                         include_related: bool = False) -> dict:
        """키워드 통계 조회"""
        ...
```

### 3. 분석 서비스 (core/analyzer.py)

```python
class KeywordAnalyzer:
    """키워드 분석 서비스"""

    def analyze(self, keywords: List[str],
                include_related: bool = False) -> KeywordAnalysisResult:
        """키워드 분석 실행"""
        ...
```

---

## CLI 사용법

```bash
# 기본 분석
python -m keyword_analyzer.cli.main analyze "침대,소파" --include-related

# JSON 출력 (Claude 서브에이전트용)
python -m keyword_analyzer.cli.main analyze "침대" --output json

# 구글 시트 저장
python -m keyword_analyzer.cli.main analyze "침대" --sheet "URL" --tab "키워드분석"
```

---

## Streamlit 웹앱 UI

```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 네이버 키워드 분석 도구                                    │
├──────────────┬──────────────────────────────┬───────────────┤
│ [사이드바]    │ [메인 영역]                   │ [우측 패널]   │
│              │                              │              │
│ 키워드 입력   │ 📊 분석 결과 (196개)          │ 📋 선택한    │
│ ┌──────────┐ │                              │    키워드    │
│ │침대      │ │ ☐ 키워드    PC   모바일  경쟁 │              │
│ │소파      │ │ ☑ 침대     150   180   높음  │ - 침대 (330) │
│ │          │ │ ☐ 침대커버  90    40   낮음  │ - 소파 (690) │
│ └──────────┘ │ ☑ 소파     190   500   높음  │              │
│              │ ☐ 소파베드  50    350   중간  │ ──────────── │
│ ☑ 연관키워드 │                              │ 💾 내보내기  │
│   포함       │                              │ [구글 시트]  │
│              │                              │ [CSV 다운로드]│
│ [🔍 분석]    │                              │              │
└──────────────┴──────────────────────────────┴───────────────┘
```

---

## 기능 비교

| 기능 | CLI | 웹앱 | Sheets |
|------|:---:|:----:|:------:|
| 연관 키워드 조회 | ✅ | ✅ | ✅ |
| 결과 테이블 표시 | ✅ | ✅ | ✅ |
| 키워드 선택 | ❌ | ✅ | ✅ |
| 구글 시트 저장 | ✅ | ✅ | ✅ |
| CSV 다운로드 | ❌ | ✅ | ❌ |
| 황금키워드 표시 | ✅ | ✅ | ✅ |

---

## 의존성

```
# requirements.txt
python-dotenv>=1.0.0
gspread>=5.0.0
google-auth-oauthlib>=1.0.0
streamlit>=1.30.0
pandas>=2.0.0
altair>=5.0.0
```

---

## 구현 순서

### Phase 1: 코어 리팩토링
1. `core/models.py` - 데이터 모델 정의
2. `core/naver_api.py` - 기존 naver_searchad.py에서 API 로직 분리
3. `core/analyzer.py` - 분석 서비스

### Phase 2: 어댑터 구현
1. `adapters/gsheet_adapter.py` - 기존 gsheet_api.py 활용
2. `adapters/json_adapter.py` - CLI용 JSON 출력

### Phase 3: CLI 개선
1. `cli/main.py` - 새 CLI 엔트리포인트
2. JSON 출력 모드 추가

### Phase 4: Streamlit 웹앱
1. `web/app.py` - 기본 UI
2. 키워드 테이블 + 체크박스
3. 선택 키워드 패널
4. 내보내기 기능

---

## 참조 파일

- 기존 API 구현: `.claude/skills/gsheet-handler/scripts/naver_searchad.py`
- 구글 시트 연동: `.claude/skills/gsheet-handler/scripts/gsheet_api.py`
- Apps Script: `.claude/skills/gsheet-handler/scripts/apps-script/Code.gs`

---

## 다음 단계

이 문서가 승인되면 Phase 1부터 순차적으로 구현 진행.
