# Marketing Automation Platform - Design Guide

> 마케팅 자동화 플랫폼의 비주얼 디자인 시스템

---

## 디자인 철학

- **미니멀리즘**: aerse.store 영감, 흑백 베이스 + 컬러 포인트
- **명확한 계층**: 정보 우선순위를 시각적으로 명확하게
- **일관성**: 4색 시스템으로 통일된 디자인 언어

---

## 색상 시스템

### 컬러 팔레트

```css
:root {
  --bg: #F0EFEA;        /* Background */
  --primary: #1a1a1a;   /* Primary */
  --accent: #6366F1;    /* Accent */
  --success: #10B981;   /* Success */
}
```

### 색상 사용

| 색상 | 용도 |
|------|------|
| `#F0EFEA` | 페이지 배경 |
| `#1a1a1a` | 헤더, 사이드바, 본문 텍스트 |
| `#6366F1` | CTA 버튼, 활성 상태, 링크, 커서 |
| `#10B981` | 긍정 지표, 성공 메시지 |

### 투명도 활용

```css
/* 필요 시 사용 */
rgba(99, 102, 241, 0.1)   /* Accent 10% */
rgba(99, 102, 241, 0.2)   /* Accent 20% */
rgba(26, 26, 26, 0.6)     /* Primary 60% */
rgba(0, 0, 0, 0.06)       /* Border */
```

---

## 타이포그래피

### 폰트

```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
```

### 타입 스케일

| 용도 | Size | Weight | Letter Spacing |
|------|------|--------|----------------|
| Page Title | 28px | 300 | -0.5px |
| Card Title | 18px | 500 | 0 |
| Body | 14px | 400 | 0 |
| Label | 13px | 500 | 0 |
| Caption | 12px | 600 | 0.5px |

---

## 레이아웃

### Grid

```css
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}
```

### Spacing

```css
--space-xs: 8px;
--space-sm: 16px;
--space-md: 24px;
--space-lg: 32px;
--space-xl: 48px;
```

---

## 컴포넌트 스타일

### Header

```css
header {
  background: var(--primary);
  padding: 16px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  color: white;
  font-size: 20px;
  font-weight: 600;
  letter-spacing: -0.5px;
}
```

### Sidebar

```css
.sidebar {
  width: 240px;
  background: var(--primary);
  padding: 24px 0;
}

.nav-item {
  padding: 12px 24px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  transition: all 0.2s;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-item.active {
  background: var(--accent);
  color: white;
}
```

### Stat Card

```css
.stat-card {
  background: white;
  padding: 24px;
  border-radius: 8px;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.stat-label {
  font-size: 13px;
  color: rgba(26, 26, 26, 0.6);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 32px;
  font-weight: 300;
}

.stat-change {
  font-size: 13px;
  color: var(--success);
  font-weight: 500;
}
```

### Button

```css
/* Primary */
.btn-primary {
  background: var(--accent);
  color: white;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: #4F46E5;
  transform: translateY(-1px);
}

/* Outline */
.btn-outline {
  background: transparent;
  border: 1px solid var(--primary);
  color: var(--primary);
}

.btn-outline:hover {
  background: var(--primary);
  color: white;
}
```

### Card

```css
.card {
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 20px;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-title {
  font-size: 18px;
  font-weight: 500;
}
```

### Table

```css
table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

th {
  text-align: left;
  padding: 12px;
  font-size: 12px;
  font-weight: 600;
  color: rgba(26, 26, 26, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

td {
  padding: 16px 12px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

tbody tr:hover {
  background: rgba(99, 102, 241, 0.02);
}
```

### Input

```css
input, select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  font-size: 14px;
  background: white;
  transition: all 0.2s;
}

input:focus, select:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

label {
  display: block;
  margin-bottom: 6px;
  font-size: 13px;
  font-weight: 500;
  color: rgba(26, 26, 26, 0.8);
}
```

### Badge

```css
.badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.badge-success {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success);
}

.badge-accent {
  background: rgba(99, 102, 241, 0.1);
  color: var(--accent);
}
```

---

## 커서 인터랙션

### 기본 스타일

