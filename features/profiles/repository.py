from uuid import UUID

from sqlalchemy.orm import Session

from features.profiles.models import Profile
from features.profiles.schemas import ProfileCreate, ProfileUpdate

def create_profile(
    db: Session,
    profile_data: ProfileCreate,
    auth_id: UUID
) -> Profile:
    profile = Profile(
        auth_id=auth_id,
        **profile_data.model_dump(),
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile


def get_profile_by_auth_id(
    db: Session,
    auth_id: UUID
) -> Profile | None:

    return(
        db.query(Profile).filter(
            Profile.auth_id == auth_id
        ).first()
    )


def update_profile(
    db: Session,
    profile: Profile,
    profile_data: ProfileUpdate
) -> Profile:

    update_data = profile_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)

    return profile