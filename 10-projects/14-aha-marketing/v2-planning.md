# Aha Marketing v2 기획서

> 작성일: 2026-02-25
> 버전: 2.0

---

## 신규 기능 개요

| # | 기능명 | 목적 |
|---|--------|------|
| A | AI 파일 정리 | 로컬 파일 업로드 → AI 분석 → 자동 파일명·폴더 구조 제안 → 승인 후 ZIP 다운로드 |
| B | AI 마케팅 리포팅 | 네이버 광고 성과 데이터 → AI 인사이트 분석 → 리포트 생성 및 PDF/PPT 내보내기 |

---

## Feature A. AI 파일 정리

### 플로우
```
파일 업로드 (드래그앤드롭, 폴더 선택)
  → 파일 유형별 AI 분석 (Claude Vision/Text, 10개 배치 병렬)
    → 제안 미리보기 (트리 구조)
      → 사용자 승인 / 개별 수정
        → ZIP 다운로드 (새 폴더 구조 적용)
```

### 파일 유형별 분석 전략

| 유형 | 파싱 방법 | Claude 역할 |
|------|----------|------------|
| 이미지 (jpg/png/webp/gif) | Base64 → Vision API | 내용 설명 → 파일명 + 카테고리 추천 |
| PDF | `pdf-parse` 텍스트 추출 | 제목·날짜·유형 판단 |
| Word (docx) | `mammoth` 파싱 | 문서 목적 파악 |
| Excel (xlsx) | `xlsx` 파싱 | 데이터 성격 판단 |
| PPT (pptx) | 메타데이터 + 텍스트 | 주제·날짜 추정 |
| 동영상 (mp4/mov) | 메타데이터만 | 파일명 패턴 + 날짜 기반 |

### 자동 폴더 구조 (AI 판단 기준)
```
/마케팅소재/{YYYY-MM}/    ← 이미지·영상
/보고서/{YYYY-Q?}/        ← PDF·Word 보고서
/데이터/                  ← Excel·CSV
/기획서/                  ← PPT·기획 문서
/기타/
```

### 파일명 규칙
- **AI 자동**: Claude가 내용 분석 후 `YYYY-MM-DD_설명_카테고리.확장자` 형태로 제안
- **사용자 템플릿**: `{YYYY-MM}_{프로젝트명}_{원본파일명}` 등 커스텀 형식 설정 가능
- 두 방식 모두 지원, 기본은 AI 자동

### 대규모 처리 전략 (500개+)
- 파일 10개씩 병렬 배치 처리
- SSE(Server-Sent Events)로 실시간 진행률 표시
- 실패 파일 개별 표시 + 재시도 버튼

### 신규 파일 구조
```
src/app/(dashboard)/tools/
  file-organizer/page.tsx
src/app/api/tools/file-organizer/
  analyze/route.ts
src/components/tools/file-organizer/
  upload-zone.tsx            ← 드래그앤드롭 UI
  analysis-progress.tsx      ← 진행률 표시
  file-tree-preview.tsx      ← 제안 미리보기 + 수정
  rule-template-editor.tsx   ← 규칙 템플릿 설정
```

### 신규 패키지
```
pdf-parse     PDF 텍스트 추출
mammoth       DOCX 파싱
jszip         ZIP 생성 및 다운로드
```

---

## Feature B. AI 마케팅 리포팅 (Naver MVP)

### 플로우
```
데이터 입력 (Naver API 연동 OR Excel/CSV 업로드)
  → 캠페인별 성과 파싱
    → Claude AI 인사이트 분석
      → 리포트 빌더 (KPI 카드 + 차트 + 텍스트)
        → PDF / PPT 내보내기
```

### 데이터 입력 이중 구조

**경로 1 — Naver 광고 API 자동 연동**
- 기존 `getNaverCampaignStats()` 활용
- 기간 선택 → 자동 fetch
- 캠페인 선택적 포함/제외

