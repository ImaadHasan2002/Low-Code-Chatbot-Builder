from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer

from .config import get_settings
from ..models.user import UserInDB
from ..models.workspace import Workspace
from ..services.auth_service import AuthService
from ..services.workspace_service import WorkspaceService

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt

async def get_current_user(request: Request) -> UserInDB:
    print(f"Getting current user...")
    print(f"Getting cookies: {request.cookies}")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = request.cookies.get("access_token")
    if not token:
        raise credentials_exception
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    auth_service = AuthService()
    user = await auth_service.get_user_by_email(email)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_workspace(request: Request) -> Workspace:
    workspace_id = request.cookies.get("workspace_id")
    if not workspace_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate workspace credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    workspace_service = WorkspaceService()
    workspace = await workspace_service.get_workspace_by_id(workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Workspace not found",
        )
    return workspace

async def get_current_workspace_id(request: Request) -> str:
    workspace_id = request.cookies.get("workspace_id")
    if not workspace_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate workspace credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    workspace_service = WorkspaceService()
    workspace = await workspace_service.get_workspace_by_id(workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Workspace not found",
        )
    return workspace_id

