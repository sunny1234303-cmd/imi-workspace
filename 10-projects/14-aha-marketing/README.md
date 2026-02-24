# 14 - Aha Marketing

## 개요

마케터를 위한 올인원 워크플로우 AI 자동화 SaaS 플랫폼

## 링크

- **프로젝트 디렉토리**: `~/aha_marketing/`
- **배포 URL**: https://aha-marketing-c5pdbrjho-jinseonis-projects.vercel.app
- **GitHub**: https://github.com/sunny1234303-cmd/aha-marketing
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
- [x] Phase 6: QA + 런치
- [ ] Phase 7: 시즈널 SEO/GEO 인사이트 (코드 완성, 검증 보류)
- [x] Phase 8: 마케팅 자동화 강화
  - Google Sheets 1클릭 내보내기 (키워드셋, 리포트)
  - 주간 리포트 자동 이메일 발송 (월요일 UTC 0시)
  - 키워드 랭크 변동 알림 이메일 (±3위 or 10위 진입/이탈)
  - 워크플로우 스케줄러 (매시간 체크, cron expression 기반)
  - 신규 env: `RESEND_API_KEY`, `EMAIL_FROM`(선택)

## 관련 파일

- [progress.md](./progress.md) - 개발 진행 로그
- [decisions.md](./decisions.md) - 기술/디자인 결정 기록
