from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.dependencies import get_db
from features.meals import service
from features.meals.schemas import (
    MealCreate,
    MealIngredientCreate,
    MealIngredientResponse,
    MealInstructionCreate,
    MealInstructionResponse,
    MealListResponse,
    MealResponse,
    IngredientSuggestionResponse,
)
from fastapi import Query

router = APIRouter(
    prefix="/meals",
    tags=["Meals"],
)

@router.post(
    "",
    response_model=MealResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_meal(
    meal_data: MealCreate,
    db: Session = Depends(get_db),
):

    return service.create_meal(
        db,
        meal_data,
    )


@router.post(
    "/{meal_id}/ingredients",
    response_model=MealIngredientResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_meal_ingredient(
    meal_id: UUID,
    ingredient_data: MealIngredientCreate,
    db: Session = Depends(get_db),
):
    return service.create_meal_ingredient(
        db,
        meal_id,
        ingredient_data.ingredient,
        ingredient_data.quantity,
        ingredient_data.unit,
        ingredient_data.is_optional,
    )


@router.post(
    "/{meal_id}/instructions",
    response_model=MealInstructionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_meal_instruction(
    meal_id: UUID,
    instruction_data: MealInstructionCreate,
    db: Session = Depends(get_db),
):
    return service.create_meal_instruction(
        db,
        meal_id,
        instruction_data.step_number,
        instruction_data.instruction,
    )


@router.get(
    "",
    response_model=MealListResponse,
)
def get_meals(
    db: Session = Depends(get_db),
):

    meals = service.get_meals(
        db,
    )

    return {
        "meals": meals,
    }


@router.get(
    "/ingredients/suggestions",
    response_model=list[IngredientSuggestionResponse],
)
def get_ingredient_suggestions(
    search: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    return service.get_ingredient_suggestions(
        db,
        search,
    )


@router.get(
    "/units",
    response_model=list[str],
)
def get_all_units(
    db: Session = Depends(get_db),
):
    return service.get_all_units(db)


@router.get(
    "/{meal_id}",
    response_model=MealResponse,
)
def get_meal(
    meal_id: UUID,
    db: Session = Depends(get_db),
):

    meal = service.get_meal_by_id(
        db,
        meal_id,
    )

    if meal is None:
        raise HTTPException(
            status_code=404,
            detail="Meal not found",
        )

    return meal