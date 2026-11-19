# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/). Changes are collected as changesets in `.changeset/` and folded into this file on release.

## [Unreleased]

## [0.1.0] - 2026-11-03

### Added

- 35 skills across the eight RE stages (12 P0, 15 P1, 8 P2) plus three shared primitives (`re-interview`, `re-ids`, `re-templates`).
- `re-lint`: stdlib-only Python package and CLI for requirement linting, ID allocation, trace coverage, baselines, views, prioritization, ReqIF, OpenSpec and issue-tracker sync.
- Composite GitHub Action (`action.yml`) for linting requirements on pull requests.
- Claude Code plugin and marketplace manifests; installer for Claude Code, Codex, Copilot and Cursor.
- `examples/loyalty-points`: the sample project with one full RE loop.
