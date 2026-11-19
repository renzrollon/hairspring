from __future__ import annotations

import json
import os
import textwrap

import pytest

from tools_helpers import REPO_ROOT, findings_by_code


def run(vc, catalogue, *argv):
    return vc.main(["--root", str(catalogue.root), *argv])


def codes(vc, catalogue, name=None, **kw):
    return findings_by_code(vc.validate(catalogue.root, **kw), name)


def errors(found):
    return {k: v for k, v in found.items() if k.startswith("error:")}


@pytest.fixture(params=["pyyaml", "builtin"])
def parser_mode(request, monkeypatch):
    if request.param == "pyyaml":
        pytest.importorskip("yaml")
        monkeypatch.setenv("RE_SKILLS_YAML", "auto")
    else:
        monkeypatch.setenv("RE_SKILLS_YAML", "builtin")
    return request.param


# ---------------------------------------------------------------- the happy path

def test_valid_catalogue_passes(vc, catalogue, capsys, parser_mode):
    catalogue.skill("requirement-phrasing", outputs_to="requirement-linter")
    catalogue.skill("requirement-linter", stage="validation", inputs_from="requirement-phrasing")
    catalogue.skill("re-setup", stage="foundations", invocation="user",
                    extra_keys='argument-hint: "[folder]"\n')
    catalogue.skill("re-ids", stage="_primitives", invocation="primitive")
    assert run(vc, catalogue) == 0
    out = capsys.readouterr().out
    assert "4 skill(s) checked: 4 ok, 0 with errors; 0 error(s), 0 warning(s)" in out
    assert "ok    skills/specification/requirement-phrasing" in out


def test_json_report(vc, catalogue, capsys):
    catalogue.skill("requirement-phrasing")
    catalogue.write("skills/specification/requirement-phrasing/references/ireb-anchor.md", "no disclaimer\n")
    assert run(vc, catalogue, "--format", "json") == 1
    doc = json.loads(capsys.readouterr().out)
    assert doc["summary"]["error_codes"] == {"ireb-anchor": 1}
    assert doc["skills"][0]["findings"][0]["code"] == "ireb-anchor"


# ---------------------------------------------------------------- frontmatter

def test_missing_and_broken_frontmatter(vc, catalogue, parser_mode):
    catalogue.skill("no-front", frontmatter="")
    catalogue.write("skills/specification/no-front/SKILL.md", "# Title\n\nno frontmatter\n")
    catalogue.skill("bad-yaml")
    catalogue.write("skills/specification/bad-yaml/SKILL.md", "---\nname: [unclosed\n---\n# T\n")
    catalogue.skill("empty-file")
    catalogue.write("skills/specification/empty-file/SKILL.md", "")
    found = codes(vc, catalogue)
    assert len(found["error:frontmatter"]) == 3


def test_unknown_key_and_name_rules(vc, catalogue):
    catalogue.skill("Bad_Name", extra_keys="tools: [Read]\n")
    catalogue.skill("other-folder", frontmatter=None)
    catalogue.write("skills/specification/other-folder/SKILL.md",
                    (catalogue.root / "skills/specification/other-folder/SKILL.md").read_text()
                    .replace("name: other-folder", "name: renamed"))
    long = "a" * 65
    catalogue.skill(long)
    found = codes(vc, catalogue)
    names = " ".join(found["error:name"])
    assert "kebab-case" in names and "must equal the folder name 'other-folder'" in names and "limit is 64" in names
    assert any("'tools' is not allowed" in m for m in found["error:keys"])


