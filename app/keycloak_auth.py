import os
import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError
import logging

logger = logging.getLogger("qa-practice")

KEYCLOAK_ISSUER = "http://localhost:8080/realms/qa-practice"
JWKS_URL = f"{KEYCLOAK_ISSUER}/protocol/openid-connect/certs"

jwks_client = PyJWKClient(JWKS_URL)

security = HTTPBearer(auto_error=False)

def verify_token(token: str):
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)


        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=KEYCLOAK_ISSUER,
            audience="qa-practice-api",
        )

        return payload

    except (InvalidTokenError, jwt.PyJWKClientError) as error:
        logger.error(f"{error}")
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        ) from error

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return verify_token(credentials.credentials)

def require_role(required_role: str):
    def role_checker(user: dict = Depends(get_current_user)):
        roles = user.get("realm_access", {}).get("roles", [])

        if required_role not in roles:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions"
            )
        return user

    return role_checker