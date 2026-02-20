# 스킬 & 슬래시 커맨드 완벽 가이드

> 반복 작업을 자동화하는 두 가지 방법

## 스킬 vs 슬래시 커맨드

| 구분 | 슬래시 커맨드 | 스킬 |
|------|-------------|------|
| **비유** | 단축키 | 전문 매뉴얼 |
| **호출 방식** | `/명령어` 직접 입력 | Claude가 자동 선택 |
| **구조** | 파일 1개 (.md) | 폴더 + 여러 파일 |
| **복잡도** | 간단한 프롬프트 | 복잡한 워크플로우 |
| **용도** | 자주 쓰는 명령 | 전문 지식/프로세스 |

### 언제 뭘 쓸까?

```
✅ 슬래시 커맨드 사용:
   - 자주 반복하는 간단한 작업
   - 명확히 내가 호출하고 싶을 때
   - 빠른 단축키가 필요할 때

✅ 스킬 사용:
   - 여러 참고 자료가 필요한 복잡한 작업
   - Claude가 알아서 판단해서 사용하길 원할 때
   - 팀 전체가 공유할 표준 프로세스
```

---

# Part 1: 슬래시 커맨드

## 슬래시 커맨드란?

`/명령어`로 시작하는 단축 명령어입니다.
자주 쓰는 프롬프트를 파일로 저장해두고 간편하게 호출합니다.

## 저장 위치

```bash
# 개인용 (모든 프로젝트에서 사용)
~/.claude/commands/명령어.md

# 프로젝트용 (팀과 공유)
.claude/commands/명령어.md
```

## 첫 번째 커맨드 만들기

### 1단계: 폴더 생성

```bash
# 개인용 커맨드 폴더
mkdir -p ~/.claude/commands

# 또는 프로젝트용
mkdir -p .claude/commands
```

### 2단계: 파일 생성

`~/.claude/commands/review.md`:

```markdown
이 코드를 검토해주세요:
- 보안 취약점
- 성능 문제
- 코드 스타일
```

### 3단계: 사용

```
/review
```

끝! 이제 `/review`만 입력하면 위 프롬프트가 자동 실행됩니다.

## 파일 구조 이해하기

### 기본 구조

```markdown
여기에 프롬프트 내용을 적습니다.
설정 없이 바로 사용 가능합니다.
```

### 설정 추가 구조

```markdown
---
description: 이 커맨드가 하는 일
allowed-tools: Read, Grep
argument-hint: [파일명]
---

여기에 프롬프트 내용을 적습니다.
```

## 설정 옵션 상세

### 주요 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `description` | 커맨드 설명 | "코드 리뷰 실행" |
| `allowed-tools` | 허용할 도구 | `Read, Grep, Bash` |
| `argument-hint` | 인자 힌트 | `[파일명] [옵션]` |
| `model` | 사용할 모델 | `claude-3-5-haiku-20241022` |
| `context` | 실행 컨텍스트 | `fork` (분리 실행) |

### 인자(Arguments) 사용하기

#### 모든 인자: `$ARGUMENTS`

```markdown
---
argument-hint: [메시지]
---
다음 내용으로 커밋해줘: $ARGUMENTS
```

사용: `/commit 버그 수정 완료`
→ "다음 내용으로 커밋해줘: 버그 수정 완료"

#### 개별 인자: `$1`, `$2`, `$3`...

```markdown
---
argument-hint: [파일] [언어]
---
$1 파일을 $2로 번역해줘
```

사용: `/translate README.md 한국어`
→ "README.md 파일을 한국어로 번역해줘"

## 고급 기능

### Bash 명령어 실행

`!` 백틱 안에 명령어를 넣으면 실행 결과를 가져옵니다:

```markdown
---
description: Git 상태 확인 후 커밋
allowed-tools: Bash(git:*)
---

## 현재 상태

- Git 상태: !`git status`
- 현재 브랜치: !`git branch --show-current`
- 최근 커밋: !`git log --oneline -5`

## 할 일

위 변경사항을 기반으로 커밋 메시지를 작성해주세요.
```

### 파일 참조

`@` 기호로 파일 내용을 가져옵니다:

```markdown
@src/main.js 파일을 분석해주세요.

@old-version.js와 @new-version.js를 비교해주세요.
```

### 네임스페이스 (폴더 구조)

커맨드가 많아지면 폴더로 정리할 수 있습니다:

