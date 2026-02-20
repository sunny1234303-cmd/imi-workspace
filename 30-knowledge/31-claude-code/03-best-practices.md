# Claude Code 베스트 프랙티스

> Anthropic 공식 가이드 기반 실무 활용 팁

## 핵심 원칙

### 1. CLAUDE.md를 적극 활용하라

`CLAUDE.md`는 Claude가 대화 시작 시 자동으로 읽는 특별한 파일입니다.

```markdown
# CLAUDE.md 포함 내용

- 프로젝트 구조 설명
- 코딩 스타일 가이드
- 자주 쓰는 명령어
- 팀 규칙
```

**팁**: Git에 커밋하여 팀과 공유하세요.

### 2. 탐색 → 계획 → 실행 → 커밋

```
1. 탐색: 코드베이스 이해
2. 계획: 변경 사항 계획
3. 실행: 코드 작성
4. 커밋: 변경 사항 저장
```

이 순서를 따르면 실수가 줄어듭니다.

### 3. 서브에이전트로 컨텍스트 관리

```
❌ 모든 작업을 하나의 대화에서

✅ 복잡한 작업은 서브에이전트에게 위임
   → 메인 대화 컨텍스트 보존
   → 각 작업이 독립적으로 처리
```

---

## 서브에이전트 베스트 프랙티스

### 1. Description이 핵심

```yaml
# ❌ 나쁜 예
description: 코드 리뷰어

# ✅ 좋은 예
description: 코드 품질, 보안, 성능을 검토하는 시니어 개발자.
             PR 리뷰, 코드 분석, 리팩토링 제안 시 사용.
```

Claude는 `description`을 보고 언제 이 에이전트를 사용할지 결정합니다.
**키워드를 충분히 포함**하세요.

### 2. 도구는 최소한으로

```yaml
# ❌ 모든 도구 허용 (위험)
tools: Read, Write, Edit, Bash

# ✅ 필요한 것만 (안전)
tools: Read, Grep, Glob
```

읽기 전용 작업이면 쓰기 도구를 주지 마세요.

### 3. 모델 선택 기준

| 작업 유형 | 추천 모델 | 이유 |
|----------|----------|------|
| 파일 탐색, 간단한 분석 | `haiku` | 빠르고 저렴 |
| 코드 리뷰, 버그 수정 | `sonnet` | 균형 잡힌 성능 |
| 복잡한 설계, 창의적 작업 | `opus` | 최고 품질 |

### 4. Hooks로 안전장치 만들기

```yaml
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate.sh"
```

Bash 실행 전 스크립트로 위험한 명령을 차단할 수 있습니다.

### 5. 포그라운드 vs 백그라운드

```
포그라운드 (기본)
- 권한 물어봄
- 결과 바로 확인
- 상호작용 필요한 작업

백그라운드
- 동시에 여러 작업
- 권한 자동 거부
- 독립적인 긴 작업
```

---

## 스킬 베스트 프랙티스

### 1. 자동 발견을 위한 Description

```yaml
# ❌ 너무 일반적
description: 파일 처리

# ✅ 구체적인 키워드 포함
description: PDF 파일 처리 시 사용. 텍스트 추출, 폼 채우기,
             문서 병합. pypdf, pdfplumber 라이브러리 활용.
```

사용자가 "PDF에서 텍스트 뽑아줘"라고 하면 자동 활성화!

### 2. Progressive Disclosure (점진적 공개)

```
SKILL.md (기본 내용)
  ↓
자세한 내용은 REFERENCE.md 참조
  ↓
고급 사용법은 ADVANCED.md 참조
```

모든 내용을 SKILL.md에 넣지 말고, 필요할 때 참조하도록 분리하세요.

### 3. 스크립트 활용

```
skills/deployment/
├── SKILL.md
└── scripts/
    ├── validate.sh    # 배포 전 검증
    ├── health-check.sh # 배포 후 확인
    └── rollback.sh    # 롤백 스크립트
```

반복되는 명령은 스크립트로 만들어두세요.

---

## 슬래시 커맨드 베스트 프랙티스

### 1. 자주 쓰는 것부터

```
가장 유용한 커맨드:
- /commit - Git 커밋 자동화
- /review - 코드 리뷰
- /test - 테스트 실행 및 수정
- /docs - 문서 생성
```

### 2. 인자 힌트 명확하게

```yaml
# ❌ 힌트 없음
---
---
PR 리뷰해줘 $ARGUMENTS

# ✅ 명확한 힌트
---
argument-hint: [PR번호] [중점사항]
---
PR #$1 리뷰해줘. 중점: $2
```

