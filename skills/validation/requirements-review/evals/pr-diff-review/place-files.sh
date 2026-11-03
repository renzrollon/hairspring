#!/usr/bin/env bash
# Builds a small git history: the base register is committed, the PR's changes stay uncommitted.
set -eu
here="$(cd "$(dirname "$0")" && pwd)"
cp -R "$here/files/base/." .
git init -q .
git add requirements
git -c user.name=eval -c user.email=eval@example.invalid commit -q -m "base: agreed requirements"
cp -R "$here/files/change/." .
