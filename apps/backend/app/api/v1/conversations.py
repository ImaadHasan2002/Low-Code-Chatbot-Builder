from datetime import datetime, timedelta
from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from ...core.security import get_current_user
from ...models.conversation import Conversation
from ...models.user import UserInDB

router = APIRouter()


def _require_object_id(value: str, label: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid {label}"
        )
    return ObjectId(value)


class ConversationOut(BaseModel):
    id: str
    workspace_id: str
    query: str
    response: str
    feedback: Optional[str] = None
    created_at: datetime


@router.get("/", response_model=List[ConversationOut])
async def list_conversations(
    workspace_id: str = Query(...),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=200),
    current_user: UserInDB = Depends(get_current_user),
) -> List[ConversationOut]:
    ws_oid = _require_object_id(workspace_id, "workspace id")
    convs = (
        await Conversation.find(Conversation.workspace_id == ws_oid)
        .sort("-created_at")
        .skip(skip)
        .limit(limit)
        .to_list()
    )
    return [
        ConversationOut(
            id=str(c.id),
            workspace_id=str(c.workspace_id),
            query=c.query,
            response=c.response,
            feedback=c.feedback,
            created_at=c.created_at,
        )
        for c in convs
    ]


@router.get("/stats")
async def conversation_stats(
    workspace_id: str = Query(...),
    current_user: UserInDB = Depends(get_current_user),
) -> dict:
    ws_oid = _require_object_id(workspace_id, "workspace id")
    all_convs = await Conversation.find(
        Conversation.workspace_id == ws_oid
    ).to_list()

    total = len(all_convs)
    today = datetime.now().date()

    daily_map: dict = {}
    for i in range(7):
        day = (today - timedelta(days=6 - i)).isoformat()
        daily_map[day] = 0

    this_week = 0
    last_week = 0

    for conv in all_convs:
        day = conv.created_at.date()
        days_ago = (today - day).days
        day_str = day.isoformat()
        if days_ago < 7:
            this_week += 1
            if day_str in daily_map:
                daily_map[day_str] += 1
        elif days_ago < 14:
            last_week += 1

    last_7_days = [{"date": d, "count": c} for d, c in daily_map.items()]

    return {
        "total": total,
        "last_7_days": last_7_days,
        "this_week": this_week,
        "last_week": last_week,
    }
