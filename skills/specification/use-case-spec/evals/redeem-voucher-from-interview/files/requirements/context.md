# System context: loyalty-points service

| External element | Kind | Interface / data flow |
| --- | --- | --- |
| Customer (member) | person | Customer mobile app: view balance, history, redeem voucher |
| Cashier | person | TillPoint POS: scan member QR, apply voucher |
| TillPoint POS | system | POS to service: purchase events; service to POS: voucher validation |
| Customer mobile app | system | App to service: balance, history, redemption |
| Fraud engine | system | Service to fraud engine: earn and redeem events; fraud engine to service: hold, release |

Open decision D-02: voucher printing at the POS, vendor or us?
