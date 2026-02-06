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
