from sqlalchemy.orm import Session
from decimal import Decimal

from features.ingredients.models.ingredient import Ingredient
from features.ingredients.models.allergen_category import AllergenCategory
from features.ingredients.models.unit_conversion import UnitConversion


def get_or_create_ingredient(db: Session, name: str) -> Ingredient:
    """
    Looks up an Ingredient by name (case/whitespace-insensitive) and
    returns it, creating a new row if none exists. Used wherever a
    user-facing feature accepts free-text ingredient names (e.g.
    Profile's disliked_ingredients) that aren't guaranteed to already
    exist in the seeded meal vocabulary.
    """
    normalized = name.strip()

    existing = (
        db.query(Ingredient)
        .filter(Ingredient.name.ilike(normalized))
        .first()
    )
    if existing is not None:
        return existing

    ingredient = Ingredient(name=normalized)
    db.add(ingredient)
    db.flush()  # populate ingredient.id without committing the outer transaction
    return ingredient


def expand_allergen_categories(db: Session, categories: list[str]) -> set[str]:
    """
    Expands a list of allergy category names (e.g. "Shellfish", "Eggs")
    into the actual set of ingredient names that fall under them, via
    the allergen_categories mapping table. A category with no mapped
    ingredients (e.g. "Peanuts", not yet represented in the seed
    vocabulary) simply contributes nothing — not an error.
    """
    if not categories:
        return set()

    rows = (
        db.query(Ingredient.name)
        .join(AllergenCategory, AllergenCategory.ingredient_id == Ingredient.id)
        .filter(AllergenCategory.category.in_(categories))
        .all()
    )

    return {name for (name,) in rows}


def convert_quantity(
    db: Session,
    quantity: Decimal,
    from_unit: str,
    to_unit: str,
) -> Decimal | None:
    """
    Converts `quantity` from from_unit to to_unit, or returns None if
    no conversion path exists (e.g. count-based units like pcs/cloves,
    or an unrecognized unit). Same-unit is a trivial no-op conversion.
    """
    from_unit = from_unit.strip().lower()
    to_unit = to_unit.strip().lower()

    if from_unit == to_unit:
        return quantity

    conversion = (
        db.query(UnitConversion)
        .filter(
            UnitConversion.from_unit == from_unit,
            UnitConversion.to_unit == to_unit,
        )
        .first()
    )

    if conversion is None:
        return None

    return quantity * conversion.factor