def test_description_rules(vc, catalogue):
    body = "Does one thing. " * 70
    catalogue.skill("too-long", frontmatter=textwrap.dedent(f"""\
        name: too-long
        description: "{body} Use when x. Not for y."
        license: MIT
        metadata:
          stage: specification
          invocation: model
          priority: P1
          ireb-anchor: "CPRE FL Handbook 1.2 §3.3"
          inputs-from: "none"
          outputs-to: "none"
          work-product: "x"
          version: "0.1.0"
        """))
    catalogue.skill("no-triggers")
    path = catalogue.root / "skills/specification/no-triggers/SKILL.md"
    path.write_text(path.read_text().replace("Use when", "Handy if").replace("Not for", "Avoid for"))
    found = codes(vc, catalogue)
    messages = " ".join(found["error:description"])
    assert "limit is 1024" in messages and '"Use when' in messages and '"Not for' in messages


def test_description_rejects_xml_like_tags(vc, catalogue):
    catalogue.skill("tagged")
    path = catalogue.root / "skills/specification/tagged/SKILL.md"
    path.write_text(path.read_text().replace("Use when", "Writes notes-<slug>.md. Use when", 1))
    found = codes(vc, catalogue)
    assert any("XML-like tags" in m and "<slug>" in m for m in found["error:description"])


def test_license_and_compatibility(vc, catalogue):
    catalogue.skill("apache", extra_keys="compatibility: Python 3.9+\n")
    path = catalogue.root / "skills/specification/apache/SKILL.md"
    path.write_text(path.read_text().replace("license: MIT", "license: Apache-2.0"))
    found = codes(vc, catalogue)
    assert found["error:license"] and found["warning:compatibility"]
    (catalogue.root / "skills/specification/apache/scripts").mkdir()
    assert "warning:compatibility" not in codes(vc, catalogue)


def test_metadata_rules(vc, catalogue):
    catalogue.skill("meta-bad", frontmatter=textwrap.dedent("""\
        name: meta-bad
        description: Does x. Use when y. Not for z.
        license: MIT
        metadata:
          stage: specification
          invocation: model
          priority: high
          ireb-anchor: "none given"
          inputs-from: "none"
          work-product: "x"
          version: 1.0
          owner: "me"
        """))
    found = codes(vc, catalogue)
    messages = " ".join(found["error:metadata"])
    assert "metadata.outputs-to is missing" in messages
    assert "'owner' is not allowed" in messages
    assert "metadata.version must be a string" in messages
    assert "priority 'high'" in messages
    assert found["warning:ireb-anchor"]


def test_stage_must_match_folder(vc, catalogue):
    catalogue.skill("misplaced", stage="validation")
    path = catalogue.root / "skills/validation/misplaced/SKILL.md"
    path.write_text(path.read_text().replace("stage: validation", "stage: specification"))
    catalogue.skill("odd-stage", stage="misc")
    found = codes(vc, catalogue)
    assert any("does not match the folder skills/validation/" in m for m in found["error:stage"])
    assert any("'misc' is not a stage" in m for m in found["error:stage"])


@pytest.mark.parametrize("invocation,extra,expected", [
    ("user", "", "must set disable-model-invocation: true"),
    ("model", "disable-model-invocation: true\n", "must not set disable-model-invocation"),
    ("model", "user-invocable: false\n", "must not set user-invocable: false"),
    ("primitive", "", "must set user-invocable: false"),
    ("user", 'disable-model-invocation: "true"\n', "must be true or false"),
])
def test_invocation_consistency(vc, catalogue, invocation, extra, expected):
    stage = "_primitives" if invocation == "primitive" else "specification"
    folder = catalogue.skill("mode-skill", stage=stage, invocation="model")
    path = folder / "SKILL.md"
    text = path.read_text().replace("invocation: model", f"invocation: {invocation}")
    text = text.replace("stage: specification", "stage: primitives") if stage == "_primitives" else text
    path.write_text(text.replace("license: MIT\n", "license: MIT\n" + extra))
    found = codes(vc, catalogue)
    assert any(expected in m for m in found.get("error:invocation", [])), found


def test_primitive_outside_primitives_folder(vc, catalogue):
    catalogue.skill("helper", invocation="primitive")
    found = codes(vc, catalogue)
    assert any("primitives live in skills/_primitives/" in m for m in found["error:invocation"])


