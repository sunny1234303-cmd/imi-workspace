# 14 - Aha Marketing

## 개요

마케터를 위한 올인원 워크플로우 AI 자동화 SaaS 플랫폼

## 링크

- **프로젝트 디렉토리**: `~/aha_marketing/`
- **배포 URL (v1)**: https://aha-marketing-c5pdbrjho-jinseonis-projects.vercel.app
- **배포 URL (v2)**: https://aha-marketing-v2.vercel.app
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

### v2 추가 기능 (2026-02-25)

- [x] v2 Phase 1+2: AI 파일 정리
  - 파일 업로드(최대 500개) → Claude Vision/Text 분석 → 폴더 트리 제안 → ZIP 다운로드
  - 10개씩 배치 처리 + 진행률 + 실패 재시도 + 파일명 규칙 템플릿
- [x] v2 Phase 3: AI 마케팅 리포팅 MVP
  - Naver API 연동 + CSV 업로드(한글 컬럼 자동 매핑)
  - KPI 카드 + 일별 성과 차트(Recharts) + Claude AI 인사이트
  - PDF 내보내기 (html2canvas + jsPDF)
- [x] v2 Phase 4: 리포팅 고도화
  - GA4 웹 트래픽 데이터 소스 추가
  - 외부용 브랜딩 패널 (클라이언트명 + 브랜드 컬러)
  - PPT 내보내기 (pptxgenjs, 4슬라이드)
- [x] v2 Vercel 배포: https://aha-marketing-v2.vercel.app
- [x] v2 버그픽스 (2026-02-25)
  - 마케팅 리포트 `Unexpected end of JSON input` 오류 수정
  - `report-generate` route: `req.json()` 파싱 실패 및 `generateNaverInsights` 미처리 예외 try-catch 처리
  - `new/page.tsx`: 비JSON 서버 응답 시 사용자 친화적 에러 메시지 표시
- [x] v2 Phase 5: 트렌드 분석 결과 리포트 저장 (2026-02-26)
  - 키워드 트렌드 / 경쟁사 USP 분석 / 블로그 현황 3종 분석 완료 후 "저장" 버튼으로 DB 저장
  - 저장 후 리포트 목록 이동 링크 + 상세 페이지에서 결과 재현
  - `keyword_trend`: AreaChart 재현 + 계절성 카드 + SEO 인사이트 패널
  - `competitor_usp`: 브랜드별 USP 괴리 카드 정적 렌더링
  - `blog_trend`: 키워드별 블로그 포스트 테이블
  - 리포트 목록 탭 3종 추가 (키워드 트렌드 / 경쟁사 USP / 블로그 현황)

## 관련 파일

- [progress.md](./progress.md) - 개발 진행 로그
- [decisions.md](./decisions.md) - 기술/디자인 결정 기록
