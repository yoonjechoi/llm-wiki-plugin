"""llm-wiki 시험 — 임시 HOME 에서만 돈다(실제 지식베이스 · 설정을 건드리지 않는다).

  python3 -m unittest tests.test_wiki
"""
import json, os, pathlib, re, shutil, subprocess, sys, tempfile, unittest

PLUGIN = pathlib.Path(__file__).resolve().parents[1] / "plugins" / "llm-wiki"
WIKI = PLUGIN / "scripts" / "wiki.py"


class Base(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp()).resolve()
        self.home = self.root / "home"
        self.home.mkdir()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def run_wiki(self, *a):
        env = dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home),
                   GIT_CONFIG_GLOBAL=str(self.root / "nogit"), GIT_CONFIG_NOSYSTEM="1")
        return subprocess.run([sys.executable, str(WIKI), *map(str, a)], env=env, capture_output=True, text=True, encoding="utf-8")

    @property
    def kb(self):
        return self.home / "llm-wiki"


class Setup(Base):
    def test_setup_makes_three_layers(self):
        r = self.run_wiki("setup")
        self.assertEqual(r.returncode, 0, r.stderr)
        for d in ("raw", "raw/assets", "wiki/sources", "wiki/entities", "wiki/concepts", "wiki/analyses"):
            self.assertTrue((self.kb / d).is_dir(), d)
        for f in ("CLAUDE.md", "wiki/index.md", "wiki/log.md", "wiki/overview.md"):
            self.assertTrue((self.kb / f).is_file(), f)
        log = (self.kb / "wiki/log.md").read_text(encoding="utf-8")
        self.assertRegex(log, r"## \[\d{4}-\d{2}-\d{2}\] setup \| ")
        self.assertNotIn("{{오늘}}", log + (self.kb / "wiki/overview.md").read_text(encoding="utf-8"))
        if shutil.which("git"):
            self.assertTrue((self.kb / ".git").exists())

    def test_setup_keeps_existing_files(self):
        self.run_wiki("setup")
        (self.kb / "CLAUDE.md").write_text("내 schema", encoding="utf-8")
        r = self.run_wiki("setup")
        self.assertIn("없음(이미 있었어요)", r.stdout)
        self.assertEqual((self.kb / "CLAUDE.md").read_text(encoding="utf-8"), "내 schema")

    def test_setup_other_folder_sets_config(self):
        other = (self.root / "다른 곳").resolve()
        self.run_wiki("setup", other)
        self.assertTrue((other / "wiki/index.md").exists())
        self.assertIn(str(other), self.run_wiki("where").stdout)
        cfg = json.loads((self.home / ".config/llm-wiki/config.json").read_text(encoding="utf-8"))
        self.assertEqual(cfg["wiki"], str(other))

    def test_where_before_setup(self):
        self.assertIn("setup 부터", self.run_wiki("where").stdout)


class Pending(Base):
    def test_pending_lists_raw_not_in_any_source_page(self):
        self.run_wiki("setup")
        (self.kb / "raw/한글 글.md").write_text("본문", encoding="utf-8")
        (self.kb / "raw/b.md").write_text("본문", encoding="utf-8")
        (self.kb / "raw/assets/그림.png").write_bytes(b"x")
        (self.kb / "wiki/sources/b.md").write_text("---\nsources: [raw/b.md]\n---\n# b\n", encoding="utf-8")
        out = self.run_wiki("pending").stdout
        self.assertIn("raw/한글 글.md", out)
        self.assertNotIn("raw/b.md", out)
        self.assertNotIn("그림.png", out)
        (self.kb / "wiki/sources/a.md").write_text("---\nsources: [raw/한글 글.md]\n---\n", encoding="utf-8")
        self.assertIn("모두 ingest 됨", self.run_wiki("pending").stdout)


class Docs(unittest.TestCase):
    def test_skills_and_agent(self):
        for s in ("setup", "ingest", "query", "lint"):
            t = (PLUGIN / "skills" / s / "SKILL.md").read_text(encoding="utf-8")
            head = t.split("---")[1]
            self.assertIn(f"name: {s}", head)
            self.assertIn("description:", head)
            self.assertIn("CLAUDE.md", t)
            self.assertIn("../../scripts/wiki.py", t)
        agent = (PLUGIN / "agents" / "batch-ingester.md").read_text(encoding="utf-8")
        self.assertNotIn("\nmodel:", agent.split("---")[1])   # 쓰는 사람의 기본 설정 모델로 돈다
        ingest = (PLUGIN / "skills/ingest/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("llm-wiki:batch-ingester", ingest)
        self.assertIn("run_in_background: true", ingest)
        self.assertIn("## 테스트 시나리오", ingest)

    def test_log_prefix_is_gist_form(self):
        for f in ("templates/log.md", "templates/schema.md", "skills/ingest/SKILL.md", "skills/query/SKILL.md", "skills/lint/SKILL.md"):
            self.assertRegex((PLUGIN / f).read_text(encoding="utf-8"), r"## \[(YYYY-MM-DD|오늘|\{\{오늘\}\})\] (ingest|query|lint|setup) \|", f)

    def test_no_wiki_word_to_people(self):
        for s in ("setup", "ingest", "query", "lint"):
            self.assertIn("「지식베이스」", (PLUGIN / "skills" / s / "SKILL.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