def test_argument_hint_only_for_user_skills(vc, catalogue):
    catalogue.skill("hinted", extra_keys='argument-hint: "[x]"\n')
    assert codes(vc, catalogue)["warning:keys"]


# ---------------------------------------------------------------- body

def test_line_budgets(vc, catalogue):
    filler = "\n".join(f"- line {n}" for n in range(160))
    catalogue.skill("long-model", body=vc_body(filler))
    catalogue.skill("long-user", stage="foundations", invocation="user", body=vc_body(filler + "\n" + filler))
    found = codes(vc, catalogue)
    assert any("model-invoked skills must stay under 150" in m for m in found["error:line-budget"])
    assert any("aim for under 250" in m for m in found["warning:line-budget"])


def vc_body(filler):
    from tools_helpers import BODY
    return BODY.format(title="Long").replace("## Quality checks", filler + "\n\n## Quality checks")


def test_headings_missing_out_of_order_and_fenced(vc, catalogue):
    from tools_helpers import BODY
    body = BODY.format(title="X").replace("## Inputs", "## Input")
    catalogue.skill("missing-heading", body=body)
    swapped = BODY.format(title="X").replace("## Outputs", "## TMP").replace("## Inputs", "## Outputs").replace("## TMP", "## Inputs")
    catalogue.skill("swapped", body=swapped)
    fenced = "# X\n\n```markdown\n## When not to use\n## Inputs\n## Outputs\n## Procedure\n## Quality checks\n## Hand-offs\n```\n"
    catalogue.skill("fenced", body=fenced)
    found = codes(vc, catalogue)
    assert any("missing section '## Inputs'" in m for m in found["error:headings"])
    assert any("out of order" in m for m in found["error:headings"])
    assert len([m for m in found["error:headings"] if "missing section" in m]) == 1 + 6


def test_optional_section_before_handoffs_is_a_warning(vc, catalogue):
    from tools_helpers import BODY
    body = BODY.format(title="X").replace("## Quality checks", "## Non-interactive mode\n\nx\n\n## Quality checks")
    catalogue.skill("early-optional", body=body)
    found = codes(vc, catalogue)
    assert found["warning:headings"] and not errors(found)


def test_ireb_anchor(vc, catalogue):
    folder = catalogue.skill("no-anchor")
    (folder / "references" / "ireb-anchor.md").unlink()
    folder2 = catalogue.skill("bad-anchor")
    (folder2 / "references" / "ireb-anchor.md").write_text("# anchor\n")
    found = codes(vc, catalogue)
    assert len(found["error:ireb-anchor"]) == 2


# ---------------------------------------------------------------- folders, evals, graders

def test_assets_examples_and_evals_required_for_non_primitives(vc, catalogue):
    catalogue.skill("bare", folders=False, evals=False)
    catalogue.write("skills/specification/bare/references/ireb-anchor.md", "independent of IREB\n")
    catalogue.write("skills/specification/bare/assets/.gitkeep", "")
    catalogue.write("skills/specification/bare/examples/input.md", "x")
    found = codes(vc, catalogue)
    assert found["error:assets"] and found["error:examples"]
    assert len(found["error:evals"]) == 2


def test_primitives_need_no_assets_or_evals(vc, catalogue):
    catalogue.skill("re-ids", stage="_primitives", invocation="primitive")
    assert codes(vc, catalogue) == {}


def test_needs_an_adversarial_case(vc, catalogue):
    folder = catalogue.skill("no-adversarial")
    (folder / "evals" / "adversarial-vague").rename(folder / "evals" / "vague")
    found = codes(vc, catalogue)
    assert found["error:evals"] == ["evals/ needs a case folder starting with 'adversarial-'"]


