# Input: constraint candidates for the loyalty-points service

Handed over on 2026-11-03 by the `quality-requirements` walkthrough (its *Unquantified and reclassified concerns*), plus statements from the platform team and Finance. Workspace state: `requirements.csv` holds R-001 to R-099; `sources.csv` holds S-01 to S-07; `stakeholders.md` holds SH-01 to SH-09. Today is 2026-11-03.

1. "We have to integrate through the TillPoint loyalty interface v2.1; the vendor won't change it before v2.2." (Wei Jie Chua, SH-08, 2026-11-03; the spec is S-02). The v2.2 upgrade is announced for March 2027 (vendor, I-02).
2. "PCI is out of scope because we never see card numbers." (Lena Koh, SH-05, 2026-11-03)
3. "We keep transaction data 7 years (DRP-2024)." (Grace Lim, SH-03, email 2026-11-02; DRP-2024 is part of S-05)
4. "Member personal data must stay in Singapore." (Farid Osman, SH-04, 2026-11-03, citing DRP-2024)
5. "Every new service runs on the shared Kubernetes platform. No exceptions this year." (Wei Jie Chua, SH-08, 2026-11-03, platform team standard)
6. "The legacy loyalty module's vendor contract ends on 31 March 2027 and we will not extend it." (Grace Lim, SH-03, 2026-11-03)
7. "Use Kafka between the POS and the service." (loyalty squad design discussion, 2026-11-03; nobody named a mandate)
8. "We'll write the service in Go." (loyalty squad, 2026-11-03)
9. "Voucher validation must not slow down checkout." (Arjun Pillai, SH-02)
