# 14 - Aha Marketing

## 개요

마케터를 위한 올인원 워크플로우 AI 자동화 SaaS 플랫폼

## 링크

- **프로젝트 디렉토리**: `~/aha_marketing/`
- **배포 URL**: (Vercel 배포 후 추가)
- **기술 스택**: Next.js 16, TypeScript, shadcn/ui, Tailwind v4, Prisma, Supabase, Clerk

## 핵심 기능

1. **AI 콘텐츠 생성** - 블로그, SNS, 광고 카피 자동 생성
2. **데이터 분석** - 키워드, 트렌드, 캠페인, GA4 분석
3. **워크플로우 자동화** - 노드 기반 워크플로우 빌더
4. **3D/물리 UI** - R3F + Rapier 기반 인터랙티브 경험

## UX 공통 사항

- **드래그 가능 다이얼로그** - 모든 팝업/다이얼로그 헤더를 잡아 드래그하여 위치 이동 가능 (`dialog.tsx` useDraggable 훅)

## 현재 상태

- [x] Phase 0: 프로젝트 스캐폴딩 + imi-workspace 연결
- [x] Phase 1: 대시보드 + 분석 코어
- [x] Phase 2: AI 콘텐츠 생성
- [x] Phase 3: 워크플로우 빌더 MVP
- [x] Phase 4: 3D/물리 폴리싱
- [x] Phase 5: 통합 + 세팅
- [ ] Phase 6: QA + 런치

## 관련 파일

- [progress.md](./progress.md) - 개발 진행 로그
- [decisions.md](./decisions.md) - 기술/디자인 결정 기록