**경로 2 — Excel/CSV 업로드 (fallback)**
- 네이버 광고 대시보드 다운로드 파일 포맷 자동 감지
- 한글 컬럼 헤더 자동 매핑

### 리포트 구성 요소

| # | 구성 | 설명 |
|---|------|------|
| ① | KPI 요약 카드 | 노출·클릭·전환·비용·CTR·ROAS |
| ② | 캠페인별 성과 테이블 + 바차트 | 상위/하위 캠페인 비교 |
| ③ | 기간 비교 트렌드 | 전주/전월 대비 꺾은선 차트 |
| ④ | Claude AI 인사이트 | 상위·하위 캠페인 분석 + 예산 효율 개선 제안 |
| ⑤ | 내보내기 | PDF(내부용) / PPT(외부 클라이언트용) |

### 내·외부 리포트 분리

| | 내부용 | 외부용 (클라이언트) |
|--|--------|------------------|
| 브랜딩 | Aha 기본 테마 | 로고·색상 커스텀 |
| 데이터 범위 | 전체 지표 | 선택 항목만 노출 |
| 인사이트 | 상세 수치 포함 | 요약 중심 |

### 신규/변경 파일 구조
```
src/app/(dashboard)/analytics/reports/
  new/page.tsx                    ← 리포트 생성 페이지 (기존 reports 확장)
src/app/api/analytics/
  report-generate/route.ts
src/components/analytics/report-builder/
  data-source-selector.tsx        ← API vs CSV 선택
  csv-upload-parser.tsx           ← CSV/Excel 파싱
  kpi-cards.tsx                   ← KPI 요약 카드
  campaign-chart.tsx              ← 캠페인별 차트
  insight-panel.tsx               ← AI 인사이트
  export-options.tsx              ← PDF/PPT 내보내기
```

### 신규 패키지
```
jspdf + html2canvas    PDF 내보내기
pptxgenjs              PPT 내보내기
```

---

## 구현 단계

| Phase | 기능 | 주요 작업 |
|-------|------|----------|
| **Phase 1** | AI 파일 정리 MVP | 업로드 UI → Claude 분석 → 트리 미리보기 → ZIP 다운로드 |
| **Phase 2** | AI 파일 정리 고도화 | 대규모 배치 처리, 규칙 템플릿 커스텀 |
| **Phase 3** | 마케팅 리포팅 MVP | Naver API + CSV 파싱 + 차트 + AI 인사이트 + PDF 내보내기 |
| **Phase 4** | 리포팅 고도화 | 외부용 브랜딩, PPT 내보내기, 데이터 소스 추가 (Meta/GA4) |

---

## 기술적 제약 및 결정사항

- 로컬 파일 직접 접근 불가 (웹 보안) → 업로드 방식으로 해결, ZIP 다운로드로 반환
- 대규모 파일(500개+)은 서버 메모리 고려 → 스트리밍 방식 필수
- 네이버 광고 API 연동은 기존 `lib/naver.ts`의 `getNaverCampaignStats()` 재활용
- PDF 내보내기: `html2canvas + jspdf` 방식 (기존 리포트 UI 그대로 캡처 가능)

---

## 측정 지표 (성공 기준)

- AI 파일 정리: 파일명 제안 수용률 ≥ 70%
- 마케팅 리포팅: 리포트 생성 → 내보내기까지 3분 이내

---

## Phase 9: 리포트 강화 (추가 제안)

### 현재 진행 중
- [x] 리포트 자동 저장 (생성 후 DB 저장 + 상세 페이지 재현)

### 추가하면 좋은 기능

---

#### 9-A. 리포트 원클릭 갱신 (데이터 새로고침)

**문제**: 저장된 리포트는 생성 당시 스냅샷. 같은 캠페인을 다음 달에 다시 분석하려면 처음부터 재입력해야 함.

