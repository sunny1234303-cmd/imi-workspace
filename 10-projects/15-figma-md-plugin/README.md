# Markdown to Figma — by Aha Marketing

Aha Marketing에서 생성한 마케팅 콘텐츠(SNS 카피, 광고 카피, 리포트 등)를
`.md` 파일로 내보내 Figma 캔버스에 바로 삽입하는 플러그인입니다.

## 설치 방법

### 방법 A — Figma Community (추천)
> 준비 중 (출시 예정)

### 방법 B — 직접 설치 (개발자 모드)

1. 이 플러그인 폴더를 로컬에 다운로드
   ```
   10-projects/15-figma-md-plugin/
   ├── manifest.json
   ├── code.js
   └── ui.html
   ```
2. **Figma 데스크탑 앱** 실행 (웹 버전 불가)
3. 임의의 파일 열기
4. 상단 메뉴 → `Plugins` → `Development` → `Import plugin from manifest...`
5. `manifest.json` 선택

## 사용 방법

1. `Plugins` → `Development` → **Markdown to Figma by Aha Marketing** 실행
2. `.md` 파일을 드래그하거나 파일 선택 (여러 개 동시 가능)
3. 설정 선택:
   - **폰트**: Inter, Noto Sans KR 등 Figma에 설치된 폰트 이름 입력
   - **크기**: 기본 글자 크기 (H1은 자동으로 2.25배 적용)
   - **테마**: Light / Dark / Brand (Aha 보라색)
   - **타입**: Doc(800px) / SNS(1080px) / Ad(1200px) / Report(1440px)
4. **Figma에 삽입** 클릭
5. 삽입 후 Figma에서 자유롭게 편집 (폰트, 색상, 레이아웃 모두 가능)

## 지원 마크다운 요소

| 요소 | 문법 |
|------|------|
| 제목 H1~H3 | `# ## ###` |
| 문단 | 일반 텍스트 |
| 순서 없는 목록 | `- * +` |
| 순서 있는 목록 | `1. 2. 3.` |
| 표 | `\| col \| col \|` |
| 구분선 | `---` |
| Frontmatter | 자동 제거 |

## 워크플로우

```
Aha Marketing → 콘텐츠 생성 → .md 다운로드
→ Figma 플러그인 실행 → 설정 선택 → 캔버스 삽입
→ Figma에서 디자인 마무리
```
