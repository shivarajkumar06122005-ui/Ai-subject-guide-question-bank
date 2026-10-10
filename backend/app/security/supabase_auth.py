import os
from pathlib import Path

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from jwt.exceptions import InvalidTokenError, PyJWKClientError
from supabase import Client, create_client

load_dotenv(Path(__file__).resolve().parents[3] / ".env", override=False)

SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_ISSUER = f"{SUPABASE_URL}/auth/v1"
JWKS_URL = f"{SUPABASE_ISSUER}/.well-known/jwks.json"

jwks_client = PyJWKClient(JWKS_URL) if SUPABASE_URL else None
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, str]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not SUPABASE_URL or jwks_client is None:
        raise HTTPException(
            status_code=500,
            detail="Supabase authentication is not configured.",
        )

    token = credentials.credentials

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except PyJWKClientError as exc:
        raise HTTPException(
            status_code=503,
            detail="Unable to retrieve the trusted authentication signing key.",
        ) from exc

    try:
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated",
            issuer=SUPABASE_ISSUER,
            options={"require": ["exp", "sub", "iss", "aud"]},
        )
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user_id = payload.get("sub")
    if not isinstance(user_id, str) or not user_id:
        raise HTTPException(status_code=401, detail="Invalid user identity.")

    return {"id": user_id, "access_token": token}


def get_user_supabase(
    current_user: dict[str, str] = Depends(get_current_user),
) -> Client:
    if not SUPABASE_KEY:
        raise HTTPException(
            status_code=500,
            detail="Supabase database configuration is missing.",
        )

    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    client.postgrest.auth(current_user["access_token"])
    return client

