"""Nightly expiry of posted points."""
from datetime import date

EXPIRY_MONTHS = 12


def add_months(d: date, months: int) -> date:
    year = d.year + (d.month - 1 + months) // 12
    month = (d.month - 1 + months) % 12 + 1
    return date(year, month, min(d.day, 28))


def is_expired(posted_on: date, today: date) -> bool:
    return today >= add_months(posted_on, EXPIRY_MONTHS)
