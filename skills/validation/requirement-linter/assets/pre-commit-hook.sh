#!/bin/sh
# re-skills requirement lint as a git pre-commit hook.
#
# Install, from the repo root:
#   cp <skill-dir>/assets/pre-commit-hook.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#
# Runs only when the commit touches the requirements workspace. Blocks the commit when the linter
# exits 1 (findings at or above RE_LINT_FAIL_ON) or 2 (usage, schema or parse error).
# It lints the files as they are in the working tree, so stage everything you want checked.
# Skip once with: git commit --no-verify
#
# Settings (environment variables):
#   RE_WORKSPACE     workspace folder (default: requirements)
#   RE_LINT_FAIL_ON  error | warning | info (default: error)
#   RE_LINT_SCRIPT   path to a vendored lint_requirements.py; used when re-lint is not installed.
#                    Without it the hook looks in the usual skill folders of each agent.

set -u

workspace="${RE_WORKSPACE:-requirements}"
fail_on="${RE_LINT_FAIL_ON:-error}"

if ! git diff --cached --name-only --diff-filter=ACMR -- "$workspace" | grep -q .; then
  exit 0
fi

script="${RE_LINT_SCRIPT:-}"
if [ -z "$script" ]; then
  for dir in .claude/skills .agents/skills .github/skills .cursor/skills; do
    if [ -f "$dir/requirement-linter/scripts/lint_requirements.py" ]; then
      script="$dir/requirement-linter/scripts/lint_requirements.py"
      break
    fi
  done
fi

if command -v re-lint >/dev/null 2>&1; then
  re-lint check --fail-on "$fail_on"
  status=$?
elif [ -n "$script" ] && [ -f "$script" ]; then
  python3 "$script" --fail-on "$fail_on"
  status=$?
else
  echo "pre-commit: re-lint not found, requirement lint skipped." >&2
  echo "  Install: pip install \"git+https://github.com/renzrollon/hairspring@v0.1.0#subdirectory=packages/re-lint\"" >&2
  echo "  or set RE_LINT_SCRIPT to the requirement-linter skill's scripts/lint_requirements.py" >&2
  exit 0
fi

if [ "$status" -ne 0 ]; then
  echo "pre-commit: requirement lint failed (exit $status). Fix the findings above, or commit with --no-verify." >&2
fi
exit "$status"
