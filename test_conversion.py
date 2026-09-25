from core.database import SessionLocal
from decimal import Decimal
from features.ingredients.repository import convert_quantity

db = SessionLocal()

# Simulates: pantry has cooked_rice: 2 kg, recipe needs 400 g
converted = convert_quantity(db, Decimal('2'), 'kg', 'g')
print(f'2 kg of cooked_rice = {converted} g')

required = Decimal('400')
covers_it = converted is not None and converted >= required
print(f'Recipe needs 400 g -- pantry covers it: {covers_it}')