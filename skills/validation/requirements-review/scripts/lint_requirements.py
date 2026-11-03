#!/usr/bin/env python3
# VENDORED from packages/re-lint/src/re_lint/lint.py by tools/vendor_scripts.py; do not edit.
# Change the package module, then run `python3 tools/vendor_scripts.py` to refresh this copy.
"""Lint requirement text and attributes: ``re-lint check`` (vendored as ``lint_requirements.py``).

Checks every row of the requirement register (``requirements/requirements.csv`` by default, plus
Markdown tables under the workspace whose ``ID`` column holds requirement IDs) for natural-language
pitfalls (weak words, passive voice, incomplete EARS conditions, ...) and structural problems
(duplicate or malformed IDs, empty required attributes, values outside the schema enums).

Stdlib only, Python 3.9+. Exit codes: 0 clean, 1 findings at or above ``--fail-on``,
2 usage, schema or parse error. Edit this file only in ``packages/re-lint``; skills carry a
vendored copy produced by ``tools/vendor_scripts.py``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

if not __package__:  # run as a script: make the sibling reqio.py importable from any cwd
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:  # inside the package
    from . import reqio
except ImportError:  # vendored next to reqio.py in a skill's scripts/
    import reqio

VERSION = getattr(reqio, "__version__", "0.1.0")
INFO_URI = "https://github.com/renzrollon/hairspring/tree/main/packages/re-lint"

SEVERITIES = ("info", "warning", "error")
SEVERITY_RANK = {"info": 1, "warning": 2, "error": 3}

# --------------------------------------------------------------------------- rule registry


@dataclass(frozen=True)
class Rule:
    """One lint rule. IDs are stable: never rename one."""

    id: str
    severity: str
    kind: str  # "text" (runs on Text) or "structure" (IDs, attributes, registers)
    summary: str
    example: str
    hint: str


_RULE_LIST = (
    Rule("weak-word", "error", "text",
         "Vague qualifiers with no measurable meaning",
         "`quickly`, `user-friendly`, `appropriate`, `fast`, `easy`, `flexible`, `robust`, "
         "`efficient`, `as soon as possible`, `etc.`, `and/or`, `if possible`, `some`, `various`",
         "Replace with a measurable criterion or a reference to a defined term"),
    Rule("universal-quantifier", "warning", "text",
         "Absolute claims that are rarely true and hard to verify",
         "`all`, `every`, `always`, `never`, `none`, `each and every`, `any` (as \"every\"), "
         "`no one`, `nothing`, `everything`",
         "Bound the scope or name the exceptions"),
    Rule("passive-voice", "warning", "text",
         "Passive construction with no actor",
         "`is validated`, `shall be stored`, `are notified` without `by <actor>`",
         "Name the actor: `the system shall validate`"),
    Rule("nominalization", "info", "text",
         "Process words hiding who does what",
         "`validation of`, `processing`, `management of`, `handling of`, `the creation of`",
         "Use the verb with an actor"),
    Rule("incomplete-condition", "error", "text",
         "A condition with no consequence, `IF` without `THEN` in unwanted-behavior form, or "
         "`WHEN`/`WHILE`/`WHERE`/`IF` with no `shall`/`should`/`may`",
         "`WHEN the user logs in, the balance`",
         "Complete the EARS pattern"),
    Rule("missing-obligation", "error", "text",
         "No `shall`/`should`/`may`/`must` and not a user story (`As a ..., I want ...`)",
         "`The system displays the balance`",
         "Add the obligation verb that matches the binding level"),
    Rule("future-tense", "warning", "text",
         "`will` used as the obligation verb",
         "`The system will log every refund`",
         "`will` states a fact; use `shall` if it is required"),
    Rule("compound-requirement", "warning", "text",
         "More than one obligation verb, or `and`/`or` joining two actions under one `shall`",
         "`shall export the file and email the user`",
         "Split into one requirement per sentence"),
    Rule("open-tbd", "info", "text",
         "`TBD`, `TBC`, `??`, `XXX` in text or attributes",
         "`within TBD ms`",
         "Resolve the open question; keep the ID"),
    Rule("duplicate-id", "error", "structure",
         "Same ID twice in one register (or across registers in the same run)",
         "two `R-012` rows",
         "Allocate a new ID with `re-lint ids next`"),
    Rule("invalid-id", "error", "structure",
         "ID not matching the schema pattern",
         "`REQ12`",
         "Use the schema prefix and digits"),
    Rule("missing-attribute", "error", "structure",
         "A required attribute empty (`schema.attributes.required`)",
         "empty `Source`",
         "Fill it; unknown values are `TBD` with an open question"),
    Rule("invalid-enum", "error", "structure",
         "Attribute value outside `schema.attributes.enums`",
         "`Type=NFR`, `Priority=high`",
         "Use an allowed value"),
    Rule("unregistered-source", "warning", "structure",
         "`Source` cites an `S-`/`SH-`/`I-` ID not found in the workspace (only when "
         "`sources.csv` / `stakeholders.md` exist)",
         "`S-19` not in `sources.csv`",
         "Register the source with `source-inventory`"),
    Rule("register-drift", "warning", "structure",
         "A detail register echoes requirement text that differs from `requirements.csv`",
         "`verification.csv` text for R-012 is stale",
         "Copy the current text or drop the echo"),
)

RULES: Dict[str, Rule] = {rule.id: rule for rule in _RULE_LIST}
TEXT_RULES = tuple(r.id for r in _RULE_LIST if r.kind == "text")
STRUCTURE_RULES = tuple(r.id for r in _RULE_LIST if r.kind == "structure")

# --------------------------------------------------------------------------- word lists

WEAK_WORDS = (
    "quickly", "quick", "fast", "user-friendly", "user friendly", "easy to use", "easy", "easily",
    "appropriate", "appropriately", "as appropriate", "flexible", "robust", "efficient",
    "efficiently", "adequate", "adequately", "as soon as possible", "asap", "etc.", "etc", "and/or",
    "if possible", "where possible", "normally", "sufficient", "sufficiently", "state-of-the-art",
    "state of the art", "seamless", "seamlessly", "intuitive", "intuitively", "minimal", "optimal",
    "optimally", "reasonable", "reasonably", "several", "some", "various", "approximately",
    "in a timely manner", "timely",
)

UNIVERSAL_WORDS = (
    "each and every", "all", "every", "always", "never", "none", "no one", "nobody", "nothing",
    "everything", "everyone", "everybody",
)

NOMINALIZATIONS = (
    "validation", "verification", "creation", "deletion", "calculation", "computation",
    "management", "handling", "generation", "modification", "registration", "cancellation",
    "submission", "execution", "initialization", "implementation", "transmission", "conversion",
    "transformation", "synchronization", "aggregation", "evaluation", "authorization",
    "authentication", "approval", "processing", "retrieval", "storage", "removal", "activation",
    "deactivation", "allocation", "completion", "extraction", "migration", "reconciliation",
    "installation",
)

# Common irregular past participles (regular ones end in -ed; see _is_participle).
IRREGULAR_PARTICIPLES = frozenset("""
    arisen awoken beaten begun bent bitten bled blown broken brought built burnt bought caught
    chosen cut dealt done drawn driven eaten fallen fed felt fought found flown forbidden
    forgotten forgiven frozen gotten given grown hung heard hidden held hurt kept known laid led
    left lent lost made meant met mistaken overridden overwritten paid proven put read rebuilt
    redone rerun reset rewritten ridden risen run said seen sought sold sent set shaken shot shown
    shut slid spoken spent split spread stolen struck sworn swept taken taught torn told thought
    thrown understood undertaken undone withdrawn withheld woken worn written won
