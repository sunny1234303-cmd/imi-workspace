# Design Guide — 진서니 워크스페이스 공통 디자인 시스템

> **이 파일은 모든 UI/웹 작업의 공식 디자인 기준입니다.**
> AI에게 작업을 요청할 때 이 파일을 컨텍스트로 제공하거나 `design-guide.md 참고해서` 라고 명시하세요.

## Design Intent

**무드**: Quiet Luxury × 하이테크 미니멀리즘
**방향성**: 장식을 덜어내고 여백과 타이포그래피로 말하는 디자인. 날카로운 모서리, 절제된 색상, 밀도 있는 자간으로 세련된 긴장감을 만든다. 화려함 없이 품격 있는 느낌. 버튼, 카드, 컴포넌트 모두 이 원칙을 따른다.

**핵심 원칙**:
- 색상보다 여백으로 위계를 만든다
- 둥근 모서리는 최소화 (기본 0px, 불가피할 때만 4px)
- 폰트 굵기는 Medium(500)이 최대 — H1/H2는 두껍지 않게
- 구분선은 얇은 선이 아닌 `#222222` 실선으로 확실하게

---

## CSS Custom Properties

아래 블록을 프로젝트 CSS 최상단에 붙여넣으면 바로 사용 가능합니다.

```css
/* ============================================================
   DESIGN TOKENS — Quiet Luxury × High-tech Minimalism
   진서니 워크스페이스 공통 디자인 시스템
   ============================================================ */

@font-face {
  font-family: 'Pretendard';
  src: url('/fonts/Pretendard-Thin.woff2') format('woff2');
  font-weight: 100;
  font-style: normal;
}
@font-face {
  font-family: 'Pretendard';
  src: url('/fonts/Pretendard-Light.woff2') format('woff2');
  font-weight: 300;
  font-style: normal;
}
@font-face {
  font-family: 'Pretendard';
  src: url('/fonts/Pretendard-Regular.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
}
@font-face {
  font-family: 'Pretendard';
  src: url('/fonts/Pretendard-Medium.woff2') format('woff2');
  font-weight: 500;
  font-style: normal;
}
@font-face {
  font-family: 'Pretendard';
  src: url('/fonts/Pretendard-SemiBold.woff2') format('woff2');
  font-weight: 600;
  font-style: normal;
}
@font-face {
  font-family: 'Pretendard';
  src: url('/fonts/Pretendard-ExtraBold.woff2') format('woff2');
  font-weight: 800;
  font-style: normal;
}
@font-face {
  font-family: 'Pretendard';
  src: url('/fonts/Pretendard-Black.woff2') format('woff2');
  font-weight: 900;
  font-style: normal;
}

:root {
  /* ── Font ─────────────────────────────────────────── */
  --font:           'Pretendard', -apple-system, sans-serif;
  --letter-spacing: -0.02em;
  --line-height:    1.6;

  /* ── Colors ───────────────────────────────────────── */
  --color-bg:           #FAF9F6;   /* 기본 배경 */
  --color-text:         #1A1A1A;   /* 기본 텍스트 */
  --color-text-muted:   #7F7F7F;   /* 흐린 텍스트 (기간, 라벨 등) */
  --color-border:       #222222;   /* 구분선 */
  --border-width:       2.25px;

  /* ── Typography Scale ─────────────────────────────── */
  --text-hero:   88px;   /* 특수 대형 타이틀 */
  --text-h1:     40px;   /* 페이지 타이틀 */
  --text-h2:     36px;   /* 섹션 타이틀 */
  --text-h3:     18px;   /* 소제목 */
  --text-label:  16px;   /* 캡션, 라벨 */
  --text-body:   14px;   /* 본문 */
  --text-sm:     13px;   /* 보조 본문, 메타 정보 */

  /* ── Font Weights ─────────────────────────────────── */
  --weight-thin:      100;   /* 대형 연락처·수치 — 가볍고 우아한 대비 */
  --weight-light:     300;   /* 보조 대형 텍스트 */
  --weight-regular:   400;
  --weight-medium:    500;
  --weight-semibold:  600;
  --weight-extrabold: 800;   /* 히어로 디스플레이 — 강렬한 무게감 */
  --weight-black:     900;   /* 최대 강조 */

  /* ── Spacing (8px base) ───────────────────────────── */
  --space-1:  4px;    /* 아주 좁은 간격 (글자·라벨 사이) */
  --space-2:  8px;    /* 좁은 간격 */
  --space-4:  16px;   /* 기본 단락 간격 */
  --space-6:  24px;   /* 콘텐츠 그룹 간격 */
  --space-8:  32px;   /* 블록·카드 간격 */
  --space-12: 48px;   /* 대형 콘텐츠 덩어리 간격 */

  /* ── Section Spacing ──────────────────────────────── */
  --space-section:    96px;   /* PC 섹션 간 여백 (기본) */
  --space-section-lg: 120px;  /* PC 섹션 간 여백 (넓게) */
  --space-section-mo: 56px;   /* 모바일 섹션 간 여백 (기본) */
  --space-section-mo-lg: 64px; /* 모바일 섹션 간 여백 (넓게) */

  /* ── Layout ───────────────────────────────────────── */
  --max-width: 1440px;
  --radius:    0px;    /* 기본: 날카로운 모서리 */
  --radius-sm: 4px;    /* 불가피할 때만 사용 */
}
```

