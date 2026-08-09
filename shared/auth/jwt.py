from jose import jwt, JWTError
import requests

from core.config import settings

JWKS_URL=(
        f"{settings.SUPABASE_URL}"
        "/auth/v1/.well-known/jwks.json"
    )

def verify_supabase_token(token: str) -> dict | None:
    try:
        header = jwt.get_unverified_header(token)

        kid = header.get("kid")

        if not kid:
            return None

        response = requests.get(JWKS_URL, timeout=5)
        response.raise_for_status()

        jwks = response.json()

        signing_key = next(
            (
                key
                for key in jwks["keys"]
                if key.get("kid") == kid
            ),
            None,
        )

        if not signing_key:
            return None

        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["ES256"],
            audience="authenticated",
            options={
                "verify_iss": False,
            },
        )

        return payload

    except (JWTError, requests.RequestException, KeyError):
        return None

