# System context: loyalty-points

The loyalty-points service lets members earn points on purchases and redeem them as vouchers worth SGD at checkout.

## Context boundary

| Aspect | Side | Source |
| --- | --- | --- |
| Singapore PDPA (member personal data) | context | S-05 |
| Programme terms and conditions | context | S-01 |

## Context table

| # | External element | Kind | Direction | Data flow | Interface | Owner | Status | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | TillPoint POS | system | in | Purchase events for earning | Events | POS vendor | confirmed | S-02 |
| 2 | Customer mobile app | system | in | Balance and redemption requests | REST API | App team | confirmed | I-01 |
| 3 | Fraud engine | system | out | Earn and redeem events for scoring | Events | TBD | confirmed | I-01 |
| 4 | Data warehouse | system | out | Daily points-liability extract for Finance | Batch | TBD | confirmed | I-01 |
| 5 | Support agent | person | in | Points adjustments | Admin console | TBD | confirmed | I-01 |