def test_eval_case_rules(vc, catalogue, parser_mode):
    folder = catalogue.skill("case-skill")
    case = folder / "evals" / "happy-path"
    (case / "prompt.md").write_text("---\ntags: [x]\nmodel: opus\n---\n\nPrompt\n")
    (case / "case.yaml").write_text("schema_version: 1.1\nname: other\n")
    (case / "files").mkdir()
    (case / "files" / "notes.md").write_text("x")
    messy = folder / "evals" / "messy-notes"
    (messy / "prompt.md").write_text("no settings block\n")
    (messy / "graders" / "01-check.md").write_text("---\ntype: llm\n---\n\nstatement\n")
    (messy / "graders" / "02-weight.md").write_text("---\ntype: llm\nfocus: trace\nweight: heavy\n---\n\nx\n")
    found = codes(vc, catalogue)
    messages = " ".join(found["error:eval-case"])
    assert "'model' not allowed" in messages
    assert 'schema_version must be "1.1" (got 1.1) (quote it' in messages
    assert "name must equal the folder name 'happy-path'" in messages
    assert "expected_outcome is missing" in messages
    assert "place-files.sh is missing" in messages
    assert "context.scaffold_script must name place-files.sh" in messages
    assert "has no '---' settings block" in messages
    graders = " ".join(found["error:grader"])
    assert "missing focus, weight" in graders and "weight must be a number" in graders


def test_eval_case_with_files_and_scaffold(vc, catalogue):
    folder = catalogue.skill("scaffolded")
    case = folder / "evals" / "happy-path"
    (case / "files").mkdir()
    (case / "files" / "notes.md").write_text("x")
    script = case / "place-files.sh"
    script.write_text("#!/usr/bin/env bash\ncp -R files/. .\n")
    script.chmod(0o755)
    with open(case / "case.yaml", "a") as handle:
        handle.write("context:\n  scaffold_script: place-files.sh\n")
    assert codes(vc, catalogue) == {}
    if os.name == "posix":
        script.chmod(0o644)
        assert codes(vc, catalogue)["warning:eval-case"]


def test_case_without_graders(vc, catalogue):
    folder = catalogue.skill("no-graders")
    for grader in (folder / "evals" / "happy-path" / "graders").iterdir():
        grader.unlink()
    assert codes(vc, catalogue)["error:grader"]


# ---------------------------------------------------------------- catalogue-level checks

def test_handoffs_resolve(vc, catalogue):
    (catalogue.root / "docs" / "epics.md").write_text(
        "| `testability-check` (model) | brief |\n\n```\n    _primitives/     re-interview  re-templates\n```\n")
    catalogue.skill("requirement-phrasing", outputs_to="requirement-linter, testability-check, re-templates, made-up")
    catalogue.skill("requirement-linter", stage="validation")
    found = codes(vc, catalogue)
    assert [m for m in found["error:handoff"] if "'made-up'" in m]
    assert {m.split("'")[1] for m in found["warning:handoff"]} == {"testability-check", "re-templates"}
    strict = codes(vc, catalogue, strict_handoffs=True)
    assert len(strict["error:handoff"]) == 3


def test_none_is_not_a_skill(vc, catalogue):
    catalogue.skill("lonely", inputs_from="none", outputs_to="none")
    assert codes(vc, catalogue) == {}


def test_duplicate_names_across_stages(vc, catalogue):
    catalogue.skill("twin", stage="specification")
    catalogue.skill("twin", stage="validation")
    found = codes(vc, catalogue)
    assert any("also used by skills/specification/twin" in m for m in found["error:duplicate-name"])


def test_half_written_skills_do_not_crash(vc, catalogue, capsys, parser_mode):
    catalogue.write("skills/specification/only-front/SKILL.md", "---\nname: only-front\n---\n")
    catalogue.write("skills/specification/list-front/SKILL.md", "---\n- a\n- b\n---\n")
    catalogue.write("skills/specification/unclosed/SKILL.md", "---\nname: unclosed\n")
    (catalogue.root / "skills/specification/binary").mkdir(parents=True)
    (catalogue.root / "skills/specification/binary/SKILL.md").write_bytes(b"\xff\xfe\x00garbage")
    catalogue.write("skills/specification/no-meta/SKILL.md", "---\nname: no-meta\nmetadata: 3\n---\n# x\n")
    folder = catalogue.skill("odd-evals")
    (folder / "evals" / "happy-path" / "case.yaml").write_text("- just\n- a list\n")
    (folder / "evals" / "messy-notes" / "graders" / "01-check.md").write_text("no front\n")
    (folder / "evals" / "empty-case").mkdir()
    catalogue.write("skills/validation/no-skill-md-yet/references/notes.md", "x")
    assert run(vc, catalogue) == 1
    out = capsys.readouterr().out
    assert "internal" not in out
    assert "no-skill-md-yet" not in out
    assert run(vc, catalogue, "--warn-only") == 0


