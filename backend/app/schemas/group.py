from __future__ import annotations
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.group import GroupRole


class GroupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class GroupUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)


class GroupMemberOut(BaseModel):
    user_id:   UUID
    user_name: str | None = None
    role:      GroupRole
    joined_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_member(cls, member):
        return cls(
            user_id=member.user_id,
            user_name=member.user.name if member.user else None,
            role=member.role,
            joined_at=member.joined_at,
        )


class GroupMemberAdd(BaseModel):
    user_id: UUID
    role:    GroupRole = GroupRole.viewer


class GroupOut(BaseModel):
    id:         UUID
    name:       str
    creator_id: UUID
    created_at: datetime
    members:    list[GroupMemberOut] = []

    model_config = {"from_attributes": True}
