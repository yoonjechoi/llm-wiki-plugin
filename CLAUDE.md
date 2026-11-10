## 하네스: llm-wiki (카파시 LLM Wiki 지식베이스 플러그인)

**목표:** 카파시 LLM Wiki gist 를 그대로 옮긴 개인 지식베이스 — raw · wiki · schema 세 층, setup 한 번과 ingest · query · lint.

**호출 조건:** 이 저장소는 플러그인 소스다. 지식베이스 일은 `llm-wiki:setup` · `llm-wiki:ingest` · `llm-wiki:query` · `llm-wiki:lint` 스킬로 하고, 일괄 넣기는 ingest 가 `llm-wiki:batch-ingester` 를 백그라운드로 부른다. 개발 · 시험은 `--plugin-dir plugins/llm-wiki` 로 한다. 설계를 바꿀 때는 gist(https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)와 견준다.

**변경 이력:**
| 날짜 | 변경 내용 | 대상 | 사유 |
|------|----------|------|------|
| 2026-11-11 | Harness v2로 처음 구성(스킬 4 · 에이전트 1 · 도우미 wiki.py) | 전체 | 저장소 주인 요청 — 「karpathy gist 대로 llm wiki 를 새로」. knowledge-base 플러그인과 따로, 빈 폴더에서 시작, ingest 는 함께 넣기 + 일괄 넣기 둘 다 |