### 3. Bash 명령어로 컨텍스트 제공

```markdown
## 현재 상태
- Branch: !`git branch --show-current`
- Status: !`git status --short`
- Recent: !`git log --oneline -3`

이 상태를 기반으로 작업해주세요.
```

### 4. 네임스페이스로 정리

```
commands/
├── git/
│   ├── commit.md
│   ├── branch.md
│   └── merge.md
├── docs/
│   ├── readme.md
│   └── api.md
└── test/
    └── run.md
```

---

## 멀티-Claude 워크플로우

> "여러 Claude를 병렬로 실행하는 것이 가장 강력한 활용법" - Anthropic

### 패턴 1: 작성자 + 검증자

```
Claude A: 코드 작성
    ↓
Claude B: 코드 리뷰 및 검증
    ↓
Claude A: 피드백 반영
```

### 패턴 2: 병렬 탐색

```
Claude A: 프론트엔드 분석
Claude B: 백엔드 분석
Claude C: 데이터베이스 분석
    ↓
결과 종합
```

### 패턴 3: Git Worktrees

```bash
# 같은 저장소를 여러 폴더로
git worktree add ../feature-a feature-a
git worktree add ../feature-b feature-b
```

각 폴더에서 별도 Claude 실행 → 독립적 작업

---

## 일반 팁

### 1. 컨텍스트 관리

```
/context   # 현재 사용량 확인
```

컨텍스트가 커지면:
- 새 대화 시작
- 서브에이전트에 위임
- 불필요한 파일 언급 줄이기

### 2. 권한 설정

```
/permissions
```

- 신뢰하는 작업: 자동 승인 추가
- 위험한 작업: 매번 확인

### 3. 디버깅

```bash
claude --debug
```

스킬/에이전트가 안 될 때 오류 확인

### 4. 캐시 초기화

```bash
rm -rf ~/.claude/plugins/cache
```

플러그인 문제 시 캐시 삭제

---

## 추천 시작 세트

### 개인용 커맨드 3종

```bash
mkdir -p ~/.claude/commands
```

**1. /commit**
```markdown
---
description: Git 커밋 생성
allowed-tools: Bash(git:*)
---
!`git status`
!`git diff --cached`
위 변경사항으로 커밋 메시지 작성하고 커밋해줘.
```

**2. /review**
```markdown
---
description: 코드 리뷰
---
현재 변경사항을 리뷰해줘:
- 보안 문제
- 성능 이슈
- 코드 스타일
```

**3. /explain**
```markdown
---
description: 코드 설명
argument-hint: [파일경로]
---
@$1 파일을 비전공자도 이해할 수 있게 설명해줘.
```

### 개인용 에이전트 2종

```bash
mkdir -p ~/.claude/agents
```

**1. code-reviewer.md**
```markdown
---
name: code-reviewer
description: 코드 품질, 보안, 성능 검토 전문가
tools: Read, Grep, Glob
model: sonnet
---
시니어 코드 리뷰어로서 검토합니다.
Critical → Warning → Suggestion 순서로 피드백.
```

**2. explainer.md**
```markdown
---
name: explainer
description: 코드나 개념을 쉽게 설명하는 전문가
tools: Read, Grep, Glob
model: sonnet
---
비전공자도 이해할 수 있게 설명합니다.
비유와 예시를 적극 활용.
```

---

## 체크리스트

### 새 프로젝트 시작 시

- [ ] CLAUDE.md 작성
- [ ] .claude/commands/ 폴더 생성
- [ ] 기본 커맨드 (/commit, /review) 추가
- [ ] 프로젝트 특화 스킬 고려

### 반복 작업 발견 시

- [ ] 3번 이상 반복? → 커맨드로 만들기
- [ ] 복잡한 지식 필요? → 스킬로 만들기
- [ ] 완전 위임 가능? → 서브에이전트로 만들기

### 팀 협업 시

- [ ] CLAUDE.md Git 커밋
- [ ] .claude/commands/ Git 커밋
- [ ] .claude/skills/ Git 커밋
- [ ] .claude/agents/ Git 커밋

---

## 참고 자료

- [Claude Code 공식 문서](https://code.claude.com/docs)
- [Anthropic 베스트 프랙티스](https://www.anthropic.com/engineering/claude-code-best-practices)
- [awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents)
- [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)

---

*이전: [스킬 & 슬래시 커맨드](02-skills-commands.md)*
