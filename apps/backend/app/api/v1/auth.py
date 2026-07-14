from fastapi import APIRouter, HTTPException, status, Response
from datetime import timedelta
from typing import Any

from ...core.config import get_settings
from ...models.user import UserCreate
from ...services.auth_service import AuthService
from ...core.security import create_access_token
from ...services.workspace_service import WorkspaceService

router = APIRouter()
settings = get_settings()

@router.post("/signup", response_model=dict)
async def signup(user: UserCreate) -> Any:
    auth_service = AuthService()
    existing_user = await auth_service.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    await auth_service.create_user(user)
    return {"message": "User created successfully"}

@router.post("/login")
async def login(response: Response, credentials: dict) -> Any:
    auth_service = AuthService()
    workspace_service = WorkspaceService()
    user = await auth_service.authenticate_user(credentials["email"], credentials["password"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    # Set secure cookie with the access token
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=not settings.DEBUG,  # secure cookies outside local development
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/"
    )

    # Get user's workspaces
    workspaces = await workspace_service.get_workspace_by_user_id(user.id)
    if workspaces and len(workspaces) > 0:
        workspace = workspaces[0]
        response.set_cookie(
            key="workspace_id",
            value=str(workspace.id),
            httponly=True,
            secure=not settings.DEBUG,
            samesite="lax",
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            path="/"
        )

    return {"message": "Login successful"}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("workspace_id")
    return {"message": "Logged out successfully"}
