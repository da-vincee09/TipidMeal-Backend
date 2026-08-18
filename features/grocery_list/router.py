from datetime import date, timedelta
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from core.dependencies import get_db
from shared.auth.dependencies import get_current_user

from features.grocery_list import service
from features.grocery_list.schemas import (
    GroceryListResponse,
)

from features.profiles import (
    service as profile_service,
)


router = APIRouter(
    prefix="/grocery-list",
    tags=["Grocery List"],
)


@router.get(
    "",
    response_model=GroceryListResponse,
)
def get_grocery_list(
    start_date: date | None = Query(
        default=None,
    ),
    end_date: date | None = Query(
        default=None,
    ),
    current_user: UUID = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
):
    profile = profile_service.get_profile_by_auth_id(
        db,
        current_user,
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    today = date.today()

    # Default to current week: Monday -> Sunday
    if start_date is None and end_date is None:
        start_date = (
            today
            - timedelta(days=today.weekday())
        )

        end_date = (
            start_date
            + timedelta(days=6)
        )

    elif start_date is None:
        start_date = (
            end_date
            - timedelta(days=6)
        )

    elif end_date is None:
        end_date = (
            start_date
            + timedelta(days=6)
        )

    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "start_date must be before "
                "or equal to end_date"
            ),
        )

    return service.get_grocery_list(
        db,
        profile.id,
        start_date,
        end_date,
    )