```
.claude/commands/
├── git/
│   ├── commit.md     → /commit (project:git)
│   └── review.md     → /review (project:git)
├── docs/
│   └── generate.md   → /generate (project:docs)
└── deploy.md         → /deploy (project)
```

## 실전 예제

### 예제 1: Git 커밋

```markdown
---
description: 변경사항 확인 후 커밋 생성
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
argument-hint: [커밋 메시지]
---

## 현재 상태

!`git status`

## 변경 내용

!`git diff --cached`

## 작업

커밋 메시지: $ARGUMENTS
위 변경사항을 커밋해주세요.
```

### 예제 2: PR 리뷰

```markdown
---
description: Pull Request 리뷰
argument-hint: [PR번호] [중점사항]
---

PR #$1을 리뷰해주세요.

중점 검토 사항: $2

확인할 것:
- 보안 취약점
- 성능 영향
- 코드 스타일 일관성
- 테스트 커버리지
```

### 예제 3: 문서 생성

```markdown
---
description: 함수/클래스 문서 자동 생성
argument-hint: [파일경로]
---

@$1 파일을 읽고 다음을 생성해주세요:

1. 각 함수/클래스에 대한 docstring
2. 사용 예제
3. 파라미터 설명
```

### 예제 4: 다국어 번역

```markdown
---
description: 마크다운 파일 번역
argument-hint: [파일] [타겟언어]
---

@$1 파일을 $2로 번역해주세요.

규칙:
- 기술 용어는 원어 유지 (예: API, JSON)
- 코드 블록은 번역하지 않음
- 자연스러운 표현 사용
```

---

# Part 2: 스킬 (Agent Skills)

## 스킬이란?

Claude가 특정 작업을 할 때 자동으로 참조하는 **전문 지식 패키지**입니다.

### 슬래시 커맨드와의 차이

```
슬래시 커맨드: 내가 "/리뷰" 입력 → 실행

스킬: 내가 "이 코드 봐줘" → Claude가 "리뷰 스킬이 있네!"
      → 자동으로 스킬 사용
```

## 저장 위치

```bash
# 개인용
~/.claude/skills/스킬이름/
├── SKILL.md          # 필수: 스킬 설명
├── REFERENCE.md      # 선택: 참고 자료
└── scripts/          # 선택: 스크립트
    └── validate.sh

# 프로젝트용
.claude/skills/스킬이름/
└── SKILL.md
```

**중요**: 스킬은 **폴더**이고, 그 안에 `SKILL.md` 파일이 필수입니다.

## 첫 번째 스킬 만들기

### 1단계: 폴더 생성

```bash
mkdir -p ~/.claude/skills/code-review
```

### 2단계: SKILL.md 작성

`~/.claude/skills/code-review/SKILL.md`:

```markdown
---
name: code-review
description: 코드 리뷰 요청 시 사용. 보안, 성능, 스타일 검토.
---

# 코드 리뷰 스킬

코드를 검토할 때 다음을 확인합니다:

## 체크리스트

1. **보안**
   - SQL 인젝션
   - XSS 취약점
   - 민감 정보 노출

2. **성능**
   - 불필요한 루프
   - N+1 쿼리
   - 메모리 누수

3. **스타일**
   - 일관된 네이밍
   - 적절한 주석
   - 코드 중복
```

### 3단계: 사용

그냥 자연스럽게 요청하면 됩니다:

```
이 코드 리뷰해줘
```

Claude가 `description`을 보고 자동으로 스킬을 사용합니다.

## SKILL.md 구조

### 기본 구조

```markdown
---
name: 스킬이름
description: 언제 이 스킬을 사용할지 설명
---

# 스킬 제목

여기에 Claude가 따를 지침을 작성합니다.
```

### 설정 옵션

| 옵션 | 필수 | 설명 |
|------|------|------|
| `name` | ✅ | 스킬 이름 (영어, 소문자, 하이픈) |
| `description` | ✅ | 언제 사용할지 설명 (Claude가 판단 기준으로 사용) |
| `allowed-tools` | ❌ | 허용할 도구 |
| `model` | ❌ | 사용할 모델 |
| `context` | ❌ | `fork`로 설정하면 분리 컨텍스트 |
| `user-invocable` | ❌ | `false`면 슬래시 메뉴에서 숨김 |

## 멀티 파일 스킬

