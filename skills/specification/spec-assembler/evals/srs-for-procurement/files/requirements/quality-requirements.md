# Quality requirements: loyalty-points service

| Field | Value |
| --- | --- |
| System | loyalty-points service |
| System type | web API or service |
| Quality model | ISO/IEC 25010:2023 product quality model (characteristic and sub-characteristic names only) |
| Walkthrough | 2026-11-03, SH-01, SH-02, SH-05, SH-08, quality-requirements |

## Quality requirements

### Performance efficiency

| Requirement | Sub-characteristic | Metric | Target | Condition | Measurement method | Driver | Open question |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-080 | time behaviour | Server-side response time of voucher validation, 95th percentile, ms | TBD | At the planned peak load of R-082 | Load test with the peak profile; production p95 at the API gateway | yes | Q1 |
| R-082 | capacity | Purchase events accepted per minute, sustained; lost events | TBD per minute for TBD minutes; zero lost | Year-end sale peak; baseline 9,000 per minute (SH-08) | Load test replaying a peak-day profile | yes | Q3 |

### Security

| Requirement | Sub-characteristic | Metric | Target | Condition | Measurement method | Driver | Open question |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-086 | authenticity | API requests accepted without valid client credentials | None accepted (SH-05) | POS and app endpoints | Automated negative tests; penetration test | yes | none |

## Open questions

| # | Question | Recommended answer | Owner | Affects | Status |
| --- | --- | --- | --- | --- | --- |
| Q1 | What 95th-percentile voucher validation time can the till absorb without checkout getting slower? | Set it below the POS timeout in the TillPoint spec (S-02) | SH-02 Arjun Pillai with SH-09 | R-080 | open |
| Q3 | What purchase-event rate must we plan for at this year's year-end peak, and how long does the peak last? | Last year's 9,000 per minute (SH-08) plus the growth Marketing plans | SH-08 Wei Jie Chua with SH-07 Priya Raman | R-080, R-082 | open |
