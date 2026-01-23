# 퍼포먼스 마케팅 자동화

**생성일**: 2026-01-22
**상태**: 구현 중 (Phase 1)

---

## 프로젝트 개요

### 핵심 컨셉
- **내부 광고 데이터는 대외비** → Claude가 직접 분석 불가
- **외부 객관적 근거 수집** → 자동화 가능
- 수집된 근거를 내부 분석의 비교 기준/맥락으로 활용

### 데이터 흐름
```
[외부 객관적 근거 수집] ──→ [구글 시트 저장] ──→ [내부 분석 시 참고]
      (자동화)                 (자동)               (수동, 대외비)
```

---

## 업무별 자동화 분류

### 완전 자동화 가능 (3개)

| 업무 | 도구 | 방법 |
|------|------|------|
| 연령별 타깃팅 메시지 | Claude + gspread | 페르소나 시트 → AI 메시지 생성 |
| 디지털 캠페인 성과 트래킹 | gspread + Claude | CSV 업로드 → 자동 분석 |
| 콘텐츠 인사이트 발굴 | competitor-review-analyzer | 리뷰 크롤링 → 감성 분석 |

### 부분 자동화 가능 (8개)

| 업무 | 자동화 범위 | 수동 처리 |
|------|------------|----------|
| 트렌드 분석 | 데이터 수집 | 전략적 해석 |
| 사업계획서 작성 | 초안 생성 | 최종 검토 |
| IMC 캠페인 플랜 | 프레임워크 생성 | 예산/협업 조율 |
| 카카오톡 채널 광고 | 메시지 초안 | 플랫폼 설정 |
| 브랜드 콘텐츠 기획 | 아이디어 생성 | 크리에이티브 디렉션 |
| 인플루언서 관리 | DB + 메시지 초안 | 직접 컨택 |
| 숏폼 콘텐츠 기획 | 트렌드 분석 | 영상 제작 |
| 채널 모니터링 | 데이터 수집 | 전략적 판단 |

### 자동화 불가 (2개)

| 업무 | 사유 | 대안 |
|------|------|------|
| 브랜드 가치 설계 | 전략적 판단 필요 | `/thinking-partner` 활용 |
| 디즈니 캠페인 | 대외비 | 로컬 전용 처리 |

---

## 1차 구현: 외부 근거 수집 시스템

### 수집 대상 데이터

| 데이터 유형 | 소스 | 용도 |
|------------|------|------|
| 키워드 검색량 | 네이버/구글 | 타깃 키워드 선정 근거 |
| 검색 트렌드 | 네이버 데이터랩 | 시즌/트렌드 파악 |
| 업종 벤치마크 | 업계 리포트 | CTR/CPC 비교 기준 |
| 경쟁사 광고 | Meta Ad Library | 경쟁사 메시지/소재 참고 |

### 사용 예시

```
"가구 키워드 트렌드 수집해줘"
→ 네이버 데이터랩 검색량 수집
→ 구글 시트 저장 + 로컬 백업
→ "침대 검색량 15% 증가, 책상 5% 감소"
```

```
"경쟁사 한샘 광고 확인해줘"
→ Meta Ad Library 검색
→ 구글 시트 저장
→ "무료 설치 강조, 25-44세 타깃, 캐러셀 형식"
```

---

## 구현 계획

### Phase 1: 구글 시트 연동 ✅ 완료
- [x] 프로젝트 폴더 생성
- [x] gsheet-handler 스킬 생성
- [x] gsheet_api.py (읽기/쓰기/탭 관리)

### Phase 2: 네이버 API 연동 ✅ 완료
- [x] naver_datalab.py (검색 트렌드 API)
- [x] naver_searchad.py (검색광고 키워드 도구 API)
- [x] API 키 설정 완료 (.env)

### Phase 3: 구글 시트 UI ✅ 완료
- [x] Apps Script 메뉴 (키워드 분석)
- [x] 분석 다이얼로그 (키워드 입력, 옵션)
- [x] 대시보드 자동 생성 (필터, 요약, TOP 키워드)
- [x] 카테고리/수집일시 필터 드롭다운

### Phase 4: 개선 필요 (TODO)
- [ ] 공백 키워드 자동 처리 (현재 400 에러)
- [ ] 오류 메시지 구체화
- [ ] 구글 트렌드 연동
- [ ] Meta Ad Library 크롤링
- [ ] 자동 주간 수집

---

## 폴더 구조

```
10-projects/13-performance-marketing/
├── README.md                    # 이 파일
├── 01-setup/
│   ├── google-sheets-setup.md   # 구글 시트 설정
│   └── naver-api-setup.md       # 네이버 API 설정
├── 02-skills/
│   ├── gsheet-handler/          # 구글 시트 스킬
│   └── naver-datalab/           # 네이버 데이터랩 스킬
├── 03-data/
│   ├── trends/                  # 트렌드 데이터
│   ├── benchmarks/              # 벤치마크
│   └── competitor-ads/          # 경쟁사 광고
└── 04-reports/                  # 분석 리포트
```

---

## 연동 현황

| 항목 | 상태 | 비고 |
|------|------|------|
| 구글 시트 OAuth | ✅ 완료 | `~/.config/gspread/` |
| gsheet-handler 스킬 | ✅ 완료 | Python + Apps Script |
| 네이버 데이터랩 API | ✅ 완료 | 검색 트렌드 |
| 네이버 검색광고 API | ✅ 완료 | 키워드 검색량 |
| Apps Script UI | ✅ 완료 | 시트 내 메뉴 |
| 대시보드 | ✅ 완료 | 필터 + 자동 분석 |

---

## 보안 규칙

- **대외비 자료**: 로컬 전용, 클라우드 저장 금지
- **API 키**: `.env`로 관리, Git 추적 제외
- **수집 데이터**: 공개된 외부 데이터만 (개인정보 금지)

---

## 관련 파일

### 스킬 (Python)
```
.claude/skills/gsheet-handler/scripts/
├── gsheet_api.py       ← 구글 시트 API
├── naver_datalab.py    ← 네이버 데이터랩
├── naver_searchad.py   ← 네이버 검색광고
└── .env                ← API 키
```

### Apps Script (구글 시트 내장)
```
.claude/skills/gsheet-handler/scripts/apps-script/
├── Config.gs   ← API 설정
├── Code.gs     ← 메인 프로그램
└── README.md   ← 설치 가이드
```

### 문서
- `30-knowledge/32-marketing/gsheet-keyword-analyzer.md` - 상세 사용법
- `10-projects/13-performance-marketing/01-setup/sheet-analysis.md` - 시트 구조

### 구글 시트
- **URL**: https://docs.google.com/spreadsheets/d/1rJ1PD_IHEQNtaZhedJvyilNgRFE36tOl8yN66xhHq8k
- **탭**: Raw_키워드, Raw_트렌드, 키워드_대시보드
