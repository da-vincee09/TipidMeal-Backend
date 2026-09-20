from datetime import date, datetime
from zoneinfo import ZoneInfo

from core.constants import APP_TIMEZONE, MEAL_SLOT_CUTOFFS


def get_app_now() -> datetime:
    return datetime.now(ZoneInfo(APP_TIMEZONE))


def is_planned_slot_in_past(planned_date: date, meal_slot: str | None) -> bool:
    now = get_app_now()
    today = now.date()

    if planned_date < today:
        return True

    if planned_date > today:
        return False

    if not meal_slot:
        return False

    cutoff = MEAL_SLOT_CUTOFFS.get(meal_slot.lower())
    if cutoff is None:
        return False

    return now.time() >= cutoff