복잡한 스킬은 여러 파일로 구성할 수 있습니다:

```
.claude/skills/deployment/
├── SKILL.md           # 메인 설명
├── CHECKLIST.md       # 배포 체크리스트
├── ROLLBACK.md        # 롤백 절차
└── scripts/
    ├── validate.sh    # 검증 스크립트
    └── health-check.sh
```

`SKILL.md`에서 다른 파일 참조:

```markdown
---
name: deployment
description: 프로덕션 배포 시 사용
---

# 배포 스킬

배포 전 [체크리스트](CHECKLIST.md) 확인
문제 발생 시 [롤백 절차](ROLLBACK.md) 참조
```

## 실전 예제

### 예제 1: PDF 처리

```
~/.claude/skills/pdf-processing/
├── SKILL.md
├── FORMS.md
└── scripts/
    └── extract.py
```

`SKILL.md`:
```markdown
---
name: pdf-processing
description: PDF 파일 처리 시 사용. 텍스트 추출, 폼 채우기, 병합.
allowed-tools: Read, Bash(python:*)
---

# PDF 처리 스킬

## 빠른 시작

텍스트 추출:
```python
import pdfplumber
with pdfplumber.open("doc.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

폼 채우기는 [FORMS.md](FORMS.md) 참조.

## 필요 패키지

```bash
pip install pypdf pdfplumber
```
```

### 예제 2: API 설계

```markdown
---
name: api-design
description: REST API 설계 시 사용. 엔드포인트, 응답 형식, 에러 처리.
---

# API 설계 스킬

## 명명 규칙

- 복수형 명사 사용: `/users`, `/posts`
- 케밥 케이스: `/user-profiles`
- 버전 포함: `/api/v1/users`

## 응답 형식

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "page": 1,
    "total": 100
  }
}
```

## 에러 형식

```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "User not found"
  }
}
```

## HTTP 상태 코드

| 코드 | 용도 |
|------|------|
| 200 | 성공 |
| 201 | 생성 성공 |
| 400 | 잘못된 요청 |
| 401 | 인증 필요 |
| 403 | 권한 없음 |
| 404 | 찾을 수 없음 |
| 500 | 서버 오류 |
```

### 예제 3: 테스트 작성

```markdown
---
name: test-writing
description: 테스트 코드 작성 시 사용. 단위 테스트, 통합 테스트.
---

# 테스트 작성 스킬

## 테스트 구조 (AAA 패턴)

```javascript
describe('함수명', () => {
  it('예상 동작 설명', () => {
    // Arrange (준비)
    const input = 'test';

    // Act (실행)
    const result = myFunction(input);

    // Assert (검증)
    expect(result).toBe('expected');
  });
});
```

## 좋은 테스트 이름

❌ `test1`, `testFunction`
✅ `should return user when valid ID provided`
✅ `throws error when email is invalid`

## 테스트 우선순위

1. 핵심 비즈니스 로직
2. 에러 케이스
3. 경계값
4. 엣지 케이스
```

---

# Part 3: 비교 및 선택 가이드

## 한눈에 비교

| 항목 | 슬래시 커맨드 | 스킬 | 서브에이전트 |
|------|-------------|------|-------------|
| 호출 | `/명령어` | 자동 | 자동 또는 명시적 |
| 구조 | 파일 1개 | 폴더 | 파일 1개 |
| 컨텍스트 | 공유 | 공유 | 분리 |
| 복잡도 | 간단 | 중간~복잡 | 복잡 |
| 용도 | 단축키 | 지식/프로세스 | 전문가 위임 |

## 언제 뭘 쓸까?

```
"자주 쓰는 프롬프트를 단축하고 싶어"
→ 슬래시 커맨드

"Claude가 특정 지식을 자동으로 참조했으면 좋겠어"
→ 스킬

"특정 작업을 완전히 위임하고 싶어"
→ 서브에이전트
```

## 실무 추천 조합

### 코드 리뷰 워크플로우

```
/review (슬래시 커맨드)
  → code-review 스킬 참조
  → 필요시 code-reviewer 서브에이전트 호출
```

### 배포 워크플로우

```
/deploy (슬래시 커맨드)
  → deployment 스킬의 체크리스트 참조
  → 자동 검증 스크립트 실행
```

---

*이전: [서브에이전트](01-subagents.md) | 다음: [베스트 프랙티스](03-best-practices.md)*