---

## Typography

폰트 계층별 사용 기준.

| 계층 | 변수 | 크기 | 굵기 | 사용 예시 |
|---|---|---|---|---|
| Hero | `--text-hero` | 88px | Medium 500 | 랜딩 페이지 핵심 카피 |
| H1 (Page Title) | `--text-h1` | 40px | Medium 500 | Career Timeline, Experience |
| H2 (Section) | `--text-h2` | 36px | Medium 500 | 섹션 구분 제목 |
| H3 (Subheading) | `--text-h3` | 18px | SemiBold 600 | 회사명, 프로젝트명 |
| Label | `--text-label` | 16px | SemiBold 600 | 태그, 카테고리 라벨 |
| Body | `--text-body` | 14px | Regular 400 | 일반 본문, 설명 |
| Small | `--text-sm` | 13px | Regular 400 | 기간, 메타 정보, 보조 설명 |

**굵기 대비 활용 원칙**:
- **Black(900) × Thin(100)** 조합이 핵심 — 같은 화면에서 극단적 대비로 긴장감을 만든다
- H1/H2는 Medium(500) — 두껍지 않게 세련되게
- ExtraBold/Black은 히어로 디스플레이 텍스트에만 사용 (남발하면 힘 잃음)
- Thin/Light는 대형 크기(48px↑)에서만 사용 — 작은 크기에서는 가독성 저하
- `letter-spacing: -0.02em` 전 계층 공통 적용
- `line-height: 1.6` 본문 이상 적용

---

## Spacing System

8px 배수 기반. 토큰 숫자는 `space-N = N × 4px` 공식.

```
--space-1  ░░░░   4px  — 라벨, 아이콘 옆 텍스트
--space-2  ░░░░░░░░   8px  — 좁은 내부 여백
--space-4  ░░░░░░░░░░░░░░░░   16px — 단락 사이, 제목↔본문
--space-6  ░░░░░░░░░░░░░░░░░░░░░░░░   24px — 콘텐츠 그룹
--space-8  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   32px — 카드, 블록 간격
--space-12 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   48px — 큰 콘텐츠 덩어리
```

섹션 간 여백은 토큰 대신 `--space-section` 계열 사용:

```css
/* PC */
padding-top: var(--space-section);     /* 96px */
padding-top: var(--space-section-lg);  /* 120px — 여유 있게 */

/* Mobile */
@media (max-width: 767px) {
  padding-top: var(--space-section-mo);     /* 56px */
  padding-top: var(--space-section-mo-lg);  /* 64px */
}
```

---

## Layout

```
max-width:       1440px  — 콘텐츠 최대 너비
border-radius:   0px     — 날카로운 모서리 (기본)
                 4px     — 최대 허용치 (불가피할 때만)

Breakpoint:
  Mobile  ≤ 767px
  PC      ≥ 768px
```

반응형 기본 패턴:

```css
.container {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 0 var(--space-8); /* PC: 32px 좌우 */
}

@media (max-width: 767px) {
  .container {
    padding: 0 var(--space-4); /* Mobile: 16px 좌우 */
  }
}
```