def test_skill_filter(vc, catalogue, capsys):
    catalogue.skill("good-one", outputs_to="bad-one")
    folder = catalogue.skill("bad-one")
    (folder / "references" / "ireb-anchor.md").unlink()
    assert run(vc, catalogue, "--skill", "good-one") == 0
    assert "1 skill(s) checked" in capsys.readouterr().out
    assert run(vc, catalogue, "--skill", "bad-one") == 1
    assert run(vc, catalogue, "--skill", "nobody") == 2


def test_missing_skills_folder_is_usage_error(vc, tmp_path):
    assert vc.main(["--root", str(tmp_path)]) == 2


# ---------------------------------------------------------------- generated docs

def test_write_and_check_docs(vc, catalogue, capsys):
    catalogue.skill("requirement-phrasing", outputs_to="requirement-linter")
    catalogue.skill("requirement-linter", stage="validation", inputs_from="requirement-phrasing, re-ids")
    catalogue.skill("re-setup", stage="foundations", invocation="user")
    catalogue.skill("re-ids", stage="_primitives", invocation="primitive", outputs_to="requirement-linter")
    assert run(vc, catalogue, "--check-docs") == 1
    assert run(vc, catalogue, "--write-docs") == 0
    assert run(vc, catalogue, "--check-docs") == 0
    catalogue_md = (catalogue.root / "docs" / "catalogue.md").read_text()
    pipeline_md = (catalogue.root / "docs" / "pipeline.md").read_text()
    assert catalogue_md.startswith(vc.GENERATED_NOTE)
    assert ("| Specification | [`requirement-phrasing`](../skills/specification/requirement-phrasing/SKILL.md) | "
            "model | P1 | Does one thing and leaves requirements/x.md behind. | `requirements/x.md` | "
            "CPRE FL Handbook 1.2 §3.3 |") in catalogue_md
    rows = [line for line in catalogue_md.splitlines() if line.startswith("| ") and "](../skills/" in line]
    assert [r.split("|")[1].strip() for r in rows] == ["Foundations", "Specification", "Validation", "Primitives"]
    assert "```mermaid\nflowchart LR" in pipeline_md
    assert '  subgraph stage_specification["Specification"]' in pipeline_md
    assert '    re_setup(["re-setup"])' in pipeline_md
    assert "  requirement_phrasing --> requirement_linter" in pipeline_md
    assert "  re_ids --> requirement_linter" in pipeline_md
    assert pipeline_md.count("requirement_phrasing --> requirement_linter") == 1  # deduplicated
    folder = catalogue.root / "skills/specification/requirement-phrasing/SKILL.md"
    folder.write_text(folder.read_text().replace("priority: P1", "priority: P0"))
    capsys.readouterr()
    assert run(vc, catalogue, "--check-docs") == 1
    assert "stale generated docs: docs/catalogue.md" in capsys.readouterr().out


def test_first_sentence(vc):
    assert vc._first_sentence("Rewrites things (e.g. EARS). Use when x.") == "Rewrites things (e.g. EARS)."
    assert vc._first_sentence("One line only") == "One line only"
    assert vc._first_sentence("Uses v1.2 rules. Then more.") == "Uses v1.2 rules."


# ---------------------------------------------------------------- built-in YAML parser