```css
body {
  cursor: none;
}

.cursor {
  width: 20px;
  height: 20px;
  border: 2px solid var(--accent);
  border-radius: 50%;
  position: fixed;
  pointer-events: none;
  z-index: 9999;
  transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
}

.cursor-dot {
  width: 6px;
  height: 6px;
  background: var(--primary);
  border-radius: 50%;
  position: fixed;
  pointer-events: none;
  z-index: 10000;
}
```

### 상태

```css
/* Hover */
.cursor.hover {
  width: 8px;
  height: 8px;
  background: var(--accent);
  border-color: var(--accent);
}

.cursor-dot.hover {
  width: 0;
  height: 0;
}

/* Click */
.cursor.click {
  transform: scale(0.8);
}
```

### 적용 규칙

**자석 효과 (Magnetic Snap):**
- `.nav-item`
- `.logo`
- `.user-avatar`

**일반 호버:**
- `button`, `input`, `select`
- `.stat-card`, `tr`

### 모바일

```css
@media (hover: none) {
  body { cursor: auto; }
  .cursor, .cursor-dot { display: none; }
}
```

---

## 애니메이션

### Transitions

```css
/* Global */
* {
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}

/* Button */
button {
  transition: all 0.2s;
}

button:hover {
  transform: translateY(-1px);
}

/* Card */
.stat-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}
```

---

## 반응형

### Breakpoints

```css
/* Mobile */
@media (max-width: 768px) {
  .sidebar { display: none; }
  main { padding: 20px; }
  .stats-grid { grid-template-columns: 1fr; }
  .page-title { font-size: 24px; }
}

/* Tablet */
@media (min-width: 769px) and (max-width: 1024px) {
  .sidebar { width: 200px; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
}

/* Desktop */
@media (min-width: 1025px) {
  .container { max-width: 1400px; }
}
```

---

## Streamlit 구현

### config.toml

```toml
[theme]
primaryColor = "#6366F1"
backgroundColor = "#F0EFEA"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#1a1a1a"
font = "sans serif"
```

### 커스텀 CSS

```python
import streamlit as st

st.markdown("""
<style>
/* Hide branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #1a1a1a;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: rgba(255, 255, 255, 0.7);
}

/* Metrics */
[data-testid="stMetricValue"] {
    font-size: 32px;
    font-weight: 300;
}

[data-testid="stMetricLabel"] {
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: rgba(26, 26, 26, 0.6);
}

/* Buttons */
.stButton button {
    background-color: #6366F1;
    color: white;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: 500;
    border: none;
    transition: all 0.2s;
}

.stButton button:hover {
    background-color: #4F46E5;
    transform: translateY(-1px);
}

/* Input */
.stTextInput input, .stSelectbox select {
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 6px;
}

.stTextInput input:focus, .stSelectbox select:focus {
    border-color: #6366F1;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

/* DataFrame */
.dataframe thead th {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: rgba(26, 26, 26, 0.6);
}

.dataframe tbody tr:hover {
    background: rgba(99, 102, 241, 0.02);
}
</style>
""", unsafe_allow_html=True)
```

### Altair 차트 스타일

```python
import altair as alt

# 공통 설정
def style_chart(chart):
    return chart.configure_view(
        strokeWidth=0
    ).configure_axis(
        labelFontSize=12,
        labelColor='#6a6a6a',
        titleFontSize=13,
        titleColor='#1a1a1a'
    )

# 라인 차트
line_chart = alt.Chart(df).mark_line(
    color='#6366F1',
    strokeWidth=2,
    point=True
).encode(
    x='date:T',
    y='value:Q'
)

# 바 차트
bar_chart = alt.Chart(df).mark_bar(
    color='#6366F1'
).encode(
    x='category:N',
    y='value:Q'
)
```

---

## 차트 컬러

```python
# 단일 색상
CHART_PRIMARY = '#6366F1'
CHART_SUCCESS = '#10B981'

# 멀티 색상
CHART_COLORS = ['#6366F1', '#10B981', '#F59E0B', '#EF4444']
```

---

## 접근성

### 색상 대비

- Primary (#1a1a1a) on Background (#F0EFEA): **13.8:1** ✅
- Accent (#6366F1) on White: **4.6:1** ✅

### Focus

```css
button:focus, input:focus, select:focus {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}
```

---

**Version:** 1.0.0
**Last Updated:** 2026-02-01
