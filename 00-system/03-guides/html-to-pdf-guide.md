# HTML → PDF 저장 가이드

> 경력기술서·포트폴리오 HTML 파일을 PDF로 저장할 때 적용하는 인쇄 CSS 설정 가이드입니다.

---

## 기본 원칙

- **목표 페이지**: 6페이지 이내 권장
- **저장 방법**: Chrome `Cmd+P` → 대상: PDF로 저장 → 여백: 없음
- 화면 레이아웃은 유지하고, `@media print` 안에서만 인쇄 전용 스타일 적용

---

## 확정된 CSS 설정값

```css
@media print {
  @page {
    size: A4;
    margin: 20mm 22mm; /* 상하 20mm / 좌우 22mm — 가독성과 페이지 수의 균형 */
  }

  body {
    font-size: 10px;       /* 9px 이하면 가독성 저하, 11px 이상이면 페이지 초과 */
    line-height: 1.55;
    padding: 0;
    max-width: 100%;
  }

  /* 제목 위계 */
  h1 { font-size: 15px; margin-bottom: 2px; }
  h2 { font-size: 11.5px; margin-top: 28px; margin-bottom: 10px; padding-bottom: 4px; }
  h3 { font-size: 11px; margin-top: 22px; margin-bottom: 6px; }
  h4 { font-size: 10.5px; margin-top: 20px; margin-bottom: 5px; }

  /* 구분선·단락·목록 */
  hr  { margin: 12px 0; }
  p   { margin: 5px 0; orphans: 2; widows: 2; }
  ul  { padding-left: 14px; margin: 6px 0; }
  li  { margin-bottom: 2px; page-break-inside: avoid; }

  /* 표 */
  table { font-size: 10px; }
  th    { padding: 4px 8px; }
  td    { padding: 3px 8px; }

  /* 기타 */
  blockquote { padding: 5px 10px; margin: 5px 0; font-size: 9.5px; }
  .meta      { font-size: 9.5px; margin-bottom: 4px; }

  /* 페이지 잘림 방지 */
  h3, h4 { page-break-after: avoid; }
  tr     { page-break-inside: avoid; }
}
```

---

## 인라인 스타일 오버라이드

HTML에 `style="font-size: 14px"` 같은 인라인 스타일이 있으면 `@media print`의 body font-size가 먹히지 않습니다. 아래처럼 명시적으로 오버라이드해야 합니다.

```css
@media print {
  p[style*="font-size: 14px"] { font-size: 10px !important; line-height: 1.5 !important; }
  p[style*="font-size: 16px"] { font-size: 13px !important; }

  /* 자기소개 div 등 인라인 margin이 있는 경우 */
  div[style*="margin-bottom: 32px"] { margin-bottom: 20px !important; }
  p[style*="margin: 16px 0 8px"]   { margin: 14px 0 8px !important; }
  p[style*="margin: 0 0 8px"]      { margin: 0 0 8px !important; }
}
```

---

## 특정 섹션 페이지 강제 분리

특정 대섹션을 항상 새 페이지에서 시작하려면 id를 추가하고 아래 CSS를 적용합니다.

```html
<!-- HTML -->
<h2 id="detail-career">상세 경력</h2>
```

```css
/* CSS */
@media print {
  #detail-career { page-break-before: always; margin-top: 0 !important; }
}
```

> ⚠️ 섹션마다 새 페이지 강제를 남발하면 페이지 수가 급증합니다. 꼭 필요한 대섹션 1~2곳에만 적용하세요.

---

## 페이지 수 조정 기준

| 상황 | 조치 |
|------|------|
| 페이지 수 너무 많음 | `@page margin` 축소, `font-size` 감소, `h2/h3 margin-top` 감소 |
| 내용이 잘려 읽기 불편 | `page-break-inside: avoid`, `orphans/widows` 설정 확인 |
| 여백이 너무 좁음 | `@page margin` 확대 (단, 페이지 수 증가 감수) |
| 자기소개 폰트가 큼 | 인라인 스타일 오버라이드 섹션 참고 |

---

## 적용 사례

- `10-projects/16-personal-portfolio/10-kurly-경력기술서.html` — 6페이지, 상하 20mm / 좌우 22mm
