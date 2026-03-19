---
name: geo-optimizer
description: Next.js 기반 서비스의 ChatGPT GEO(Generative Engine Optimization) 최적화 자동화. "GEO 최적화", "ChatGPT에 인용되게", "AI 검색 최적화", "Bing 등록", "sitemap 만들어" 등을 언급하면 자동 실행. 메타데이터·sitemap·robots·JSON-LD·About 페이지 강화까지 전체 SOP 수행.
allowed-tools: Bash, Read, Write, Edit, WebFetch
---

# ChatGPT GEO 최적화 스킬 (Next.js App Router)

Next.js 기반 SaaS/랜딩 페이지가 ChatGPT 웹 검색(Bing 기반)에 인용되도록 최적화하는 End-to-End 스킬.

## 전체 워크플로우

```
[1] 현황 진단 (메타데이터, sitemap, robots, 콘텐츠 품질)
       ↓
[2] layout.tsx 메타데이터 강화
       ↓
[3] sitemap.ts 생성
       ↓
[4] robots.ts 생성 (Bingbot 명시적 허용)
       ↓
[5] JSON-LD 구조화 데이터 추가 (SoftwareApplication / FAQPage)
       ↓
[6] About 페이지 콘텐츠 강화 (스토리·기능·FAQ)
       ↓
[7] 빌드 확인 → 커밋 → 배포
       ↓
[8] Bing Webmaster Tools 등록 안내
```

---

## Step 1: 현황 진단

다음 파일을 확인한다:

```bash
# 메타데이터 확인
cat src/app/layout.tsx | grep -A 10 "metadata"

# sitemap/robots 존재 여부
ls src/app/sitemap.ts src/app/robots.ts 2>/dev/null

# 마케팅 페이지 목록
find src/app/\(marketing\) -name "page.tsx"

# 라이브 메타태그 확인
curl -s https://[도메인] | grep -o '<meta[^>]*>'
```

### 진단 체크리스트

| 항목 | 문제 | 조치 |
|------|------|------|
| metadata title | 짧고 키워드 없음 | Step 2에서 개선 |
| metadata description | 1줄 이하 | Step 2에서 개선 |
| sitemap.ts | 없음 | Step 3에서 생성 |
| robots.ts | 없음 | Step 4에서 생성 |
| JSON-LD | 없음 | Step 5에서 추가 |
| About 페이지 | 내용 빈약 | Step 6에서 보강 |
| `"use client"` on layout | 있으면 메타 미노출 위험 | layout은 서버 컴포넌트 유지 |

---

## Step 2: layout.tsx 메타데이터 강화

`src/app/layout.tsx`의 `metadata` 객체를 아래 구조로 확장:

```typescript
export const metadata: Metadata = {
  title: "[서비스명] - [핵심 키워드 포함 한 줄 설명]",
  description: "[주요 기능 3~4개 나열] + [타겟 사용자] + [무료/가격 정보]",
  keywords: ["키워드1", "키워드2", "키워드3", "서비스명"],
  authors: [{ name: "서비스명" }],
  creator: "서비스명",
  metadataBase: new URL("https://[도메인]"),
  alternates: { canonical: "/" },
  openGraph: {
    type: "website",
    locale: "ko_KR",
    url: "https://[도메인]",
    siteName: "서비스명",
    title: "...",
    description: "...",
  },
  twitter: {
    card: "summary_large_image",
    title: "...",
    description: "...",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true },
  },
};
```

### Bing 인증 메타 태그 추가 (layout의 `<head>` JSX에 직접 삽입)

> ⚠️ Next.js의 `metadata.other` 필드는 일부 버전에서 렌더링 안 됨 → JSX에 직접 작성

```tsx
<head>
  <meta name="msvalidate.01" content="[Bing 인증 코드]" />
  <script type="application/ld+json" ... />
</head>
```

---

## Step 3: sitemap.ts 생성

`src/app/sitemap.ts` 생성:

```typescript
import { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = "https://[도메인]";
  return [
    { url: baseUrl, lastModified: new Date(), changeFrequency: "weekly", priority: 1 },
    { url: `${baseUrl}/about`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.8 },
    { url: `${baseUrl}/pricing`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.8 },
  ];
}
```

빌드 후 `https://[도메인]/sitemap.xml` 에서 확인 가능.

---

## Step 4: robots.ts 생성

`src/app/robots.ts` 생성:

```typescript
import { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "*",
        allow: ["/", "/about", "/pricing"],
        disallow: ["/dashboard/", "/api/", "/sign-in", "/sign-up"],
      },
      {
        userAgent: "Bingbot",   // ChatGPT가 사용하는 크롤러 명시
        allow: ["/", "/about", "/pricing"],
        disallow: ["/dashboard/", "/api/", "/sign-in", "/sign-up"],
      },
    ],
    sitemap: "https://[도메인]/sitemap.xml",
  };
}
```

---

## Step 5: JSON-LD 구조화 데이터

`layout.tsx`의 `<head>` 안에 추가. SaaS 서비스라면 `SoftwareApplication` 스키마 사용:

```typescript
const jsonLd = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  name: "서비스명",
  applicationCategory: "BusinessApplication",
  operatingSystem: "Web",
  url: "https://[도메인]",
  description: "서비스 설명 (150자 내외)",
  offers: {
    "@type": "Offer",
    price: "0",
    priceCurrency: "KRW",
    description: "무료 플랜 제공. Pro 플랜 월 XX,000원.",
  },
  featureList: ["기능1", "기능2", "기능3"],
  inLanguage: "ko",
};
```

About 페이지에는 `FAQPage` 스키마 추가:

```typescript
const jsonLd = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: [
    {
      "@type": "Question",
      name: "질문 1",
      acceptedAnswer: { "@type": "Answer", text: "답변 1" },
    },
    // ... FAQ 3~5개
  ],
};
```

---

## Step 6: About 페이지 콘텐츠 강화

`"use client"` 제거 → 서버 컴포넌트로 전환 후 아래 섹션 추가:

1. **Hero**: 한 줄 미션 + 서비스 핵심 설명 (첫 50단어에 USP 배치)
2. **왜 만들었나**: 문제 인식 → 해결 방식 서술형 스토리
3. **핵심 기능**: 각 기능을 제목 + 1~2줄 설명으로 카드 형태
4. **FAQ 섹션**: 자주 묻는 질문 4개 이상 (JSON-LD FAQPage와 동일 내용)
5. **CTA**: 가격 정보 포함 + 버튼

### 콘텐츠 작성 원칙
- 과장 표현("최고", "최강") 금지 → 구체적 수치나 사실로 대체
- FAQ는 "이 서비스가 무엇인가?", "무료인가?", "다른 툴과 차이는?" 포함 필수
- 작성일(날짜) 명시

---

## Step 7: 빌드 확인 → 배포

```bash
# 빌드 오류 확인
pnpm build 2>&1 | tail -20

# sitemap, robots 정적 생성 확인 (○ 표시)
# ○ /sitemap.xml
# ○ /robots.txt

# 커밋
git add [변경된 파일들]
git commit -m "feat: ChatGPT GEO 최적화 — metadata, sitemap, robots, JSON-LD, about 강화"
git push

# 라이브 확인
curl -s https://[도메인] | grep -o '<meta[^>]*>'
curl -s https://[도메인]/sitemap.xml
```

---

## Step 8: Bing Webmaster Tools 등록

ChatGPT 웹 검색은 Microsoft Bing 인덱스 기반. Bing 등록이 필수.

1. [https://www.bing.com/webmasters](https://www.bing.com/webmasters) 접속
2. 사이트 URL 추가
3. **소유권 인증** 선택: "메타 태그" 방식 권장
   - 발급된 `<meta name="msvalidate.01" content="...">` 태그를 layout.tsx `<head>`에 직접 삽입
   - ⚠️ `metadata.other` 필드 사용 금지 — 일부 Next.js 버전에서 렌더링 안 됨
4. 배포 후 "확인" 버튼 클릭
5. **사이트맵** 제출: `https://[도메인]/sitemap.xml`
6. **URL 제출**: 메인·About·Pricing 페이지 URL 제출

---

## 완료 후 테스트

Bing 크롤링 완료까지 **1~2주** 소요. 이후 ChatGPT에서 테스트:

```
"[서비스 카테고리]에서 좋은 툴 추천해줘"
"한국 [타겟 직군]이 쓰는 AI 툴 뭐 있어?"
"[서비스명]이 뭐야?"
```

---

## 주요 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| msvalidate 태그 미노출 | `metadata.other` 렌더링 안 됨 | layout JSX `<head>`에 직접 `<meta>` 태그 삽입 |
| sitemap 미생성 | `sitemap.ts` 위치 오류 | `src/app/sitemap.ts` 위치 확인 |
| 메타 description 없음 | 랜딩이 `"use client"` | layout.tsx는 서버 컴포넌트 유지 |
| Bing 인증 실패 | 배포 전 인증 시도 | Vercel 배포 완료 후 인증 버튼 클릭 |
