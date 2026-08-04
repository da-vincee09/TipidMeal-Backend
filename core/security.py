from datetime import datetime, timezone
from jose import JWTError, jwt
from core.config import settings

def verify_supabase_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={
                "verify_aud": False
            }
        )

        return payload

    except JWTError:
        return None

def get_user_id_from_token(token: str):
    payload = verify_supabase_token(token)

    if not payload:
        return None

    user_id = payload.get("sub")

    return user_id