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
