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