**해결**: 리포트 저장 시 `generateParams` (source, campaignId, startDate~endDate 또는 days)를 함께 저장.
상세 페이지에 "데이터 갱신" 버튼 → 저장된 params로 `/api/analytics/report-generate` 재호출 → 리포트 업데이트.

**저장 데이터 추가 필드**:
```json
{
  "type": "naver",
  "stats": [...],
  "kpis": {...},
  "insights": "...",
  "dateRange": "...",
  "generateParams": {
    "source": "api",
    "campaignId": "xxx",
    "startDate": "2025-01-01",
    "endDate": "2025-01-31"
  }
}
```

**영향 파일**: `new/page.tsx`, `[id]/page.tsx`, `analytics-report-view.tsx`
**의존**: 현재 진행 중인 자동 저장 기능 완료 후 구현 가능

---

#### 9-B. 리포트 이메일 발송

**문제**: 클라이언트에게 리포트를 전달하려면 PDF 다운로드 후 이메일 첨부 과정이 필요.

**해결**: 상세 페이지 또는 목록에서 "이메일로 공유" 버튼 → 수신자 이메일 입력 → HTML 리포트를 이메일로 발송.

**구현 방식**:
- 기존 Resend API 인프라 활용 (`RESEND_API_KEY` 이미 설정됨)
- 리포트 HTML을 이메일 템플릿으로 변환 (React Email 컴포넌트)
- 신규 API: `POST /api/analytics/report-share-email`

**영향 파일**: 신규 route + `analytics-report-view.tsx`에 공유 버튼 추가

---

#### 9-C. 기간 비교 리포트 (WoW / MoM)

**문제**: 현재 리포트는 단일 기간만 분석. 전월 대비 성과 개선/악화를 파악하기 어려움.

**해결**: Naver 리포트 생성 시 "비교 기간 추가" 옵션 → 두 기간 데이터를 나란히 비교.

**UI 추가**:
- KPI 카드에 델타 표시: `노출 +12.3% ↑` (초록/빨강)
- 차트에 두 기간 꺾은선 오버레이

**구현 방식**:
- `DataSourceSelector`에 "비교 기간" 토글 추가
- `report-generate` API에 `comparePeriod` 파라미터 추가
- AI 인사이트 프롬프트에 비교 데이터 포함

---

#### 9-D. 다중 캠페인 통합 리포트

**문제**: 현재 캠페인 1개 단위 리포트만 가능. 여러 캠페인을 운영하는 경우 전체 현황 파악 불가.

**해결**: 캠페인 선택 UI에서 다중 선택 → 합산 KPI + 캠페인별 성과 비교 테이블.

**데이터 구조**:
- 각 캠페인 stats 병렬 fetch → 합산 KPI + 캠페인별 breakdown
- AI 인사이트에 "최고 효율 캠페인", "예산 재분배 제안" 추가

---

#### 9-E. 리포트 공개 공유 링크

**문제**: 외부 클라이언트에게 리포트를 공유할 때 로그인 없이 볼 수 있는 방법이 없음.

**해결**: "공유 링크 생성" → 토큰 기반 공개 URL (`/share/[token]`) → 만료일 설정 가능.

**DB 변경**: `Report` 모델에 `shareToken String? @unique`, `shareExpiresAt DateTime?` 추가 (마이그레이션 필요)
**신규 페이지**: `src/app/share/[token]/page.tsx` (비인증 접근 가능)

---

### 우선순위

| 기능 | 난이도 | 마케터 가치 | 권장 순서 |
|------|--------|------------|----------|
| 9-A 원클릭 갱신 | 낮음 | ★★★★★ | 1순위 |
| 9-B 이메일 발송 | 낮음 | ★★★★☆ | 2순위 (Resend 기존 활용) |
| 9-C 기간 비교 | 중간 | ★★★★☆ | 3순위 |
| 9-D 다중 캠페인 | 중간 | ★★★☆☆ | 4순위 |
| 9-E 공개 링크 | 중간 | ★★★☆☆ | 5순위 |