---

## 컬러 레퍼런스

```
배경     #FAF9F6  ████  크림-화이트 (순백보다 따뜻한 오프화이트)
텍스트   #1A1A1A  ████  소프트 블랙 (순흑보다 눈에 편안한 거의-검정)
흐린     #7F7F7F  ████  미드 그레이 (기간, 보조 텍스트)
구분선   #222222  ████  다크 (얇은 선이 아닌 확실한 구분)
```

액센트 컬러 없음 (추후 추가 시 이 파일 업데이트).

---

## 선(Line) 활용 원칙

이 디자인 시스템에서 선은 장식이 아닌 **구조** 역할을 한다. 색상 대신 선으로 위계와 영역을 나눈다.

### 선 종류

| 종류 | 값 | 용도 |
|---|---|---|
| 굵은 선 (Primary) | `#222222`, `2.25px` | 섹션 경계, 헤더·푸터 구분, 핵심 분리 |
| 얇은 선 (Subtle) | `#d8d4ce`, `1px` | 행(row) 간 구분, 콘텐츠 내부 반복 분리 |

### 수평선 사용 패턴

**섹션 경계** — 헤더/본문/푸터를 구분할 때 굵은 선 사용
```
[헤더 영역]
────────────────  ← border-bottom: 2.25px #222222
[본문 영역]
────────────────  ← border-bottom: 2.25px #222222
[로고·푸터 영역]
```

**행(row) 구분** — 라벨+내용 반복 테이블에서 얇은 선 사용
```
실행 목적  |  LTV 높은 잠재고객 확장 방안 기획
- - - - - - - - - - ← border-bottom: 1px #d8d4ce
접근 과정  |  ...
- - - - - - - - - -
결과      |  ...
```

### 수직선 사용 패턴

**컬럼 분리** — 좌(이미지·프로필)와 우(콘텐츠)를 나눌 때 굵은 수직선 사용
```
[좌 컬럼]  │  [우 컬럼]
이름·사진  │  스펙 테이블
           ↑
  border-right: 2.25px #222222
```

**2단 레이아웃 기본 구조**
```css
.two-col {
  display: grid;
  grid-template-columns: 2fr 3fr;  /* 좌:우 = 40:60 */
}

.two-col > *:first-child {
  border-right: var(--border-width) solid var(--color-border);
}
```

### 선 활용 실제 예시

**Career Timeline** — 수평선만으로 구성
- 헤더(타이틀) 아래 굵은 선 1개
- 각 이력 항목 사이 얇은 선 반복

**Case Study** — 수평선 계층화
- 프로젝트명/날짜 메타 행 아래 굵은 선 → 본문과 명확히 분리
- 실행목적/접근과정/결과/역할 행 사이 얇은 선

**Profile Card** — 수평 + 수직 교차
- 수평 굵은 선: 헤더↔본문↔로고바 구분 (3단 구조)
- 수직 굵은 선: 프로필 사진 영역↔스펙 테이블 분리

### 절대 하지 말 것
- box-shadow로 영역 구분 (납작한 Quiet Luxury 무드와 충돌)
- 얇은 선(1px)을 섹션 경계에 사용 (위계가 사라짐)
- 굵은 선을 행 구분에 남발 (시각적 피로)
- 컬러로 배경 영역을 나누는 방식 (선 하나로 충분)

---

## AI 사용 가이드

### Claude Code에서 사용하기
이 파일을 대화에 붙여넣거나 다음과 같이 참조하세요:

```
design-guide.md의 디자인 토큰을 참고해서 [컴포넌트명] 만들어줘.
```

### Figma AI / v0.dev에서 사용하기
"CSS Custom Properties" 섹션의 코드 블록 + "Design Intent" 단락을 함께 붙여넣으세요.
무드 설명이 있어야 AI가 컴포넌트 형태를 올바르게 판단합니다.

### 새 프로젝트 시작 시
1. `--font-face` 경로를 프로젝트 `/public/fonts/` 기준으로 수정
2. CSS Custom Properties 블록을 `globals.css` 또는 최상위 CSS에 붙여넣기
3. 액센트 컬러 필요 시 `:root` 블록에 `--color-accent` 추가
