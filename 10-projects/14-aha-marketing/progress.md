# Aha Marketing - 개발 진행 로그

## Phase 0: 프로젝트 스캐폴딩 (2026-02-06)

### 완료 사항
- Next.js 15 프로젝트 생성 (pnpm, App Router, TypeScript)
- 핵심 의존성 설치: shadcn/ui, Clerk, Prisma, Zustand, Framer Motion, Recharts, React Flow
- 디자인 시스템 설정: 듀얼 테마 (Intro 다크 #0A0A0A / Main 라이트 #F0EFEA), 인디고 액센트
- Pretendard 한글 폰트 + Inter + JetBrains Mono 설정
- 대시보드 레이아웃 (Sidebar + Topbar + Mobile Nav) 구현
- 전체 라우트 placeholder 페이지 생성 (20+ 페이지)
- API 라우트 스텁: ai/generate (SSE 스트리밍), keywords/search, workflows, webhooks/clerk
- Lib 유틸리티: AI 프로바이더 추상화, Prisma 클라이언트, Python 브릿지
- Prisma 스키마: User, Content, Workflow, KeywordSet, Report, UserApiKey
- Zustand 앱 스토어 + TypeScript 타입 정의
- imi-workspace 추적 문서 생성

### 기술 참고
- shadcn/ui 컴포넌트 16개 설치 (button, card, input 등)
- Tailwind CSS v4 + `@theme inline` 방식으로 CSS 변수 설정
- 랜딩 페이지 다크 테마에 `className="dark"` 적용 방식 사용

## Phase 1: 대시보드 + 분석 코어 (2026-02-06)

### 완료 사항

**대시보드 실체화**
- KPI 카드: 총 콘텐츠/키워드셋/워크플로우/최근 실행 수 (실제 DB 조회)
- Recharts AreaChart (30일 콘텐츠 생성 추이) + PieChart (타입 분포)
- 최근 콘텐츠 테이블 (shadcn Table + Badge)
- Clerk webhook 서명 검증 (svix) + DB 사용자 동기화
- 빈 데이터 시 empty state 처리

**분석 페이지**
- GA4 서비스 계정 인증 + 메트릭/트래픽 조회 (`lib/ga4.ts`)
- 리포트/키워드셋 데이터 레이어 + API 라우트 (CRUD)
- 분석 메인: 내부 KPI + GA4 섹션 + 콘텐츠 추이/분포 차트
- 키워드: 검색 패널 + 키워드셋 저장/관리
- 트렌드: 콘텐츠 타입별 30일 다중 라인 차트
- 캠페인/DataLab: Coming Soon 배너

**콘텐츠/워크플로우 CRUD**
- 콘텐츠 목록 + 생성 + 삭제
- 워크플로우 목록 + 생성 + 삭제

## Phase 2: AI 콘텐츠 생성 (2026-02-07)

### 완료 사항
- 콘텐츠 페이지에 AI 생성기 연동
- SSE 스트리밍 지원으로 실시간 생성 결과 표시
- 블로그/SNS/광고카피 타입별 콘텐츠 생성

## Phase 3: 워크플로우 빌더 MVP (2026-02-07)

### 완료 사항

**커스텀 노드 5종** (`components/workflows/nodes/index.tsx`)
- BaseNode 래퍼 + 타입별 색상/아이콘
- Trigger(green/Zap), AI(purple/Sparkles), Data(blue/Database), Action(orange/Play), Condition(yellow/GitBranch)

**3단 레이아웃 캔버스** (`components/workflows/workflow-canvas.tsx`)
- 왼쪽: 노드 팔레트 (드래그 가능)
- 중앙: React Flow 캔버스 (MiniMap, Controls, Background)
- 오른쪽: 노드 설정 패널 (타입별 폼)

**주요 기능**
- 팔레트 → 캔버스 드래그 & 드롭으로 노드 추가
- 노드 간 엣지 연결 (드래그)
- 노드 클릭 → 설정 패널에서 속성 편집
- 명시적 저장 버튼 (PATCH API → DB 반영)
- 실행 버튼 (POST → 순차 노드 실행)

**실행 엔진** (`app/api/workflows/[id]/execute/route.ts`)
- Trigger 노드부터 edges 따라 순차 실행
- AI 노드: `generateContent()` 호출 → 결과 다음 노드 전달
- Action 노드 (save-content): `createContent()` 호출
- WorkflowExecution 레코드 생성 (COMPLETED/FAILED + 실행 로그)

**API** (`app/api/workflows/[id]/route.ts`)
- GET: 워크플로우 상세 조회
- PATCH: nodes/edges/name 저장
- DELETE: 기존 유지

### 기술 참고
- `@xyflow/react` v12: useNodesState, useEdgesState, screenToFlowPosition
- Prisma Json 필드 ↔ TypeScript 타입 간 이중 캐스팅 (`as unknown as Node[]`)
- ReactFlowProvider 래퍼 필수 (useReactFlow 훅 사용을 위해)

## Phase 3.5: 인증 추상화 (2026-02-08)

### 완료 사항

**인증 추상화 레이어** (`src/lib/auth.ts`)
- `getAuthUser()` — Page용: null 반환 시 redirect 처리
- `requireApiAuth()` — API용: AuthUser 또는 401/404 Response
- `requireApiAuthId()` — API용 (DB 조회 없음): userId 또는 401 Response
- `@clerk/nextjs/server` import를 `auth.ts` + `middleware.ts` 2곳으로 집중
- 추후 NextAuth 전환 시 auth.ts + middleware + layout + webhook 4파일만 수정하면 됨

**Sign-in/Sign-up 실제 Clerk 컴포넌트 교체**
- `<SignIn />` / `<SignUp />` Clerk 컴포넌트로 교체 (소셜 로그인 자동 지원)
- 다크 테마 appearance 커스터마이징

**26파일 마이그레이션**
- API Route 10개 — Pattern A (`requireApiAuth`)
- API Route 3개 — Pattern C (`requireApiAuthId`)
- Page 11개 — Pattern B (`getAuthUser`)
- 결과: 103줄 추가, 366줄 삭제 (net -263줄)

## Phase 3.6: GA4 연동 강화 (2026-02-09)

### 완료 사항

**GA4 추가 메트릭** (`src/lib/ga4.ts`)
- `getGA4TrafficSources()` — 채널별 세션/사용자 수 (상위 8개)
- `getGA4TopPages()` — 인기 페이지 Top 10 (페이지뷰, 체류시간, 이탈률)
- `getGA4DeviceBreakdown()` — 디바이스 카테고리별 세션 분포

**분석 컴포넌트 3종 추가**
- `GA4TrafficSources` — 수평 바 차트 (채널별 세션/사용자)
- `GA4TopPages` — 인기 페이지 테이블 (경로, 페이지뷰, 체류, 이탈률)
- `GA4DeviceChart` — 도넛 차트 (데스크톱/모바일/태블릿 비율)

**설정 > 연동 페이지 개선** (`settings/integrations/page.tsx`)
- GA4 자격 증명 설정 다이얼로그 (Property ID, 서비스 계정 이메일, Private Key)
- DB 저장/조회/삭제 API (`/api/settings/integrations/ga4`)
- 연결 상태 실시간 표시 + 연동 해제 기능

**분석 대시보드 확장** (`analytics/page.tsx`)
- 트래픽 소스 + 디바이스 분포 2컬럼 레이아웃
- 인기 페이지 테이블 추가
- GA4 미연결 시 설정 페이지 링크 버튼

## Phase 5: 통합 + 세팅 (2026-02-15)

### v3.26 — 설정 프로필 연동

- `api/settings/profile/route.ts` — GET/PATCH 프로필 API (requireApiAuth)
- 설정 페이지 client 컴포넌트 전환, DB에서 이름/이메일 로드
- 이메일 read-only (Clerk 관리), 이름 수정 + 저장 피드백

### v3.27 — API 키 상태 페이지

- `api/settings/api-keys/route.ts` — 4개 서비스 그룹 연결 상태 API
- api-keys 페이지: 하드코딩 5개 키 제거 → DB 기반 상태 대시보드 + "설정" 링크
- integrations 페이지: Google Sheets/Notion → "준비 중" 배지 + 버튼 비활성화

### v3.28 — 알림 설정

- Prisma schema: User.notificationPrefs (Json, default 3개 true)
- shadcn Switch 컴포넌트 설치
- `api/settings/notifications/route.ts` — GET/PATCH 알림 선호도
- 설정 페이지: 3개 토글 (콘텐츠 생성/워크플로우 완료/주간 리포트), 즉시 PATCH
- "알림 발송 기능은 추후 업데이트에서 지원됩니다" 안내

### v3.29 — 리포트 자동 생성 + 상세 보기

- `lib/reports.ts`: generateContentSummaryReport, generateKeywordAnalysisReport, getReport 추가
- `api/reports/generate/route.ts` — POST 자동 생성 (content_summary, keyword_analysis)
- CreateReportDialog: 자동 타입 선택 시 제목 자동 채움, "자동 생성" 버튼
- ReportTable: 제목 클릭 → 상세 페이지 Link
- `analytics/reports/[id]/page.tsx` — 서버 컴포넌트, 타입별 상세 뷰
  - content_summary: 통계 카드 + 상태 분포 + 30일 트렌드 바 + 최근 콘텐츠 테이블
  - keyword_analysis: 세트 수/키워드 수 카드 + 세트별 목록 테이블
  - custom: JSON 원문 표시

### v3.30 — 워크플로우 조건 노드

- NodeConfigPanel.ConditionConfig: 조건 타입 Select (텍스트 포함/정확히 일치/비어있지 않음/글자수 초과) + 조건 값 Input
- 실행 엔진: evaluateCondition() 함수로 4가지 조건 실제 평가
- 실행 엔진: DFS walk → BFS 동적 walk로 리팩터링, sourceHandle 기반 T/F 분기
- ConditionNode: T/F 라벨 표시 (좌30% green, 우70% red)

### 기술 참고
- 신규 파일 5개, 수정 파일 10개, 설치 1개 (shadcn switch)
- Prisma migration: `add_notification_prefs`
- `pnpm build` 성공 확인

## Phase 6: 트렌드 분석 확장 + UX 개선 (2026-02-16)

### 트렌드 분석 기간 확장 및 키워드 연결

**naver.ts** — `getNaverTrend()`, `getNaverTrendMulti()`에 `timeUnit` 파라미터 추가 (date/week/month)

**naver-trend API** — `startDate/endDate/timeUnit` 옵션 필드 추가, `autoSelectTimeUnit` 자동 선택 (90일→일별, 365일→주별, 초과→월별)

**트렌드 비교 UI** — 기간 선택 [7일, 30일, 90일, 1년, 직접입력] 확장, 직접입력 시 날짜 피커 2개, `initialKeywords` prop으로 URL에서 키워드 전달 + 자동 검색

**트렌드 페이지** — `searchParams`에서 `keywords` 쿼리 파라미터 파싱 → `NaverTrendCompare`에 전달

**키워드 검색 패널** — "트렌드 분석" 버튼 추가, 선택 키워드(최대 5개) → `/analytics/trends?keywords=...`로 이동

### 성수기/비수기 분석 팝업

**analyzeSeasons()** — 월별 평균 대비 120%↑ 성수기, 80%↓ 비수기 판정, 추세/변동성/최고점/최저점 분석

**AI 요약 다이얼로그** — 차트 영역에 "AI 요약" 버튼, 종합 분석 (전체 추세/공통 성수기·비수기/전략 제안) + 키워드별 상세 (평균/추세/변동성/성수기·비수기/최고·최저점)

### 테이블 UX 개선

**keyword-search-panel.tsx + keyword-set-table.tsx** — PC(검색량, CTR), 모바일(검색량, CTR) 그룹 헤더(colSpan/rowSpan) 적용, CSV 다운로드 컬럼 순서 동기화

### 드래그 가능 다이얼로그

**dialog.tsx** — `useDraggable` 훅 추가, `DialogHeader`를 드래그 핸들로 사용 (cursor: grab/grabbing), 열릴 때 위치 자동 리셋, 모든 다이얼로그에 자동 적용

## Phase 7: 시즈널 SEO/GEO 인사이트 (보류)

### 구현 완료 (코드 작성됨, 동작 검증 보류)

**trend-insight API** (`api/analytics/trend-insight/route.ts`) — SeasonAnalysis[] 받아 LLM으로 SEO/GEO 인사이트 생성, `generateContent()` 호출

**naver-trend-compare.tsx 수정** — `SeasonAnalysis` 타입 export, `onSeasonAnalysis` 콜백 prop 추가, seasonAnalysis 계산 후 부모에 전달

**SeoGeoInsight 컴포넌트** (`components/analytics/seo-geo-insight.tsx`) — 마크다운 인사이트 표시, 로딩/결과/빈상태 처리

**page.tsx → TrendsContent 클라이언트 래퍼 도입** — 서버 컴포넌트에서 데이터 fetch 후 TrendsContent에 전달, NaverTrendCompare ↔ SeoGeoInsight 간 상태 공유

### 보류 사유
- `.env`에 `ANTHROPIC_API_KEY`가 비어있어 LLM 호출 시 500 에러 발생
- API 키 설정 후 동작 검증 + `tsc --noEmit` 확인 필요
