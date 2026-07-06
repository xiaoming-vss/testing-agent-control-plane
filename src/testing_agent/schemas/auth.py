from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RegisterRequest(BaseModel):
    name: str
    password: str
    email: str = ""


class LoginRequest(BaseModel):
    name: str
    password: str


class UserResponse(BaseModel):
    user_id: str = Field(alias="userId")
    name: str
    email: str = ""

    model_config = ConfigDict(populate_by_name=True)


class LoginResponse(BaseModel):
    access_token: str = Field(alias="accessToken")
    model_config = ConfigDict(populate_by_name=True)


class UpdateProfileRequest(BaseModel):
    name: str | None = None
    email: str | None = None
