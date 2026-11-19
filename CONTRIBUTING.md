# Contributing

Thanks for helping. `re-skills` is meant to be used by teams with no requirements engineer, so every contribution is judged by one question: *can an engineer with no RE training run this in under ten minutes and get a file a reviewer can read?*

## Quick start

```bash
git clone https://github.com/renzrollon/hairspring && cd hairspring
python3 -m pip install -e "packages/re-lint[dev]"
python3 -m pytest -q packages/re-lint/tests tests
python3 tools/vendor_scripts.py --check --strict
python3 tools/validate_catalogue.py
```

## Changing or adding a skill

1. Read [`docs/authoring-guide.md`](docs/authoring-guide.md). It is the contract; the PR checklist is at its end.
2. Copy the structure of [`skills/specification/requirement-phrasing/`](skills/specification/requirement-phrasing/), the reference implementation.
3. Keep scripts in `packages/re-lint` if more than one skill or CI needs them, then run `python3 tools/vendor_scripts.py`. Never edit a file that starts with `VENDORED from`.
4. Run `python3 tools/validate_catalogue.py --skill <name>` and `python3 tools/validate_catalogue.py --write-docs` (regenerates `docs/catalogue.md` and `docs/pipeline.md`).
5. Add a changeset in `.changeset/` (see its README).
6. Check [`SCOPE.md`](SCOPE.md) before proposing a new skill.

## Changing `re-lint`

- Stdlib only, Python 3.9+. Rule IDs are stable: never rename one; deprecate and add a new one instead.
- Precision over recall for `error` rules: a red CI must be worth fixing. New heuristics start as `warning` or `info`.
- Every rule needs a positive and a negative test.

## Copyright rules (non-negotiable)

- Do not paste or closely paraphrase IREB handbook, syllabus or glossary text. Cite section numbers and term names.
- Do not paste ISO text. Cite clause titles.
- Do not embed Volere templates. EARS may be shown with attribution to Mavin et al.

## Commit messages

Conventional Commits (`feat(skills/glossary): ...`, `fix(re-lint): ...`, `docs: ...`). Cite requirement IDs when a change implements one of this repo's own requirements.
