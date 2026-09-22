from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class GroceryListItem(BaseModel):
    ingredient: str
    unit: str
    required_quantity: Decimal
    pantry_quantity: Decimal
    quantity_to_buy: Decimal
    estimated_cost: Decimal | None = None


class GroceryListResponse(BaseModel):
    start_date: date
    end_date: date
    items: list[GroceryListItem]
    total_estimated_cost: Decimal | None = None