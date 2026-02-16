# Aha Marketing - 기술/디자인 결정 기록

## D001: 프레임워크 선택 (2026-02-06)

**결정**: Next.js 15 (App Router) + TypeScript
**이유**: Vercel 네이티브 배포, SSR/SSG, API Routes 통합, Claude 코드 생성 최적화
**대안**: Remix, SvelteKit → 생태계 성숙도 & Vercel 통합 우선

## D002: 디자인 시스템 듀얼 테마 (2026-02-06)

**결정**: Intro(다크 #0A0A0A) + Main(라이트 #F0EFEA) 분리
**이유**: 랜딩 페이지는 3D/PBR 효과를 위해 다크 필수, 대시보드는 작업 편의성 위해 라이트
**구현**: CSS 변수 + shadcn의 `.dark` 클래스 활용

## D003: Python 브릿지 전략 (2026-02-06)

**결정**: FastAPI 마이크로서비스로 기존 Python API 로직만 래핑
**이유**: Streamlit UI 코드는 버리고 API 호출 함수만 재사용 → 프론트엔드 완전 재설계
**배포**: Railway (Python) + Vercel (Next.js)

## D004: 인증 (2026-02-06)

**결정**: Clerk
**이유**: 사전 빌드 UI, 10K MAU 무료, 최소 코드 → 빠른 MVP
**대안**: NextAuth → 커스터마이징 자유도는 높지만 구현 복잡

## D005: 상태관리 (2026-02-06)

**결정**: Zustand
**이유**: 경량, 보일러플레이트 최소, React 19 호환
**대안**: Jotai, Redux Toolkit → 규모 대비 오버엔지니어링

## D006: GA4 연동 방식 (2026-02-06)

**결정**: 서비스 계정 인증 (google-auth-library)
**이유**: 서버 사이드 전용, OAuth 동의 흐름 불필요, API Route에서 직접 호출
**구현**: `lib/ga4.ts` — 서비스 계정 JSON → BetaAnalyticsDataClient

## D007: 워크플로우 빌더 라이브러리 (2026-02-07)

**결정**: `@xyflow/react` v12 (React Flow)
**이유**: 노드 기반 에디터 업계 표준, MIT 라이선스, 풍부한 API (커스텀 노드, Handle, MiniMap)
**대안**: 직접 구현 → 개발 비용 대비 효용 낮음

## D008: 워크플로우 저장 전략 (2026-02-07)

**결정**: Prisma Json 필드에 nodes/edges 배열 직접 저장, 명시적 저장 버튼
**이유**: 자동 저장은 실수 저장 위험, Json 필드는 스키마 변경 없이 유연한 노드 구조 대응
**트레이드오프**: 노드별 쿼리 불가 → MVP에서는 문제없음

## D009: 워크플로우 실행 방식 (2026-02-07)

**결정**: 동기 순차 실행 (trigger → edges 순서대로 walk)
**이유**: MVP 단순성 우선, 비동기 병렬 실행은 Phase 5+에서 고려
**제약**: 긴 워크플로우는 API 타임아웃 가능 → 추후 큐 기반으로 전환 검토

## D010: 워크플로우 조건 분기 방식 (2026-02-15)

**결정**: BFS 동적 walk + sourceHandle 기반 분기
**이유**: 기존 DFS walk는 condition 노드의 true/false 분기를 구분할 수 없었음. BFS로 전환하여 condition 노드에서 evaluateCondition() 결과에 따라 해당 sourceHandle("true"/"false")의 edge만 추적
**조건 타입**: contains, equals, not_empty, length_gt

## D011: 알림 설정 저장 (2026-02-15)

**결정**: User 모델에 `notificationPrefs` Json 필드
**이유**: 별도 테이블보다 단순, 3개 boolean 토글이라 Json으로 충분
**제약**: 실제 알림 발송은 미구현 (UI 선호도만 저장)

## D012: 드래그 가능 다이얼로그 (2026-02-16)

**결정**: `dialog.tsx`에 `useDraggable` 훅 내장, `DialogHeader`를 드래그 핸들로 사용
**이유**: 분석 팝업(성수기/비수기, 키워드 결과 등)이 차트와 함께 사용되므로 팝업을 이동시켜 데이터 비교 필요
**구현**: Pointer Events 기반, `data-slot="dialog-header"` 감지, 열릴 때 위치 리셋, 버튼/인풋 클릭은 드래그 제외
**범위**: 모든 Dialog 컴포넌트에 자동 적용 (코드 변경 없이)

## D013: 트렌드 분석 timeUnit 자동 선택 (2026-02-16)

**결정**: 기간에 따라 API에서 timeUnit 자동 결정 (90일→일별, 365일→주별, 초과→월별)
**이유**: 1년 이상 일별 데이터는 데이터 포인트가 너무 많아 차트 가독성 저하, 네이버 API도 장기간 일별 조회 시 오류 가능
**구현**: `autoSelectTimeUnit()` 서버 헬퍼, 프론트에서 명시 지정도 가능
