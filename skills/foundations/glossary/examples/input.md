# Input: glossary run on the loyalty-points repo (Harbourline sample)

Prompt: "Build a glossary from docs/, src/ and the support ticket export." No `requirements/glossary.md` exists yet. Owners come from `requirements/stakeholders.md` (SH-01 Mei Tan, Head of Loyalty; SH-02 Arjun Pillai, store operations; SH-03 Grace Lim, Finance; SH-05 Lena Koh, security; SH-06 Daniel Ng, support; SH-07 Priya Raman, marketing; SH-08 Wei Jie Chua, platform tech lead).

## `docs/programme-notes.md`

```markdown
# Harbourline Rewards: programme notes (from T&C draft v3, S-01)

- A member earns 1 point per SGD 1 spent at a Harbourline store or in the app, rounded down per purchase.
- Points stay pending for 24 hours after the purchase (return window); then the points are posted.
- Posted points can be redeemed for a voucher: 100 points = SGD 1, minimum 500 points.
- A bonus campaign multiplies the points earned on a purchase.
- Points expire 12 months after posting.
- Members are grouped into tiers; tier rules are not final.
- Finance books unredeemed posted points in the points liability account.
- The cashier scans the member QR code at the POS.
```

## `docs/team.md`

```markdown
# Team notes

- PO: Mei Tan (Head of Loyalty). The PO accepts stories at sprint review.
- Store ops: raise a PO for receipt paper through the store portal; the PO number goes on the invoice.
- Support agents log in to the admin console with their staff account.
```

## `src/loyalty/models.py`

```python
class Customer:
    """A loyalty member (the legacy POS module calls them customers)."""

    customer_id: str
    tier: str


class PointsTransaction:
    """One entry in a customer's points ledger."""

    transaction_id: str
    customer_id: str
    status: str  # PENDING, POSTED, REDEEMED, EXPIRED, REVERSED


class LedgerAccount:
    """Finance general-ledger account, for example the points liability account."""

    account_code: str
```

## `tickets/support-export.csv`

```csv
ticket,summary
LOY-201,"Member says her account is locked after three wrong passwords in the app"
LOY-202,"Account holder asks why points from Saturday's transaction are still pending"
LOY-203,"Support agent account cannot open the adjustment screen in the admin console"
LOY-204,"POS transaction shows no points; customer wants a manual adjustment"
LOY-205,"Customer asks when her points transaction will be posted"
```

## Step 3: `python3 scripts/mine_terms.py docs src tickets --format md --top 25`

| Term | Kind | Count | Files | Variants | In glossary | Locations |
| --- | --- | --- | --- | --- | --- | --- |
| points | word | 15 | 3 | points; Points; point | - | docs/programme-notes.md:3 docs/programme-notes.md:4 docs/programme-notes.md:5 |
| account | word | 7 | 4 | account; Account | - | docs/programme-notes.md:9 docs/team.md:5 src/loyalty/models.py:17 |
| customer | identifier+word | 7 | 2 | Customer; customer; customer_id; customers | - | src/loyalty/models.py:1 src/loyalty/models.py:2 src/loyalty/models.py:4 |
| member | word | 5 | 3 | member; Member; Members | - | docs/programme-notes.md:3 docs/programme-notes.md:8 docs/programme-notes.md:10 |
| posted | word | 5 | 3 | posted; POSTED; Posted | - | docs/programme-notes.md:4 docs/programme-notes.md:5 docs/programme-notes.md:9 |
| transaction | identifier+word | 4 | 2 | transaction; transaction_id | - | src/loyalty/models.py:11 tickets/support-export.csv:3 tickets/support-export.csv:5 |
| PO | acronym | 4 | 1 | PO | - | docs/team.md:3 docs/team.md:4 |
| POS | acronym | 3 | 3 | POS | - | docs/programme-notes.md:10 src/loyalty/models.py:2 tickets/support-export.csv:5 |
| pending | word | 3 | 3 | pending; PENDING | - | docs/programme-notes.md:4 src/loyalty/models.py:13 tickets/support-export.csv:3 |
| store | word | 3 | 2 | store; Store | - | docs/programme-notes.md:3 docs/team.md:4 |
| tier | word | 3 | 2 | tier; tiers | - | docs/programme-notes.md:8 src/loyalty/models.py:5 |
| purchase | word | 3 | 1 | purchase | - | docs/programme-notes.md:3 docs/programme-notes.md:4 docs/programme-notes.md:6 |
| admin | word | 2 | 2 | admin | - | docs/team.md:5 tickets/support-export.csv:4 |
| admin console | phrase | 2 | 2 | admin console | - | docs/team.md:5 tickets/support-export.csv:4 |
| agent | word | 2 | 2 | agent; agents | - | docs/team.md:5 tickets/support-export.csv:4 |
| app | word | 2 | 2 | app | - | docs/programme-notes.md:3 tickets/support-export.csv:2 |
| console | word | 2 | 2 | console | - | docs/team.md:5 tickets/support-export.csv:4 |
| finance | word | 2 | 2 | Finance | - | docs/programme-notes.md:9 src/loyalty/models.py:17 |
| liability | word | 2 | 2 | liability | - | docs/programme-notes.md:9 src/loyalty/models.py:17 |
| liability account | phrase | 2 | 2 | liability account | - | docs/programme-notes.md:9 src/loyalty/models.py:17 |
| loyalty | word | 2 | 2 | Loyalty; loyalty | - | docs/team.md:3 src/loyalty/models.py:2 |
| notes | word | 2 | 2 | notes | - | docs/programme-notes.md:1 docs/team.md:1 |
| points liability | phrase | 2 | 2 | points liability | - | docs/programme-notes.md:9 src/loyalty/models.py:17 |
| points liability account | phrase | 2 | 2 | points liability account | - | docs/programme-notes.md:9 src/loyalty/models.py:17 |
| points transaction | identifier+phrase | 2 | 2 | PointsTransaction; points transaction | - | src/loyalty/models.py:8 tickets/support-export.csv:6 |

Line numbers in the expected output refer to the files above, counting from line 1.
