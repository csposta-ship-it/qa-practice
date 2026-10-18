from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from app.security_utils import mask_sensitive_data
from app.database import create_user, init_db, write_audit_log
from app.logging_config import configure_logging
from typing import Literal
import time
import uuid
import sqlite3
import logging
import json

FORBIDDEN_USERNAMES = {
    "admin",
    "administrator",
    "root",
}

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    type: Literal["BUSINESS", "RETAIL"]
    company_name: str | None = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if value != value.strip():
            raise ValueError(
                "Username must not start or end with whitespace"
        )

        normalized = value.lower()

        if normalized in FORBIDDEN_USERNAMES:
            raise ValueError("This username is not allowed")

        return normalized

    @model_validator(mode="after")
    def validate_company_name(self):
        if self.type == "BUSINESS" and (
            not self.company_name or not self.company_name.strip()
        ):
            raise ValueError("Company name is required for BUSINESS users")

        if self.type == "RETAIL" and self.company_name is not None:

            raise ValueError("Company name is not allowed for RETAIL users")

        return self

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = configure_logging()
    logger.info("Application startup")

    init_db()
    yield

    logger.info("Application shutdown")

app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def log_http_request(request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()
    logger = logging.getLogger("qa_practice")

    # A request body beolvasása
    body = await request.body()
    request_data = None

    if body:
        try:
            parsed_body = json.loads(body)
            request_data = mask_sensitive_data(parsed_body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            request_data = {"body": "[non-JSON body]"}

    logger.info(
        "HTTP request started: request_id=%s method=%s path=%s",
        request_id,
        request.method,
        request.url.path,
    )

    try:
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000

        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk

        response_data = None
        if response_body:
            try:
                response_data = json.loads(response_body)
                response_data = mask_sensitive_data(response_data)
            except (json.JSONDecodeError, UnicodeDecodeError):
                response_data = {"body": "[non-JSON response]"}

        logger.info(
            "HTTP request completed: request_id=%s method=%s "
            "path=%s status=%s duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        response.headers["X-Request-ID"] = request_id

        # Csak a regisztráció üzleti eseményeit írjuk az auditlogba
        
        if request.method == "POST" and request.url.path == "/users":
            success = 200 <= response.status_code < 300

            user_id = None
            if isinstance(response_data, dict):
                user_id = response_data.get("id")

            write_audit_log(
                event_type="USER_REGISTRATION",
                details="SUCCESS" if success else "FAILED",
                user_id=user_id,
                request_id=request_id,
                request_data=json.dumps(request_data),
                response_data=json.dumps({
                    "status_code": response.status_code,
                    "body": response_data,
                }),
            )


        from starlette.responses import Response

        return Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

    except Exception:
        logger.exception(
            "HTTP request failed: request_id=%s method=%s path=%s",
            request_id,
            request.method,
            request.url.path,
        )
        raise

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/users", status_code=201)
def register_user(user: UserCreate):
    logger = logging.getLogger("qa_practice")
    try:
        result = create_user(
            username=user.username,
            email=str(user.email),
            password=user.password,
            user_type=user.type,
            company_name=user.company_name
        )

        logger.info(
            "User registered successfully: user_id=%s",
            result["id"],
        )
        return result
    
    except sqlite3.IntegrityError as error:
        logger.warning(
            "User registration failed: username or email already exists"
        )
        raise HTTPException(
            status_code=409,
            detail="Username or email already exists",
        ) from error