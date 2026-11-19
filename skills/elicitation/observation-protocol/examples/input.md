# Input: evening-peak shadowing of cashiers (loyalty-points sample)

## Run 1 (phase A), 2026-11-12

> `/observation-protocol half-day shadowing of two cashiers at the Tampines store during the evening peak on Wednesday 2026-11-18, to see what happens at the till with member QR scans, vouchers and network drops. Arjun arranged it with the store manager. I observe.`

The observer is Wei Jie Chua (SH-08); Arjun Pillai (SH-02) is the process owner for the till. Interview I-02 (Arjun) said QR scans fail when the phone screen is dim and that cashiers cannot type member numbers by hand today. `requirements/candidates.csv` holds CAN-001 to CAN-024.

## Run 2 (phase B), 2026-11-18

> `/observation-protocol field notes from today below, write it up and land the candidates`

Field notes, as typed after the session:

```text
17:00 start. Cashier A (till 3), Cashier B (till 4). Consent read out, both ok, store manager ok. Notes only.
17:20 A: member QR fails 3x, dim screen. A asks member to turn brightness up, works 4th try. ~40 s. "Happens all the time with old phones." Seen again 18:05, 18:50, 20:10 (B).
17:45 A: scan fails, member in a hurry. A writes receipt no. and member phone (Mrs Lim 9876 5432) on a notepad under the till. "Support adds the points later if they call." Notepad has ~15 entries from this week. Seen 3 more times (A 2x, B 1x).
18:10 B: voucher "invalid code" at till, app shows it active. B calls supervisor, supervisor key, manual SGD 5 discount, voucher no. written on back of receipt. ~2 min, queue of 6. Seen again 19:30.
19:05 network drop ~5 min, both tills. Sales continue, no loyalty scans. A tells members "points will come later". (they won't - nothing queues them)
19:40 member asks B "when do my points show?" B: "tomorrow I think". Same question 20:25 (A), 20:40 (A).
21:00 end.
Debrief 21:05-21:25 with A and B together:
- brightness: "every shift, many times", old phones and cracked screens. Want: "type the number when it fails".
- notepad: "every shift"; they know many members never call so points are lost. Want: "something that gives the points later from the receipt".
- voucher: "a few times a week"; supervisor key annoys supervisor too. Want: "if the app says ok, the till should say ok".
- network: "Friday and Saturday evenings mostly, maybe twice a week".
- points timing: "we never know, so we guess". Want: "a simple answer we can tell members".
- typical day? "yes, but Friday is worse". Watching changed anything? "We were a bit slower, more careful."
```

The expected output is the observation file after run 2 (`expected-output.md`) and the rows appended to `requirements/candidates.csv` (`expected-candidates.csv`).
