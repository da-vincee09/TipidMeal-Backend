from sqlalchemy.orm import Session
from features.ingredients.models.ingredient import Ingredient


def normalize_ingredient_name(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


def get_or_create_ingredient(db: Session, name: str) -> Ingredient:
    normalized = normalize_ingredient_name(name)

    ingredient = (
        db.query(Ingredient)
        .filter(Ingredient.name == normalized)
        .first()
    )

    if ingredient is not None:
        return ingredient

    ingredient = Ingredient(name=normalized)
    db.add(ingredient)
    db.flush()  # assigns ingredient.id without committing the outer transaction

    return ingredient