YAML_SAMPLES = [
    "name: x\ndescription: >-\n  Folded text\n  over lines.\n\n  New paragraph.\nlicense: MIT\n",
    "a: |\n  keep\n    indent\n  lines\nb: |-\n  strip\nc: |+\n  keep trailing\n\nd: last\n",
    "flag: true\nother: False\nyes_word: yes\nnum: 30\nfloat: 1.1\nver: 0.1.0\nnull_v: ~\nempty:\n",
    'quoted: "a \\"b\\" \\u00e9 # not a comment"\nsingle: \'it\'\'s\'\nplain: x # comment\n',
    "metadata:\n  stage: specification\n  nested:\n    deep: 1\n  after: 2\ntop: 3\n",
    "tags: [re-skills, \"two words\", 3]\nempty_list: []\nmap: {a: 1, b: two}\n",
    "items:\n  - one\n  - two: 2\n    three: 3\n  -\n    four: 4\nseq_same_indent:\n- a\n- b\n",
    "description: A plain scalar\n  that continues\n  on more lines.\nnext: x\n",
    'description: "A quoted scalar\n  that continues"\nnext: y\n',
    "context:\n  scaffold_script: place-files.sh\nexpected_outcome: |\n  Line one.\n  Line two.\n",
    "# comment first\n\nkey: value\n# trailing comment\n",
    "url: https://example.com/a#frag\nanchor: \"CPRE FL Handbook 1.2 §3.3.1, §3.2\"\n",
]


@pytest.mark.parametrize("sample", YAML_SAMPLES)
def test_mini_yaml_matches_pyyaml(vc, sample):
    yaml = pytest.importorskip("yaml")
    assert vc.mini_yaml_load(sample) == yaml.safe_load(sample)


def test_mini_yaml_without_pyyaml_values(vc):
    data = vc.mini_yaml_load(YAML_SAMPLES[0])
    assert data == {"name": "x", "description": "Folded text over lines.\nNew paragraph.", "license": "MIT"}
    data = vc.mini_yaml_load(YAML_SAMPLES[2])
    assert data["flag"] is True and data["other"] is False and data["num"] == 30
    assert data["float"] == 1.1 and data["ver"] == "0.1.0" and data["null_v"] is None


@pytest.mark.parametrize("bad", [
    "name: [unclosed\n",
    "a: 1\n  b: 2\n",
    "a: 1\na: 2\n",
    "a: \"open\n",
    "\tkey: tab\n",
    "just text without colon\nsecond: x\n",
    "a: &anchor x\n",
    "description: Rewrites text: one per line\n",
    "description: first line\n  second: line\n",
])
def test_mini_yaml_errors(vc, bad):
    with pytest.raises(vc.YamlError):
        vc.mini_yaml_load(bad)


def _repo_yaml_documents():
    docs = []
    for path in sorted((REPO_ROOT / "skills").rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        if path.name in ("SKILL.md", "prompt.md") or path.parent.name == "graders":
            text = path.read_text(encoding="utf-8", errors="replace")
            if text.startswith("---\n") and "\n---" in text[3:]:
                docs.append((path, text[4: text.index("\n---", 3)]))
        elif path.name == "case.yaml":
            docs.append((path, path.read_text(encoding="utf-8", errors="replace")))
    return docs


def test_mini_yaml_parity_on_the_real_catalogue(vc):
    yaml = pytest.importorskip("yaml")
    mismatches = []
    for path, text in _repo_yaml_documents():
        try:
            expected = yaml.safe_load(text)
        except yaml.YAMLError:
            continue
        try:
            actual = vc.mini_yaml_load(text)
        except vc.YamlError as exc:
            mismatches.append(f"{path}: {exc}")
            continue
        if actual != expected:
            mismatches.append(str(path))
    assert not mismatches, mismatches


def test_real_catalogue_validates_without_crashing(vc, capsys):
    skills = vc.validate(REPO_ROOT)
    assert not [f for s in skills for f in s.findings if f.code == "internal"]
    assert vc.main(["--warn-only", "-q"]) == 0
