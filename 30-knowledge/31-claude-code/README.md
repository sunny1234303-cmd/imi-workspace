# Claude Code 서브에이전트 & 스킬 가이드

> 비전공자를 위한 친절한 공식 문서 정리

## 이 가이드의 목적

Claude Code를 더 강력하게 사용하기 위한 **서브에이전트**와 **스킬** 만들기를 배웁니다.

## 핵심 개념 한눈에 보기

| 개념 | 쉬운 설명 | 예시 |
|------|----------|------|
| **서브에이전트** | 특정 일만 하는 전문가 비서 | 코드 리뷰어, 디버거, 번역가 |
| **스킬** | Claude가 자동으로 사용하는 지식 | PDF 처리법, 데이터 분석법 |
| **슬래시 커맨드** | 내가 직접 부르는 단축 명령어 | `/review`, `/commit` |

### 비유로 이해하기

```
당신(사용자)
    ↓
Claude (메인 비서)
    ↓
서브에이전트들 (전문가 팀)
├── 코드리뷰어 (코드 검토 전문)
├── 디버거 (오류 해결 전문)
└── 번역가 (다국어 전문)
```

**스킬**은 Claude가 참고하는 "매뉴얼"이고,
**슬래시 커맨드**는 자주 쓰는 "단축키"입니다.

## 문서 구성

1. **[서브에이전트 가이드](01-subagents.md)** - 전문가 비서 만들기
2. **[스킬 & 슬래시 커맨드](02-skills-commands.md)** - 자동화 명령어 만들기
3. **[베스트 프랙티스](03-best-practices.md)** - 실무 활용 팁

## 파일 저장 위치 요약

```
개인용 (모든 프로젝트에서 사용)
~/.claude/
├── agents/     ← 서브에이전트
├── skills/     ← 스킬
└── commands/   ← 슬래시 커맨드

프로젝트용 (팀과 공유)
.claude/
├── agents/
├── skills/
└── commands/
```

## 참고 링크

- [Claude Code 서브에이전트 공식 문서](https://code.claude.com/docs/en/sub-agents)
- [Claude Code 슬래시 커맨드 공식 문서](https://code.claude.com/docs/en/slash-commands)
- [Claude Code 스킬 공식 문서](https://code.claude.com/docs/en/skills)
- [Claude Code 베스트 프랙티스](https://www.anthropic.com/engineering/claude-code-best-practices)

---

*작성일: 2026-01-20*
