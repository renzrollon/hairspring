# Evals

Each skill keeps its eval cases next to it, in `skills/<stage>/<skill>/evals/<case-name>/` (see [ADR 0006](../docs/adr/0006-evals-live-with-each-skill.md)). The format is the skill-creator case-folder format, so `claude plugin eval` can run it directly.

```text
skills/<stage>/<skill>/evals/<case-name>/
  prompt.md          settings block, then the prompt as a user would type it
  case.yaml          schema_version "1.1", name, expected_outcome, optional context.scaffold_script
  graders/NN-*.md    one verifiable statement per file (type: llm, focus: trace, weight: 1)
  files/             optional input files, copied into the run folder by place-files.sh
  place-files.sh     present whenever files/ exists
```

## What CI checks

`python3 tools/validate_catalogue.py` checks the **structure** on every PR: at least three cases per skill, at least one whose name starts with `adversarial-`, a valid settings block, a valid `case.yaml`, at least one grader per case, and a scaffold script whenever a case has input files. It does not run models.

## Running the evals (real, billed model runs)

With Claude Code 2.1.269 or later, from a skill folder:

```bash
cd skills/specification/requirement-phrasing
claude plugin eval . --allow-tools Write,Edit,Bash --scaffold
```

To run every P0 skill:

```bash
python3 tools/list_skills.py --priority P0 --paths | while read -r dir; do
  (cd "$dir" && claude plugin eval . --allow-tools Write,Edit,Bash --scaffold)
done
```

Results land in each skill's `evals/results/` (git-ignored). Without the CLI, the `skill-creator` skill can run the same cases: ask it to "run the evals for `<skill>`".

## Release gate

The v1 gate in `docs/epics.md` is: evals green on two agents. Record each release run in `docs/eval-runs.md` with the agent, model, date, pass rate per skill, and the commit.

## Writing a good case

- **Happy path:** the input the skill is designed for, on the loyalty-points sample.
- **Messy input:** a real-looking transcript, ticket dump or legacy file with noise.
- **Adversarial (`adversarial-*`):** vague wording, contradictions, a design decision posing as a requirement, or a request to skip a safety step. The skill passes when it refuses to invent, flags the problem, or routes to the right neighbor.
- Graders state observable facts ("`requirements/conflicts.md` contains a row typed `subject matter` for R-022 and R-035"), never opinions ("the output is good").
