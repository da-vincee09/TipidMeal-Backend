from datetime import time

APP_TIMEZONE = "Asia/Manila"

MEAL_SLOT_CUTOFFS: dict[str, time] = {
    "breakfast": time(10, 0),
    "lunch": time(14, 0),
    "dinner": time(21, 0),
}