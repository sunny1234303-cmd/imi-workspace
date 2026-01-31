# 네이버 키워드 분석 도구 v2 - 설계 문서

> 작성일: 2026-01-24
> 최종 업데이트: 2026-01-31
> 상태: **개발 중** (v3 프로토타입 완료)

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

### 남은 이슈
- [ ] 일반 브라우저 캐시 문제 (시크릿 모드에서는 정상 작동)
- [ ] 정렬 기능 확인 필요
- [ ] 경쟁정도 필터 값 확인

### 실행 방법
```bash
cd ~/.claude/skills/keyword-analyzer
streamlit run app.py --server.port 8501
```

### 파일 위치
- 앱: `.claude/skills/keyword-analyzer/app.py`
- 의존성: `.claude/skills/keyword-analyzer/requirements.txt`
- API 키: `.claude/skills/gsheet-handler/scripts/.env`

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
