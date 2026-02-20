# 구글 시트 키워드 분석 도구

## 개요
네이버 API를 활용한 키워드 분석 도구. 구글 시트에서 직접 분석 실행 가능.

## 구글 시트
- **URL**: https://docs.google.com/spreadsheets/d/1rJ1PD_IHEQNtaZhedJvyilNgRFE36tOl8yN66xhHq8k
- **탭 구조**:
  - `Raw_키워드`: 검색량 데이터 (네이버 검색광고 API)
  - `Raw_트렌드`: 트렌드 데이터 (네이버 데이터랩 API)
  - `키워드_대시보드`: 자동 분석 대시보드

## 파일 위치

### Apps Script (구글 시트 내장)
```
.claude/skills/gsheet-handler/scripts/apps-script/
├── Config.gs   ← API 설정 관리
├── Code.gs     ← 메인 프로그램
└── README.md   ← 설치 가이드
```

### Python 스크립트 (로컬 실행용)
```
.claude/skills/gsheet-handler/scripts/
├── gsheet_api.py       ← 구글 시트 읽기/쓰기
├── naver_datalab.py    ← 네이버 데이터랩 API
├── naver_searchad.py   ← 네이버 검색광고 API
└── .env                ← API 키 (git 제외)
```

## API 키 정보

### 네이버 데이터랩 API
- **용도**: 키워드 검색 트렌드 (상대적 검색지수)
- **발급**: https://developers.naver.com/apps
- **키**: NAVER_CLIENT_ID, NAVER_CLIENT_SECRET

### 네이버 검색광고 API
- **용도**: 월간 검색량, 경쟁강도, 클릭률
- **발급**: https://manage.searchad.naver.com (API 관리)
- **키**: NAVER_AD_ACCESS_LICENSE, NAVER_AD_SECRET_KEY, NAVER_AD_CUSTOMER_ID

## 현재 기능

### 구글 시트 메뉴
```
키워드 분석
├── 키워드 검색량 분석   ← 월간 검색량, 경쟁강도
├── 키워드 트렌드 분석   ← 일별 검색지수 추이
├── 대시보드 새로고침
└── API 설정
```

### 분석 옵션
- **카테고리**: 데이터 분류용 태그
- **연관 키워드 포함**: 입력 키워드 관련 키워드도 수집
- **기존 데이터 초기화**: 새 분석 시 이전 데이터 삭제

### 대시보드 기능 (키워드 대시보드 탭)
- 카테고리/수집일시 필터 드롭다운
- 핵심 요약 (총 키워드, 평균 검색량, 검색량 중앙값)
- 경쟁강도 분포 (높음/중간/낮음 비율)
- TOP 검색량 15
- 황금 키워드 (검색량↑ 경쟁↓) - TOP 검색량 하단에 배치
- 경쟁 높음 주의 키워드

## 알려진 이슈

### 공백 포함 키워드 오류
- **증상**: "내셔널지오그래픽 매거진" 같은 공백 포함 키워드 → 400 에러
- **원인**: 네이버 검색광고 API가 공백 키워드 미지원
- **해결 필요**: 공백 → 쉼표 자동 변환 또는 오류 메시지 개선

## 다음 작업 (TODO)

- [ ] 공백 키워드 자동 처리 (공백 → 쉼표 변환)
- [ ] 오류 메시지 구체화 (400 에러 시 "키워드에 공백 제거 필요" 안내)
- [ ] 트렌드 차트 시각화 (스파크라인 또는 미니 차트)

## 사용 예시

### 구글 시트에서
1. 메뉴: **키워드 분석** → **키워드 검색량 분석**
2. 키워드 입력: `스킨케어, 화장품` (쉼표 구분)
3. 카테고리: `뷰티`
4. **분석 시작** 클릭

### Python 스크립트
```bash
cd ~/.claude/skills/gsheet-handler/scripts

# 키워드 검색량
python3 naver_searchad.py keyword "스킨케어"

# 트렌드 분석
python3 naver_datalab.py trend "스킨케어" --days 30
```

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-01-24 | 대시보드 레이아웃 개선 (황금 키워드 → TOP 검색량 하단으로 이동) |
| 2026-01-24 | 키워드 대시보드 탭으로 통합 (Raw 탭에서 분리) |
| 2026-01-23 | Apps Script 분리 (Config.gs, Code.gs) |
| 2026-01-23 | 카테고리/수집일시 필터 추가 |
| 2026-01-23 | 기존 데이터 초기화 옵션 추가 |
| 2026-01-22 | 초기 버전 (Python 스크립트 + 구글 시트 연동) |
