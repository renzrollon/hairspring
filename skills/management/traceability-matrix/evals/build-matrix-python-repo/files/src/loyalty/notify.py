"""Member notifications."""


# @req R-022
def balance_sms(balance: int) -> str:
    return f"Harbourline Rewards: your balance is {balance} points."
