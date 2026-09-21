from typing import Literal

from pydantic import BaseModel


class NutritionAdequacyResponse(BaseModel):
    caloric_adequacy: Literal["within", "below", "above", "unavailable"]
    food_group_proportions: dict[str, float] | None
    food_group_adequate: bool | None
    nutritionally_adequate: bool | None
    # True for staple meals (e.g. Garlic Fried Rice), which are not
    # judged as an ulam. Their verdicts are None and caloric_adequacy
    # is "unavailable". Defaults to False so older callers keep working.
    is_staple: bool = False