""".split())

# -ed / -en words that are not participles, or participles used as plain adjectives of state.
NOT_PARTICIPLES = frozenset("""
    bed bleed breed embed exceed feed greed heed hundred indeed need proceed red reed seed shed
    speed succeed weed sacred naked wicked kindred rugged beloved
    based located situated supposed concerned involved interested connected disconnected enabled
    disabled expired logged signed married tired pleased unchanged unaffected detailed advanced
    experienced skilled qualified
    open often even token screen green seven eleven ten between when then listen happen kitchen
    garden citizen golden wooden sudden dozen oxygen specimen linen burden warden chicken children
    women men queen keen teen heaven eighteen fifteen sixteen seventeen thirteen fourteen nineteen
""".split())

# Base-form verbs that, after "and"/"or" and before a determiner, signal a second action.
ACTION_VERBS = frozenset("""
    accept add alert allow apply approve archive ask assign attach audit authenticate authorize
    award block calculate cancel capture change charge check close compute configure confirm
    convert create credit debit decline decrypt delete deliver deny detect disable dispatch
    display download edit email emit enable encrypt escalate export fetch filter flag forward
    generate grant hide import inform insert invite issue load lock log mark mask merge message
    modify monitor notify open pause post print prompt publish purge queue raise read redeem
    redirect refund register reject reload remove rename renew replace report request reset
    restart restore resume retain retrieve retry return reverse revoke route save scan schedule
    send set show sign sort start stop store submit suspend sync synchronize text track transfer
    trigger unlock update upload validate verify warn write
""".split())

DETERMINERS = r"(?:the|a|an|its|their|his|her|each|all|any|every|this|that|these|those|it|them|him|us|me|both|no|one|our|your|my)"

_OBLIGATION = re.compile(r"\b(shall|should|must|may)\b", re.I)
_WILL = re.compile(r"\b(will|won['’]t)\b", re.I)
_CAN = re.compile(r"\bcan(?:not)?\b", re.I)
_COND_START = re.compile(r"^\s*(WHERE|WHILE|WHEN|IF)\b", re.I)
_SUBORDINATE_START = re.compile(
    r"^\s*(?:once|after|before|until|unless|whenever|upon|as\s+soon\s+as|as\s+long\s+as|"
    r"in\s+case|provided\s+that)\b", re.I)
_THEN = re.compile(r"\bTHEN\b", re.I)
_MID_IF = re.compile(r",\s*IF\b")  # an upper-case IF clause inside a complex requirement
_STORY = re.compile(
    r"^\W*(?:in\s+order\s+to\b[^,]*,\s*)?as\s+(?:an?\s+|the\s+)?[^,]{1,80}?,?\s+(?:I|we)\s+"
    r"(?:want|need|would\s+like|wish|expect)\b", re.I)
_TBD = re.compile(r"(?<![A-Za-z0-9])(TBD|TBC|XXX)(?![A-Za-z0-9])|\?\?+", re.I)
_TBD_ONLY = re.compile(r"^\s*(?:TBD|TBC|XXX|\?\?+)\s*\.?\s*$", re.I)
_QUOTED = re.compile(
    r"`[^`]*`|\"[^\"]*\"|“[^”]*”|‘[^’]*’|(?<![\w])'[^'\n]*'(?![\w])")
_SENTENCE_END = re.compile(r"[.;!?](?=\s|$)")
_BE = r"(?:is|are|was|were|be|been|being)"
_ADVERB = (r"(?:\w+ly|not|then|also|only|always|never|first|still|again|now|often|either|"
           r"automatically|immediately)")
_PASSIVE = re.compile(rf"\b{_BE}\s+(?:being\s+)?(?:{_ADVERB}\s+){{0,2}}([a-z]+)\b", re.I)
_PLACEHOLDER_PASSIVE = re.compile(
    r"\bto\s+be\s+(?:confirmed|defined|determined|decided|agreed|clarified|specified|announced)\b",
    re.I)
_RELATIVE_BEFORE = re.compile(r"\b(?:that|which|who)\s+(?:has\s+|have\s+|had\s+)?$", re.I)
_CONDITIONAL_WORDS = re.compile(
    r"\b(?:when|whenever|while|if|whether|once|after|before|until|unless|where|upon)\b", re.I)
_BY_ACTOR = re.compile(r"\bby\s+(?:the\s+|a\s+|an\s+|its\s+|their\s+)?([A-Za-z][\w-]*)", re.I)
_NOT_ACTORS = frozenset("""
    email e-mail sms text phone post mail default hand means way end midnight noon then now date
    time percent far chance design itself themselves cash card
