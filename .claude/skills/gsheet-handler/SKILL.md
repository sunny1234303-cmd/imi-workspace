---
name: gsheet-handler
description: 구글 시트 읽기/쓰기 핸들러. "구글 시트", "스프레드시트", "시트에 저장", "시트에서 읽어", "gsheet" 등을 언급하면 자동 실행. 마케팅 데이터 수집/저장 파이프라인의 핵심.
allowed-tools: Bash, Read, Write
---

# 구글 시트 핸들러 스킬

구글 시트 읽기/쓰기/업데이트를 위한 범용 스킬.
기존 OAuth 인증 (~/.config/gspread/) 활용.

**전용 스크립트**: `scripts/gsheet_api.py`

---

## 기능 요약

| 명령 | 설명 | 예시 |
|------|------|------|
| `read` | 시트 읽기 | 전체 또는 특정 범위 |
| `write` | 시트 쓰기 | JSON → 시트 |
| `update` | 셀 업데이트 | 특정 셀 값 변경 |
| `append` | 행 추가 | 기존 데이터 뒤에 추가 |
| `create-tab` | 탭 생성 | 새 워크시트 생성 |
| `list-tabs` | 탭 목록 | 시트 구조 확인 |

---

## 사용법

### 1. 시트 읽기

```bash
cd /Users/seoni/imi-workspace/.claude/skills/gsheet-handler/scripts && \
python3 gsheet_api.py read "<SHEET_URL>" [--tab "탭이름"] [--range "A1:B10"]
```

**예시:**
```bash
python3 gsheet_api.py read "https://docs.google.com/spreadsheets/d/xxx" --tab "키워드트렌드"
```

### 2. 시트 쓰기 (JSON → 시트)

```bash
python3 gsheet_api.py write "<SHEET_URL>" <json_file> [--tab "탭이름"]
```

**JSON 형식 예시:**
```json
{
  "headers": ["키워드", "검색량", "수집일"],
  "rows": [
    ["침대", 15000, "2026-01-22"],
    ["책상", 8000, "2026-01-22"]
  ]
}
```

또는 리스트 형식:
```json
[
  {"키워드": "침대", "검색량": 15000},
  {"키워드": "책상", "검색량": 8000}
]
```

### 3. 행 추가 (Append)

기존 데이터 끝에 새 행 추가:
```bash
python3 gsheet_api.py append "<SHEET_URL>" <json_file> --tab "수집로그"
```

### 4. 특정 셀 업데이트

```bash
python3 gsheet_api.py update "<SHEET_URL>" --cell "A1" --value "새 값"
```

### 5. 새 탭 생성

```bash
python3 gsheet_api.py create-tab "<SHEET_URL>" --name "새탭이름" --rows 100 --cols 26
```

### 6. 탭 목록 조회

```bash
python3 gsheet_api.py list-tabs "<SHEET_URL>"
```

---

## 워크플로우 예시

### 예시 1: 키워드 트렌드 저장

```
사용자: "검색량 데이터 구글 시트에 저장해줘"

Claude:
1. 데이터를 JSON 파일로 저장 (/tmp/keyword_data.json)
2. gsheet_api.py write 실행
3. 시트 URL 반환
```

```bash
# 1. 데이터 준비
echo '[{"키워드": "침대", "검색량": 15000}]' > /tmp/keyword_data.json

# 2. 시트에 쓰기
python3 gsheet_api.py write "https://docs.google.com/spreadsheets/d/xxx" \
  /tmp/keyword_data.json --tab "키워드트렌드"
```

### 예시 2: 수집 로그 추가

```
사용자: "수집 로그 기록해줘"

Claude:
1. 로그 데이터 JSON 생성
2. append 명령으로 기존 로그에 추가
```

```bash
echo '{"시간": "2026-01-22 10:00", "작업": "키워드수집", "결과": "성공"}' > /tmp/log.json
python3 gsheet_api.py append "https://docs.google.com/spreadsheets/d/xxx" \
  /tmp/log.json --tab "수집로그"
```

### 예시 3: 시트 데이터 읽고 분석

```
사용자: "구글 시트에서 지난주 데이터 읽어줘"

Claude:
1. gsheet_api.py read 실행
2. JSON 결과 파싱
3. 분석 결과 제공
```

---

## 출력 형식

모든 명령은 JSON 형식으로 결과 반환:

```json
{
  "status": "success",
  "sheet_id": "xxx",
  "tab": "키워드트렌드",
  "rows_written": 10,
  "timestamp": "2026-01-22T10:00:00"
}
```

---

## 마케팅-외부근거 시트 구조

퍼포먼스 마케팅 프로젝트용 표준 시트:

| 탭 이름 | 용도 | 컬럼 예시 |
|---------|------|----------|
| 키워드트렌드 | 검색량/트렌드 | 키워드, 검색량, 변화율, 수집일 |
| 업종벤치마크 | CTR/CPC 기준 | 업종, 지표, 값, 출처, 날짜 |
| 경쟁사광고 | 광고 소재 수집 | 경쟁사, 플랫폼, 메시지, 타깃, URL |
| 수집로그 | 작업 기록 | 시간, 작업, 결과, 비고 |

---

## 트러블슈팅

### 인증 오류

```bash
# 토큰 갱신
rm ~/.config/gspread/authorized_user.json
python3 gsheet_api.py list-tabs "<SHEET_URL>"
# 브라우저에서 재인증
```

### 권한 오류

시트 공유 설정 확인:
- 편집자 권한으로 본인 이메일 추가
- 또는 "링크가 있는 모든 사용자" 편집 가능으로 설정

### 패키지 미설치

```bash
pip install gspread google-auth-oauthlib google-auth
```

---

## 의존성

- **gspread**: 구글 시트 Python API
- **google-auth-oauthlib**: OAuth 인증
- **인증 파일**: `~/.config/gspread/credentials.json`

---

## 파일 구조

```
gsheet-handler/
├── SKILL.md              # 이 파일
└── scripts/
    └── gsheet_api.py     # 핵심 스크립트
```

---

## 버전

- **v1.0.0 (2026-01-22)**: 초기 스킬 생성
  - read/write/update/append/create-tab/list-tabs 지원
  - OAuth 인증 연동
  - JSON 입출력 지원
