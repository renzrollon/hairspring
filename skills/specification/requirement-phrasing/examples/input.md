# Input: ticket LOY-118 (loyalty-points sample)

> **LOY-118: Show points after purchase**
>
> After a member pays at the till, the app should quickly show the new balance. Points will be added once the purchase is processed. If something goes wrong with the fraud check the points are held. All members should get a push notification and an email when points are added. Use Redis to cache balances.
>
> Reporter: Mei Tan (Head of Loyalty), 2026-10-28. Source in the inventory: S-06.

The workspace already holds `R-001` to `R-019` (earning) and `R-020` to `R-022` (balance).