""".split())
_EVERY_INTERVAL = re.compile(
    r"\s+(?:\d+(?:[.,]\d+)?\s*|other\s+|single\s+)?(?:time|second|minute|hour|day|night|week|"
    r"fortnight|month|quarter|year|morning|evening|weekday|weekend|business\s+day|working\s+day|"
    r"monday|tuesday|wednesday|thursday|friday|saturday|sunday|cycle|interval|run|batch|ms|s|"
    r"min|h)s?\b", re.I)
_MONTH_MAY = re.compile(r"\bMay\s+\d|\d\s+May\b")
# Skipped by the default workspace scan: generated outputs, and historical records (decisions,
# change requests, reviews) whose echoed text is meant to differ from the current register.
_GENERATED_DIRS = ("trace", "views", "baselines", "exports", "changes", "decisions", "reviews")


def _phrase_regex(phrases: Iterable[str]) -> Optional["re.Pattern[str]"]:
    items = sorted({p.strip().lower() for p in phrases if p and p.strip()}, key=len, reverse=True)
    if not items:
        return None
    alternatives = "|".join(r"\s+".join(re.escape(tok) for tok in item.split()) for item in items)
    return re.compile(rf"(?<![\w-])(?:{alternatives})(?![\w-])", re.I)


_NOMINALIZATION_RE = re.compile(
    rf"(?<![\w-])(?:the\s+)?(?:{'|'.join(NOMINALIZATIONS)})\s+of\b|(?<![\w-])processing(?![\w-])",
    re.I)
# "processing" used as a verb (``stops processing``, ``is processing``) is not a nominalization.
_PROCESSING_AS_VERB = re.compile(
    r"\b(?:is|are|was|were|be|been|start|starts|stop|stops|resume|resumes|continue|continues|"
    r"finish|finishes|begin|begins|keep|keeps|while|after|before|without|when)\s+$", re.I)
_UNIVERSAL_RE = _phrase_regex(UNIVERSAL_WORDS)
_ANY_RE = re.compile(r"(?<![\w-])any(?![\w-])", re.I)
_COMPOUND_VERB_RE = re.compile(
    rf"\b(and|or)\s+(?:then\s+|also\s+)?([a-z]+)\s+{DETERMINERS}\b", re.I)

# --------------------------------------------------------------------------- findings


@dataclass
class Finding:
    rule: str
    severity: str
    id: str
    file: str
    line: int
    column: Optional[int]
    match: str
    message: str
    hint: str
    # (file, first line, last line) of every row this finding is about; used by --changed-only.
    related: List[Tuple[str, int, int]] = field(default_factory=list, repr=False, compare=False)
    scope: str = "row"  # "row", or "file" for header-level findings

    def to_dict(self) -> Dict:
        return {
            "rule": self.rule, "severity": self.severity, "id": self.id, "file": self.file,
            "line": self.line, "column": self.column, "match": self.match,
            "message": self.message, "hint": self.hint,
        }


@dataclass
class Config:
    severity: Dict[str, str]
    enabled: Set[str]
    weak_re: Optional["re.Pattern[str]"]
    allow_re: Optional["re.Pattern[str]"]


class UsageError(Exception):
    """Bad command-line usage or configuration (exit code 2)."""


# --------------------------------------------------------------------------- text analysis


def mask_quoted(text: str) -> str:
    """Blank out quoted and backticked spans (same length) so they are not linted as prose."""
    return _QUOTED.sub(lambda m: " " * len(m.group(0)), text)


def is_story(text: str) -> bool:
    """True for user-story form: ``As a <role>, I want <goal> ...``."""
    return bool(_STORY.match(text or ""))


@dataclass
class Structure:
    keyword: Optional[str] = None  # leading EARS keyword as written (WHEN, If, ...)
    response_start: int = 0  # offset where the response clause starts
    if_without_then: bool = False
    has_response: bool = True


def _is_obligation(text: str, match: "re.Match[str]") -> bool:
    """Exclude epistemic ``may`` (``that may expire``) and the month ``May``."""
    if match.group(1).lower() != "may":
        return True
    before = text[: match.start()]
    if re.search(r"\b(?:that|which|who|it|they|there|this|these|those)\s+$", before, re.I):
        return False
    window = text[max(0, match.start() - 3): match.end() + 3]
    if match.group(1) == "May" and _MONTH_MAY.search(window):
        return False
    return True


def obligations(text: str) -> List["re.Match[str]"]:
    return [m for m in _OBLIGATION.finditer(text) if _is_obligation(text, m)]


def analyze_structure(masked: str) -> Structure:
    """Split an EARS-style sentence into its condition and response regions."""
    s = Structure()
    lead = _COND_START.match(masked)
    sub = None if lead else _SUBORDINATE_START.match(masked)
    if not lead and not sub:
        return s
    start = (lead or sub).end()  # type: ignore[union-attr]
    if lead:
        s.keyword = lead.group(1)
    found_then = False
    if lead and lead.group(1).upper() == "IF":
        then = _THEN.search(masked, start)
        if then:
            s.response_start, found_then = then.end(), True
        elif lead.group(1) == "IF":
            s.if_without_then = True
    if not found_then:
        mid_if = _MID_IF.search(masked, start)
        if mid_if:
            then = _THEN.search(masked, mid_if.end())
            if then:
                s.response_start, found_then = then.end(), True
            else:
                s.if_without_then = True
    if not found_then:
        first = next((m for m in obligations(masked) if m.start() >= start), None)
        if first is not None:
            comma = masked.rfind(",", start, first.start())
            s.response_start = comma + 1 if comma >= 0 else first.start()
        else:
            comma = masked.rfind(",", start)
            s.response_start = comma + 1 if comma >= 0 else len(masked)
    s.has_response = any(m.start() >= s.response_start for m in obligations(masked))
    return s


def _is_participle(word: str) -> bool:
    w = word.lower()
    if w in NOT_PARTICIPLES or w.endswith("teen"):
        return False
    if w in IRREGULAR_PARTICIPLES:
        return True
    if w.endswith("ed") and len(w) >= 4:
        return True
    return w.endswith("en") and len(w) >= 5


def _sentence_end(text: str, pos: int) -> int:
    m = _SENTENCE_END.search(text, pos)
    return m.start() if m else len(text)


def _in_conditional_clause(text: str, start: int, floor: int) -> bool:
    """True when ``start`` sits in a subordinate clause (``... when the purchase is completed``)."""
    segment = text[floor:start]
    cut = max(segment.rfind(","), segment.rfind(";"))
    for m in _OBLIGATION.finditer(segment):
        cut = max(cut, m.end())
    return bool(_CONDITIONAL_WORDS.search(segment[cut + 1 if cut >= 0 else 0:]))


def find_passives(masked: str, region_start: int = 0) -> List[Tuple[int, str]]:
    out: List[Tuple[int, str]] = []
    placeholders = [(m.start(), m.end()) for m in _PLACEHOLDER_PASSIVE.finditer(masked)]
    for m in _PASSIVE.finditer(masked, region_start):
        if not _is_participle(m.group(1)):
            continue
        if any(a <= m.start() < b for a, b in placeholders):  # "to be confirmed" is a TBD
            continue
        before = masked[: m.start()]
        if _RELATIVE_BEFORE.search(before):
            continue
        if _in_conditional_clause(masked, m.start(), region_start):
            continue
        end = _sentence_end(masked, m.end())
        actor = None
        for by in _BY_ACTOR.finditer(masked, m.end(), end):
            word = by.group(1).lower()
            if word not in _NOT_ACTORS and not word[0].isdigit():
                actor = by
                break
        if actor:
            continue
        out.append((m.start(), re.sub(r"\s+", " ", m.group(0))))
    return out


def find_universals(masked: str, region_start: int) -> List[Tuple[int, str]]:
    out: List[Tuple[int, str]] = []
    region = masked[region_start:]
    if _UNIVERSAL_RE is not None:
        for m in _UNIVERSAL_RE.finditer(region):
            word = m.group(0).lower()
            if word == "every" and _EVERY_INTERVAL.match(region, m.end()):
                continue
            if word == "all" and re.search(r"\b(?:at|after)\s+$", region[: m.start()], re.I):
                continue
            out.append((region_start + m.start(), re.sub(r"\s+", " ", m.group(0))))
    for m in _ANY_RE.finditer(region):
        before = region[: m.start()]
        after = region[m.end():]
        if re.match(r"\s+(?:more|longer)\b", after, re.I):
            continue
        if re.search(r"\b(?:if|whether|when|without|not|than|hardly|no)\s+$", before, re.I):
            continue
        prev = before.rstrip()
        universal = (
            not prev
            or prev[-1] in ".;:,"
            or re.search(r"\b(?:for|at|under|in)$", prev, re.I)
            or re.search(r"\b(?:shall|should|must|may)\s+(?:not\s+)?(?:be\s+able\s+to\s+)?[a-z]+$",
                         prev, re.I)
        )
        if universal:
            out.append((region_start + m.start(), m.group(0)))
    return out


def find_compound(masked: str, region_start: int) -> Optional[Tuple[int, str, str]]:
    """Return (offset, match, message) when the text holds more than one requirement."""
    obs = [m for m in obligations(masked) if m.start() >= region_start]
    if len(obs) >= 2:
        verbs = ", ".join(m.group(1).lower() for m in obs)
        return obs[1].start(), obs[1].group(1), f"{len(obs)} obligation verbs ({verbs}) in one requirement"
    if len(obs) != 1:
        return None
    ob = obs[0]
    end = _sentence_end(masked, ob.end())
    for m in _COMPOUND_VERB_RE.finditer(masked, ob.end(), end):
        verb = m.group(2).lower()
        if verb not in ACTION_VERBS:
            continue
        between = masked[ob.end(): m.start()]
        if re.search(r"\b(?:when|whenever|while|if|once|after|before|until|unless|where|that|which|"
                     r"who|whose|whom)\b", between, re.I):
            continue
        first_verb = re.match(r"\s+(?:not\s+)?(?:be\s+able\s+to\s+)?([a-z]+)", masked[ob.end():], re.I)
        first = first_verb.group(1).lower() if first_verb else ob.group(1).lower()
        return (m.start(), m.group(0),
                f'"{m.group(1).lower()}" joins two actions under one {ob.group(1).lower()} '
                f'("{first} ... {m.group(1).lower()} {verb}")')
    return None


def _spans(regex: Optional["re.Pattern[str]"], text: str) -> List[Tuple[int, int]]:
    return [(m.start(), m.end()) for m in regex.finditer(text)] if regex else []


def _allowed(pos: int, length: int, spans: Sequence[Tuple[int, int]]) -> bool:
    return any(a <= pos and pos + length <= b for a, b in spans)


def check_text(text: str, config: Config) -> List[Tuple[str, int, str, str]]:
    """Run the text rules on one requirement text.

    Returns ``(rule, offset, match, message)`` tuples; the caller turns them into findings.
    """
    out: List[Tuple[str, int, str, str]] = []
    on = config.enabled
    raw = text or ""
    if not raw.strip():
        return out
    tbd_seen: Set[str] = set()
    if "open-tbd" in on:
        for m in _TBD.finditer(raw):
            token = m.group(0).upper()
            if token not in tbd_seen:
                tbd_seen.add(token)
                out.append(("open-tbd", m.start(), m.group(0), f'open placeholder "{m.group(0)}" in Text'))
    if _TBD_ONLY.match(raw):
        return out
    masked = mask_quoted(raw)
    allow = _spans(config.allow_re, raw)
    story = is_story(raw)
    structure = analyze_structure(masked)
    region = structure.response_start

    if "weak-word" in on and config.weak_re is not None:
        seen: Set[str] = set()
        for m in config.weak_re.finditer(masked):
            word = re.sub(r"\s+", " ", m.group(0).lower())
            if word in seen or _allowed(m.start(), len(m.group(0)), allow):
                continue
            seen.add(word)
            out.append(("weak-word", m.start(), m.group(0),
                        f'weak word "{m.group(0)}" has no measurable meaning'))

    if "universal-quantifier" in on:
        seen = set()
        for pos, word in find_universals(masked, region):
            key = word.lower()
            if key in seen or _allowed(pos, len(word), allow):
                continue
            seen.add(key)
            out.append(("universal-quantifier", pos, word,
                        f'universal quantifier "{word}" makes an absolute claim'))

    if "passive-voice" in on and not story:
        seen = set()
        for pos, phrase in find_passives(masked, region):
            if phrase.lower() in seen:
                continue
            seen.add(phrase.lower())
            out.append(("passive-voice", pos, phrase, f'passive voice "{phrase}" names no actor'))

    if "nominalization" in on:
        seen = set()
        for m in _NOMINALIZATION_RE.finditer(masked):
            phrase = re.sub(r"\s+", " ", m.group(0))
            if phrase.lower() == "processing" and _PROCESSING_AS_VERB.search(masked[: m.start()]):
                continue
            key = phrase.lower()
            if key in seen or _allowed(m.start(), len(m.group(0)), allow):
                continue
            seen.add(key)
            out.append(("nominalization", m.start(), phrase,
                        f'nominalization "{phrase}" hides who does what'))

    obligation_matches = obligations(masked)
    condition_fired = False
    if "incomplete-condition" in on and structure.keyword:
        kw = structure.keyword.upper()
        if structure.if_without_then:
            condition_fired = not obligation_matches
            out.append(("incomplete-condition", 0, structure.keyword,
                        'IF condition without THEN (use "IF <condition>, THEN the <system> '
                        'shall <response>")'))
        elif not structure.has_response:
            condition_fired = not obligation_matches
            out.append(("incomplete-condition", 0, structure.keyword,
                        f"{kw} clause has no response with shall/should/may/must"))

    if "missing-obligation" in on and not story and not obligation_matches and not condition_fired:
        message = "no obligation verb (shall/should/may/must) and not a user story"
        if _CAN.search(masked):
            message += '; "can" states an ability, not an obligation'
        out.append(("missing-obligation", 0, "", message))

    if "future-tense" in on and not story and not obligation_matches:
        for m in _WILL.finditer(masked):
            before = masked[: m.start()]
            if re.search(r"\b(?:at|the|a|free|good|ill|his|her|their|own)\s+$", before, re.I):
                continue
            out.append(("future-tense", m.start(), m.group(0),
                        f'"{m.group(0)}" used as the obligation verb'))
            break

    if "compound-requirement" in on:
        compound = find_compound(masked, region)
        if compound:
            out.append(("compound-requirement", compound[0], compound[1], compound[2]))
    return out


# --------------------------------------------------------------------------- configuration


def _as_list(value, where: str) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [v.strip() for v in value.split(",") if v.strip()]
    if isinstance(value, list) and all(isinstance(v, str) for v in value):
        return [v.strip() for v in value if v.strip()]
    raise UsageError(f"schema: {where} must be a list of strings")


def _split_rules(values: Optional[Sequence[str]]) -> List[str]:
    out: List[str] = []
    for value in values or []:
        out.extend(v.strip() for v in value.split(",") if v.strip())
    return out


def build_config(schema: Dict, disable: Sequence[str] = (), enable: Sequence[str] = ()) -> Config:
    lint_cfg = schema.get("lint") or {}
    if not isinstance(lint_cfg, dict):
        raise UsageError("schema: lint must be an object")
    severity = {rid: rule.severity for rid, rule in RULES.items()}
    enabled = set(RULES)
    for rid in _as_list(lint_cfg.get("disable"), "lint.disable"):
        if rid not in RULES:
            _warn(f"schema lint.disable: unknown rule {rid!r} ignored")
            continue
        enabled.discard(rid)
    overrides = lint_cfg.get("severity") or {}
    if not isinstance(overrides, dict):
        raise UsageError("schema: lint.severity must be an object mapping rule IDs to severities")
    for rid, level in overrides.items():
        if rid not in RULES:
            _warn(f"schema lint.severity: unknown rule {rid!r} ignored")
            continue
        level_s = str(level).strip().lower()
        if level_s in ("off", "none", "disabled"):
            enabled.discard(rid)
        elif level_s in SEVERITY_RANK:
            severity[rid] = level_s
        else:
            raise UsageError(
                f"schema: lint.severity.{rid} must be one of error, warning, info, off (got {level!r})")
    for label, ids in (("--disable", disable), ("--enable", enable)):
        unknown = [r for r in ids if r not in RULES]
        if unknown:
            raise UsageError(f"{label}: unknown rule(s) {', '.join(unknown)}; "
                             f"valid rules: {', '.join(RULES)}")
    enabled.difference_update(disable)
    enabled.update(enable)
    weak = list(WEAK_WORDS) + _as_list(lint_cfg.get("extra_weak_words"), "lint.extra_weak_words")
    allow = _as_list(lint_cfg.get("allow_words"), "lint.allow_words")
    allow_lower = {a.lower() for a in allow}
    weak = [w for w in weak if w.lower() not in allow_lower]
    return Config(severity=severity, enabled=enabled, weak_re=_phrase_regex(weak),
                  allow_re=_phrase_regex(allow))


def _warn(message: str) -> None:
    sys.stderr.write(f"re-lint: warning: {message}\n")


# --------------------------------------------------------------------------- inputs


@dataclass
class Inputs:
    workspace: Path
    registers: List[Path] = field(default_factory=list)  # CSV files (requirement registers or details)
    markdown: List[Path] = field(default_factory=list)
    details: List[Path] = field(default_factory=list)  # detail CSVs scanned only for drift
    explicit: bool = False


def _workspace_name(schema: Optional[Dict]) -> str:
    return str((schema or {}).get("workspace") or "requirements")


def infer_workspace(path: Path) -> Path:
    """The workspace folder holding ``path``: nearest ancestor with ``schema.json`` or named like it."""
    here = path.resolve()
    folder = here if here.is_dir() else here.parent
    root = reqio.find_repo_root(folder)
    for candidate in [folder, *folder.parents]:
        if (candidate / "schema.json").is_file() or candidate.name == "requirements":
            return candidate
        if candidate == root:
            break
    default = reqio.find_workspace(folder)
    try:
        folder.relative_to(default)
        return default
    except ValueError:
        return folder


def workspace_schema(ws: Path) -> Dict:
    """``<ws>/schema.json``, else ``<repo root>/requirements/schema.json`` (where a renamed
    workspace is declared), else the defaults."""
    if (ws / "schema.json").is_file():
        return reqio.load_schema(workspace=ws)
    return reqio.load_schema(path=reqio.find_repo_root(ws) / "requirements" / "schema.json")


def _workspace_files(ws: Path) -> Tuple[List[Path], List[Path], List[Path]]:
    registers: List[Path] = []
    main = ws / "requirements.csv"
    if main.is_file():
        registers.append(main)
    markdown: List[Path] = []
    details: List[Path] = []
    if ws.is_dir():
        for path in sorted(ws.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(ws).parts
            if rel and (rel[0] in _GENERATED_DIRS or any(p.startswith(".") for p in rel)):
                continue
            suffix = path.suffix.lower()
            if suffix in (".md", ".markdown"):
                markdown.append(path)
            elif suffix == ".csv" and path != main:
                details.append(path)
    return registers, markdown, details


def collect_inputs(paths: Sequence[str], schema_path: Optional[str],
                   workspace: Optional[str] = None) -> Tuple[Inputs, Dict]:
    if schema_path and not Path(schema_path).is_file():
        raise UsageError(f"--schema: file not found: {schema_path}")
    if workspace and not Path(workspace).is_dir():
        raise UsageError(f"--workspace: folder not found: {workspace}")
    if not paths:
        schema = reqio.load_schema(path=schema_path) if schema_path else None
        ws = Path(workspace).resolve() if workspace else reqio.find_workspace(".", schema=schema)
        if schema is None:
            schema = workspace_schema(ws)
        registers, markdown, details = _workspace_files(ws)
        if not registers and not markdown:
            raise UsageError(
                f"no requirement register found: {_display(ws / 'requirements.csv')} does not exist "
                "(pass PATH, or create the workspace with the re-setup skill)")
        return Inputs(ws, registers, markdown, details), schema
    inputs = Inputs(infer_workspace(Path(paths[0])), explicit=True)
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            registers, markdown, details = _workspace_files(p)
            inputs.registers += registers
            inputs.markdown += markdown
            inputs.details += details
        elif not p.exists():
            raise UsageError(f"file not found: {raw}")
        elif p.suffix.lower() == ".csv":
            inputs.registers.append(p)
        elif p.suffix.lower() in (".md", ".markdown"):
            inputs.markdown.append(p)
        else:
            raise UsageError(f"{raw}: unsupported file type (use .csv or .md)")
    schema = reqio.load_schema(path=schema_path) if schema_path else workspace_schema(inputs.workspace)
    return inputs, schema


# --------------------------------------------------------------------------- locating matches


class Locator:
    """Maps an offset inside a cell value to a (line, column) in the source file."""

    def __init__(self) -> None:
        self._lines: Dict[str, List[str]] = {}

    def _file_lines(self, file: str) -> List[str]:
        if file not in self._lines:
            try:
                self._lines[file] = Path(file).read_text(encoding="utf-8").splitlines()
            except (OSError, UnicodeDecodeError):
                self._lines[file] = []
        return self._lines[file]

    def locate(self, row: reqio.Row, value: str, offset: int) -> Tuple[int, Optional[int]]:
        lines = self._file_lines(row.file)
        end_line = max(row.line, getattr(row, "end_line", row.line))
        chunk = "\n".join(lines[row.line - 1: end_line])
        if not chunk or not value:
            return row.line, None
        variants = [(value.replace('"', '""'), '"'), (value.replace("|", "\\|"), "|"), (value, "")]
        for encoded, doubled in variants:
            idx = chunk.find(encoded)
            if idx < 0:
                continue
            extra = value[:offset].count(doubled) if doubled else 0
            absolute = idx + offset + extra
            line = row.line + chunk.count("\n", 0, absolute)
            column = absolute - (chunk.rfind("\n", 0, absolute) + 1) + 1
            return line, column
        return row.line, None


# --------------------------------------------------------------------------- checking


def _display(path) -> str:
    p = Path(path)
    try:
        rel = os.path.relpath(str(p.resolve()), os.getcwd())
    except ValueError:  # different drive on Windows
        rel = str(p)
    if rel.startswith(".." + os.sep) and p.is_absolute():
        rel = str(p)
    return rel.replace(os.sep, "/")


def _is_placeholder(value: str) -> bool:
    return bool(_TBD_ONLY.match(value or ""))


def _normalize_echo(text: str) -> str:
    text = re.sub(r"<br\s*/?>", " ", text or "", flags=re.I)
    text = text.replace("**", "").replace("__", "")
    return re.sub(r"\s+", " ", text).strip().strip('"').strip()


def _texts_match(canonical: str, echo: str) -> bool:
    """Whitespace, emphasis and a final period do not count; a trailing ellipsis marks a prefix."""
    a, b = _normalize_echo(canonical), _normalize_echo(echo)
    for ellipsis in ("...", "\u2026"):
        if b.endswith(ellipsis):
            stem = b[: -len(ellipsis)].rstrip()
            return bool(stem) and a.startswith(stem)
    return a.rstrip(".").rstrip() == b.rstrip(".").rstrip()


class Checker:
    def __init__(self, schema: Dict, config: Config, inputs: Inputs) -> None:
        self.schema = schema
        self.config = config
        self.inputs = inputs
        self.findings: List[Finding] = []
        self.rows_checked = 0
        self.files_checked: List[str] = []
        self.req_pattern = reqio.id_regex("requirement", schema)
        attrs = schema.get("attributes") or {}
        self.required = [c for c in attrs.get("required", []) if isinstance(c, str)]
        self.enums: Dict[str, List[str]] = {
            k: [str(x) for x in v] for k, v in (attrs.get("enums") or {}).items() if isinstance(v, list)}
        self.locator = Locator()
        self._known_sources: Optional[Dict[str, Optional[Set[str]]]] = None

    # -- helpers
    def add(self, rule: str, row: Optional[reqio.Row], message: str, *, match: str = "",
            file: str = "", line: int = 0, column: Optional[int] = None,
            related: Sequence[reqio.Row] = ()) -> None:
        if rule not in self.config.enabled:
            return
        rid = row.get_str("ID") if row is not None else ""
        src = row.file if row is not None else file
        rows = [r for r in ([row] if row is not None else []) + list(related)]
        rel = [(r.file, r.line, max(r.line, getattr(r, "end_line", r.line))) for r in rows]
        if row is None:
            rel.append((file, line, line))
        self.findings.append(Finding(
            rule=rule, severity=self.config.severity[rule], id=rid, file=_display(src),
            line=line or (row.line if row is not None else 0), column=column, match=match,
            message=message, hint=RULES[rule].hint, related=rel,
            scope="row" if row is not None else "file"))

    def is_requirement_id(self, value: str) -> bool:
        return bool(self.req_pattern.match(value or ""))

    # -- main flow
    def run(self) -> None:
        canonical: Dict[str, reqio.Row] = {}
        definitions: List[Tuple[reqio.Row, List[str], bool]] = []  # row, columns, full register
        echoes: List[reqio.Row] = []
        for path in self.inputs.registers:
            table = reqio.read_table(path)
            self.files_checked.append(_display(path))
            is_main = path.name == "requirements.csv"
            if "ID" not in table.columns:
                if is_main or self.inputs.explicit:
                    if not table.columns and not table.rows:
                        continue  # empty file
                    raise UsageError(f"{_display(path)}: no 'ID' column in the header; "
                                     "is this a requirement register?")
                continue
            if not is_main and not self._looks_like_register(table.columns):
                echoes.extend(r for r in table.rows if self.is_requirement_id(r.get_str("ID")))
                continue
            self._check_header(table)
            for row in table.rows:
                rid = row.get_str("ID")
                definitions.append((row, table.columns, True))
                if not self.is_requirement_id(rid):
                    continue
                if rid in canonical:
                    first = canonical[rid]
                    self.add("duplicate-id", row, f"{rid} is already defined at "
                             f"{_display(first.file)}:{first.line}", match=rid, related=[first])
                else:
                    canonical[rid] = row
        for path in self.inputs.markdown:
            self._collect_markdown(path, canonical, definitions, echoes)
        for path in self.inputs.details:
            try:
                tables = reqio.read_tables(path)
            except ValueError as exc:
                _warn(f"skipping {_display(path)}: {exc}")
                continue
            found = False
            for table in tables:
                if "ID" in table.columns:
                    rows = [r for r in table.rows if self.is_requirement_id(r.get_str("ID"))]
                    echoes.extend(rows)
                    found = found or bool(rows)
            if found:
                self.files_checked.append(_display(path))
        for row, columns, full in definitions:
            self._check_row(row, columns, full)
        self._check_drift(canonical, echoes)
        self.rows_checked = len(definitions) + len(echoes)

    @staticmethod
    def _looks_like_register(columns: Sequence[str]) -> bool:
        return "Text" in columns and any(c in columns for c in ("Type", "Status", "Priority", "Source"))

    def _collect_markdown(self, path: Path, canonical: Dict[str, reqio.Row],
                          definitions: List[Tuple[reqio.Row, List[str], bool]],
                          echoes: List[reqio.Row]) -> None:
        """Markdown tables are registers only when their header has every required column.

        Any other table holding requirement IDs is a view or a report: its rows are echoes of a
        register (checked for drift) or, when no register defines the ID, get the text rules only.
        """
        try:
            tables = reqio.read_tables(path)
        except ValueError as exc:
            if self.inputs.explicit:
                raise
            _warn(f"skipping {_display(path)}: {exc}")
            return
        used = False
        local: Dict[str, reqio.Row] = {}
        for table in tables:
            if "ID" not in table.columns:
                continue
            ids = [r.get_str("ID") for r in table.rows]
            if not any(self.is_requirement_id(v) for v in ids):
                continue
            used = True
            full = bool(self.required) and all(c in table.columns for c in self.required)
            for row in table.rows:
                rid = row.get_str("ID")
                valid = self.is_requirement_id(rid)
                if valid and rid in canonical:
                    echoes.append(row)
                    continue
                if not full:
                    # A view or report: lint the first row of each requirement ID, nothing else.
                    if valid and rid not in local:
                        local[rid] = row
                        definitions.append((row, table.columns, False))
                    continue
                if valid:
                    if rid in local:
                        first = local[rid]
                        self.add("duplicate-id", row, f"{rid} is already defined at "
                                 f"{_display(first.file)}:{first.line}", match=rid, related=[first])
                    else:
                        local[rid] = row
                if rid or any(row.get_str(c) for c in table.columns):
                    definitions.append((row, table.columns, True))
        if used or self.inputs.explicit:
            self.files_checked.append(_display(path))

    def _check_header(self, table: reqio.Table) -> None:
        missing = [c for c in self.required if c not in table.columns]
        for column in missing:
            self.add("missing-attribute", None, f'required column "{column}" is missing from the header',
                     match=column, file=table.file, line=table.header_line)

    def _invalid_id_message(self, value: str) -> str:
        example = reqio.format_id("requirement", 1, self.schema)
        return f'"{value}" does not match the requirement ID pattern {self.req_pattern.pattern} (e.g. {example})'

    def _check_row(self, row: reqio.Row, columns: Sequence[str], full: bool) -> None:
        """All rules for register rows (``full``); the text rules only for rows of a partial view."""
        rid = row.get_str("ID")
        if full:
            if rid and not self.is_requirement_id(rid):
                self.add("invalid-id", row, self._invalid_id_message(rid), match=rid)
            for column in self.required:
                if column in columns and not row.get_str(column):
                    self.add("missing-attribute", row, f'required attribute "{column}" is empty',
                             match=column)
            for column, allowed in self.enums.items():
                if column not in columns:
                    continue
                value = row.get_str(column)
                if not value or _is_placeholder(value) or value in allowed:
                    continue
                near = [a for a in allowed if a.lower() == value.lower()]
                hint = f' (did you mean "{near[0]}"?)' if near else ""
                self.add("invalid-enum", row,
                         f'{column} "{value}" is not one of {", ".join(allowed)}{hint}', match=value)
            self._check_sources(row)
        status = row.get_str("Status").lower()
        if status in ("withdrawn", "rejected"):
            return
        text = row.get("Text") or ""
        for rule, offset, match, message in check_text(text, self.config):
            line, column = self.locator.locate(row, text, offset)
            self.add(rule, row, message, match=match, line=line, column=column)
        if full and "open-tbd" in self.config.enabled:
            for column in columns:
                if column in ("ID", "Text"):
                    continue
                value = row.get_str(column)
                m = _TBD.search(value)
                if m:
                    self.add("open-tbd", row, f'open placeholder "{m.group(0)}" in {column}',
                             match=m.group(0))

    # -- unregistered-source
    def _source_registry(self) -> Dict[str, Optional[Set[str]]]:
        if self._known_sources is not None:
            return self._known_sources
        ws = self.inputs.workspace
        known: Dict[str, Optional[Set[str]]] = {"source": None, "stakeholder": None, "interview": None}
        sources = ws / "sources.csv"
        stakeholders = ws / "stakeholders.md"
        if sources.is_file():
            known["source"] = self._ids_in(sources, "source")
        if stakeholders.is_file():
            known["stakeholder"] = self._ids_in(stakeholders, "stakeholder")
        if (sources.is_file() or stakeholders.is_file()) and (ws / "elicitation").is_dir():
            register_files = {p.resolve() for p in self.inputs.registers}
            found: Set[str] = set()
            for path in ws.rglob("*"):
                if path.is_file() and path.resolve() not in register_files and path.suffix.lower() in (
                        ".md", ".csv", ".txt", ".markdown"):
                    found |= self._ids_in(path, "interview")
            known["interview"] = found
        self._known_sources = known
        return known

    def _ids_in(self, path: Path, kind: str) -> Set[str]:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return set()
        pattern = reqio.id_prefix_regex(kind, self.schema)
        return {reqio.format_id(kind, int(m.group(1)), self.schema) for m in pattern.finditer(text)}

    def _check_sources(self, row: reqio.Row) -> None:
        if "unregistered-source" not in self.config.enabled:
            return
        value = row.get_str("Source")
        if not value:
            return
        registry = self._source_registry()
        labels = {"source": "sources.csv", "stakeholder": "stakeholders.md", "interview": "the workspace"}
        for kind in ("source", "stakeholder", "interview"):
            known = registry.get(kind)
            if known is None:
                continue
            for m in reqio.id_prefix_regex(kind, self.schema).finditer(value):
                cited = reqio.format_id(kind, int(m.group(1)), self.schema)
                if cited not in known:
                    self.add("unregistered-source", row,
                             f"Source cites {m.group(0)}, which is not in {labels[kind]}", match=m.group(0))

    # -- register-drift
    def _check_drift(self, canonical: Dict[str, reqio.Row], echoes: Sequence[reqio.Row]) -> None:
        for row in echoes:
            original = canonical.get(row.get_str("ID"))
            echo = row.get("Text")
            if original is None or echo is None or not str(echo).strip():
                continue
            if not _texts_match(original.get_str("Text"), str(echo)):
                self.add("register-drift", row,
                         f"text differs from {_display(original.file)}:{original.line}",
                         match=row.get_str("ID"), related=[original])


# --------------------------------------------------------------------------- --changed-only


def changed_lines(path: str, base: str) -> Optional[Set[int]]:
    """Lines of ``path`` added or changed since ``base`` (merge base with HEAD).

    Returns ``None`` when every line counts as changed (untracked file) and raises
    ``RuntimeError`` when git cannot answer.
    """
    folder = str(Path(path).resolve().parent)

    def git(*args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", *args], cwd=folder, capture_output=True, text=True, timeout=60)

    try:
        if git("rev-parse", "--is-inside-work-tree").returncode != 0:
            raise RuntimeError("not inside a git repository")
        if git("rev-parse", "--verify", "--quiet", f"{base}^{{commit}}").returncode != 0:
            raise RuntimeError(f"unknown base ref {base!r} (fetch it first, e.g. fetch-depth: 0)")
        target = Path(path).resolve()
        if git("ls-files", "--error-unmatch", "--", str(target)).returncode != 0:
            return None  # untracked: every row is new
        merge_base = git("merge-base", base, "HEAD")
        ref = merge_base.stdout.strip() if merge_base.returncode == 0 and merge_base.stdout.strip() else base
        diff = git("diff", "-U0", "--no-color", "--no-ext-diff", ref, "--", str(target))
    except FileNotFoundError:
        raise RuntimeError("git is not installed") from None
    except subprocess.TimeoutExpired:
        raise RuntimeError("git timed out") from None
    if diff.returncode != 0:
        raise RuntimeError(diff.stderr.strip() or "git diff failed")
    lines: Set[int] = set()
    for m in re.finditer(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", diff.stdout, re.M):
        start, count = int(m.group(1)), int(m.group(2) or 1)
        lines.update(range(start, start + count))
    return lines


def filter_changed(findings: List[Finding], base: str) -> List[Finding]:
    cache: Dict[str, Optional[Set[int]]] = {}
    failed: Set[str] = set()

    def changed(file: str, first: int, last: int) -> bool:
        if file in failed:
            return True
        if file not in cache:
            try:
                cache[file] = changed_lines(file, base)
            except RuntimeError as exc:
                _warn(f"--changed-only: {exc}; checking all rows of {_display(file)}")
                failed.add(file)
                return True
        lines = cache[file]
        return lines is None or any(n in lines for n in range(first, last + 1))

    return [f for f in findings if any(changed(*r) for r in f.related)]


# --------------------------------------------------------------------------- output


def _summary(findings: Sequence[Finding]) -> Dict[str, int]:
    counts = {s: 0 for s in ("error", "warning", "info")}
    for f in findings:
        counts[f.severity] += 1
    return counts


def _plural(n: int, word: str) -> str:
    return f"{n} {word}" + ("" if n == 1 or word == "info" else "s")


def summary_line(findings: Sequence[Finding], rows: int, files: int) -> str:
    c = _summary(findings)
    where = f"{_plural(rows, 'row')} ({_plural(files, 'file')})"
    if not findings:
        return f"re-lint: no findings in {where}"
    parts = [_plural(c["error"], "error"), _plural(c["warning"], "warning"), _plural(c["info"], "info")]
    return f"re-lint: {', '.join(parts)} in {where}"


def format_text(findings: Sequence[Finding], rows: int, files: int) -> str:
    out: List[str] = []
    for f in findings:
        rid = f" {f.id}" if f.id else ""
        out.append(f"{f.file}:{f.line}: {f.severity} {f.rule}{rid}: {f.message}")
        out.append(f"    hint: {f.hint}")
    out.append(summary_line(findings, rows, files))
    return "\n".join(out) + "\n"


def format_json(findings: Sequence[Finding], rows: int, files: Sequence[str]) -> str:
    doc = {
        "tool": "re-lint", "version": VERSION, "files": list(files), "rows_checked": rows,
        "summary": _summary(findings), "findings": [f.to_dict() for f in findings],
    }
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


def _gh_data(value: str) -> str:
    return value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def _gh_prop(value: str) -> str:
    return _gh_data(value).replace(":", "%3A").replace(",", "%2C")


def format_github(findings: Sequence[Finding], rows: int, files: int) -> str:
    level = {"error": "error", "warning": "warning", "info": "notice"}
    out = []
    for f in findings:
        text = f"{f.id}: {f.message}" if f.id else f.message
        out.append(f"::{level[f.severity]} file={_gh_prop(f.file)},line={f.line},"
                   f"title={_gh_prop('re-lint ' + f.rule)}::{_gh_data(text)}")
    out.append(summary_line(findings, rows, files))
    return "\n".join(out) + "\n"


def format_sarif(findings: Sequence[Finding], config: Config) -> str:
    level = {"error": "error", "warning": "warning", "info": "note"}
    rule_ids = list(RULES)
    rules = []
    for rid in rule_ids:
        rule = RULES[rid]
        name = "".join(part.capitalize() for part in rid.split("-"))
        rules.append({
            "id": rid,
            "name": name,
            "shortDescription": {"text": rule.summary.replace("`", "")},
            "fullDescription": {"text": f"{rule.summary} Example: {rule.example}".replace("`", "")},
            "help": {"text": rule.hint.replace("`", ""),
                     "markdown": f"**{rid}**: {rule.summary}\n\nExample that fires: {rule.example}\n\n"
                                 f"Fix: {rule.hint}"},
            "helpUri": f"{INFO_URI}#rules",
            "defaultConfiguration": {"level": level[config.severity[rid]],
                                     "enabled": rid in config.enabled},
            "properties": {"tags": ["requirements", rule.kind]},
        })
    results = []
    for f in findings:
        region: Dict[str, int] = {"startLine": max(1, f.line)}
        if f.column:
            region["startColumn"] = f.column
        text = f"{f.id}: {f.message}" if f.id else f.message
        fingerprint = hashlib.sha256(f"{f.rule}|{f.id}|{f.match}|{f.file}".encode("utf-8")).hexdigest()
        results.append({
            "ruleId": f.rule,
            "ruleIndex": rule_ids.index(f.rule),
            "level": level[f.severity],
            "message": {"text": f"{text}. Hint: {f.hint.replace('`', '')}"},
            "locations": [{"physicalLocation": {
                "artifactLocation": {"uri": f.file, "uriBaseId": "%SRCROOT%"},
                "region": region}}],
            "partialFingerprints": {"reLintFinding/v1": fingerprint[:32]},
            "properties": {"requirementId": f.id, "match": f.match},
        })
    doc = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {"name": "re-lint", "version": VERSION, "semanticVersion": VERSION,
                                "informationUri": INFO_URI, "rules": rules}},
            "columnKind": "unicodeCodePoints",
            "results": results,
        }],
    }
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


def format_rules() -> str:
    width = max(len(r) for r in RULES)
    lines = [f"{'RULE':<{width}}  {'DEFAULT':<8} SUMMARY"]
    for rule in RULES.values():
        lines.append(f"{rule.id:<{width}}  {rule.severity:<8} {rule.summary.replace('`', '')}")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- API


def lint(paths: Sequence[str] = (), schema_path: Optional[str] = None,
         disable: Sequence[str] = (), enable: Sequence[str] = (),
         only_ids: Sequence[str] = (), changed_only: Optional[str] = None,
         workspace: Optional[str] = None) -> Tuple[List[Finding], "Checker"]:
    """Lint ``paths`` (default: the workspace) and return ``(findings, checker)``.

    Raises :class:`UsageError` for usage or schema problems and ``ValueError`` for parse errors.
    """
    inputs, schema = collect_inputs(paths, schema_path, workspace)
    config = build_config(schema, disable, enable)
    checker = Checker(schema, config, inputs)
    checker.run()
    findings = checker.findings
    if only_ids:
        wanted = set(only_ids)
        present = {f.id for f in findings} | _ids_seen(checker)
        for rid in sorted(wanted - present):
            _warn(f"--only-ids: {rid} not found")
        findings = [f for f in findings if f.id in wanted or f.scope == "file"]
    if changed_only:
        findings = filter_changed(findings, changed_only)
    order = {rid: n for n, rid in enumerate(RULES)}
    findings.sort(key=lambda f: (f.file, f.line, f.column or 0, order[f.rule]))
    return findings, checker


def _ids_seen(checker: Checker) -> Set[str]:
    seen: Set[str] = set()
    for path in checker.inputs.registers + checker.inputs.markdown:
        try:
            for table in reqio.read_tables(path):
                seen.update(r.get_str("ID") for r in table.rows)
        except (OSError, ValueError):
            continue
    return seen


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Lint requirement text and attributes: weak words, universal quantifiers, "
                    "passive voice, EARS conditions, obligation verbs, compound requirements, open "
                    "TBDs, IDs, required attributes and enum values.",
        epilog="Exit codes: 0 clean, 1 findings at or above --fail-on, 2 usage, schema or parse "
               "error. Configure rules in schema.json under lint.disable, lint.severity, "
               "lint.extra_weak_words and lint.allow_words.",
    )
    parser.add_argument("paths", nargs="*", metavar="PATH",
                        help="requirement files (.csv or .md) or workspace folders; default: "
                             "<workspace>/requirements.csv plus Markdown tables under the workspace")
    parser.add_argument("--schema", metavar="FILE",
                        help="schema.json to use (default: <workspace>/schema.json, else built-in defaults)")
    parser.add_argument("--workspace", metavar="DIR",
                        help="workspace folder to lint when no PATH is given (default: <repo root>/requirements, "
                             "or the schema's workspace)")
    parser.add_argument("--format", choices=("text", "json", "github", "sarif"), default="text",
                        help="output format: text (default), json, github (Actions annotations), sarif")
    parser.add_argument("--fail-on", choices=("error", "warning", "info"), default="error",
                        help="exit 1 when a finding has this severity or higher (default: error)")
    parser.add_argument("--disable", action="append", metavar="RULE[,RULE]", default=[],
                        help="turn rules off (repeatable or comma-separated)")
    parser.add_argument("--enable", action="append", metavar="RULE[,RULE]", default=[],
                        help="turn rules on, overriding lint.disable in schema.json")
    parser.add_argument("--only-ids", action="append", metavar="R-001,R-002", default=[],
                        help="report only findings for these requirement IDs")
    parser.add_argument("--changed-only", metavar="BASE_REF",
                        help="report only rows changed versus BASE_REF (e.g. origin/main); falls "
                             "back to all rows when git cannot answer")
    parser.add_argument("--list-rules", action="store_true", help="print the rule registry and exit")
    return parser


def run(args: argparse.Namespace) -> int:
    if getattr(args, "list_rules", False):
        sys.stdout.write(format_rules())
        return 0
    try:
        findings, checker = lint(
            paths=args.paths, schema_path=args.schema,
            disable=_split_rules(args.disable), enable=_split_rules(args.enable),
            only_ids=_split_rules(args.only_ids), changed_only=args.changed_only,
            workspace=getattr(args, "workspace", None))
    except UsageError as exc:
        sys.stderr.write(f"re-lint: error: {exc}\n")
        return 2
    except (ValueError, OSError) as exc:
        sys.stderr.write(f"re-lint: error: {exc}\n")
        return 2
    files = checker.files_checked
    if args.format == "json":
        sys.stdout.write(format_json(findings, checker.rows_checked, files))
    elif args.format == "github":
        sys.stdout.write(format_github(findings, checker.rows_checked, len(files)))
    elif args.format == "sarif":
        sys.stdout.write(format_sarif(findings, checker.config))
    else:
        sys.stdout.write(format_text(findings, checker.rows_checked, len(files)))
    threshold = SEVERITY_RANK[args.fail_on]
    return 1 if any(SEVERITY_RANK[f.severity] >= threshold for f in findings) else 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return run(args)
    except BrokenPipeError:  # e.g. piped into head
        return 0


if __name__ == "__main__":
    sys.exit(main())
