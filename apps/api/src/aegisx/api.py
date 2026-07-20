from collections.abc import Awaitable, Callable
from typing import Annotated, Literal
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from redis import Redis
from redis.exceptions import RedisError
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError

from .auth import SqlRefreshTokenStore, authenticate_user
from .config import Settings, get_settings
from .database import Database
from .models import Membership, MembershipRole, Permission, RolePermission
from .observability import RequestTelemetryMiddleware, configure_logging
from .security.passwords import PasswordHasher
from .security.tokens import AccessTokenCodec, RefreshTokenService, TokenError

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
}


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=1024)
    organization_id: UUID


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"  # noqa: S105 - OAuth token type, not a secret


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or get_settings()
    configure_logging()
    database = Database(config.database_url)
    cache = Redis.from_url(config.redis_url, decode_responses=False)
    codec = AccessTokenCodec(config.token_signing_key.encode(), "aegisx", "aegisx-api")
    tokens = RefreshTokenService(
        codec, SqlRefreshTokenStore(database.sessions), config.token_hash_key.encode()
    )
    app = FastAPI(
        title="AegisX API",
        version="0.1.0",
        docs_url=None if config.environment == "production" else "/docs",
    )
    app.state.database, app.state.cache = database, cache
    app.add_middleware(RequestTelemetryMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-Correlation-ID"],
    )

    @app.middleware("http")
    async def security_headers(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers.update(SECURITY_HEADERS)
        return response

    @app.get("/health/live", tags=["health"])
    def live() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/auth/login", response_model=TokenResponse, tags=["authentication"])
    def login(credentials: LoginRequest) -> TokenResponse:
        try:
            subject, permissions = authenticate_user(
                database.sessions,
                PasswordHasher(),
                str(credentials.email),
                credentials.password,
                credentials.organization_id,
            )
            pair = tokens.issue(subject, credentials.organization_id, permissions)
        except TokenError as exc:
            raise HTTPException(status_code=401, detail="invalid credentials") from exc
        return TokenResponse(access_token=pair.access_token, refresh_token=pair.refresh_token)

    @app.post("/v1/auth/refresh", response_model=TokenResponse, tags=["authentication"])
    def refresh(credentials: RefreshRequest) -> TokenResponse:
        try:
            subject, organization_id = tokens.identity(credentials.refresh_token)
            with database.sessions() as session:
                membership = session.scalar(
                    select(Membership).where(
                        Membership.organization_id == organization_id,
                        Membership.user_id == subject,
                        Membership.status == "active",
                    )
                )
                if membership is None:
                    raise TokenError("invalid refresh token")
                names = session.scalars(
                    select(Permission.name)
                    .join(RolePermission, RolePermission.permission_id == Permission.id)
                    .join(
                        MembershipRole,
                        (MembershipRole.role_id == RolePermission.role_id)
                        & (MembershipRole.organization_id == RolePermission.organization_id),
                    )
                    .where(
                        MembershipRole.organization_id == organization_id,
                        MembershipRole.membership_id == membership.id,
                    )
                )
                permissions = frozenset(names)
            pair = tokens.rotate(credentials.refresh_token, permissions)
        except TokenError as exc:
            raise HTTPException(status_code=401, detail="invalid refresh token") from exc
        return TokenResponse(access_token=pair.access_token, refresh_token=pair.refresh_token)

    @app.post("/v1/auth/logout", status_code=204, tags=["authentication"])
    def logout(credentials: RefreshRequest) -> Response:
        tokens.revoke(credentials.refresh_token)
        return Response(status_code=204)

    def db() -> Database:
        return database

    @app.get("/health/ready", tags=["health"])
    def ready(database_dependency: Annotated[Database, Depends(db)]) -> dict[str, str]:
        try:
            with database_dependency.sessions() as session:
                session.execute(text("SELECT 1"))
            app.state.cache.ping()
        except (SQLAlchemyError, RedisError, OSError) as exc:
            raise HTTPException(status_code=503, detail="dependencies unavailable") from exc
        return {"status": "ready"}

    @app.get("/metrics", include_in_schema=False)
    def metrics() -> Response:
        lines = ["# TYPE aegisx_http_responses_total counter"]
        lines.extend(
            f'aegisx_http_responses_total{{status="{key.removeprefix("http_")}"}} {value}'
            for key, value in sorted(RequestTelemetryMiddleware.counters.items())
        )
        return Response("\n".join(lines) + "\n", media_type="text/plain; version=0.0.4")

    return app


app = create_app()
