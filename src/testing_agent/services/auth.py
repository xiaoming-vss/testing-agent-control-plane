from __future__ import annotations

from testing_agent.core.errors import (
    ErrForbidden,
    ErrNameAlreadyUse,
    ErrNotFound,
    ErrUnauthorized,
)
from testing_agent.core.security import create_access_token, hash_password, verify_password
from testing_agent.core.sid import new_id
from testing_agent.models.user import User
from testing_agent.repositories.user import UserRepository
from testing_agent.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UpdateProfileRequest,
    UserResponse,
)


class AuthService:
    def __init__(self, users: UserRepository):
        self.users = users

    async def register(self, body: RegisterRequest) -> dict:
        exists = await self.users.get_by_name(body.name)
        if exists is not None:
            raise ErrNameAlreadyUse
        user = User(
            user_id=new_id(),
            nickname=body.name,
            password=hash_password(body.password),
            email=body.email,
        )
        self.users.add(user)
        await self.users.commit()
        await self.users.refresh(user)
        return self._user_data(user)

    async def login(self, body: LoginRequest) -> dict:
        user = await self.users.get_by_name(body.name)
        if user is None or not verify_password(body.password, user.password):
            raise ErrUnauthorized
        data = LoginResponse(access_token=create_access_token(user.user_id))
        return data.model_dump(by_alias=True)

    async def get_profile(self, user_id: str) -> dict:
        user = await self.users.get_by_user_id(user_id)
        if user is None:
            raise ErrNotFound
        return self._user_data(user)

    async def update_profile(self, user_id: str, body: UpdateProfileRequest) -> dict:
        user = await self.users.get_by_user_id(user_id)
        if user is None:
            raise ErrForbidden
        if body.name is not None and body.name != user.nickname:
            exists = await self.users.get_by_name(body.name)
            if exists is not None:
                raise ErrNameAlreadyUse
            user.nickname = body.name
        if body.email is not None:
            user.email = body.email
        await self.users.commit()
        await self.users.refresh(user)
        return self._user_data(user)

    async def delete_user(self, user_id: str) -> dict:
        user = await self.users.get_by_user_id(user_id)
        if user is None:
            raise ErrForbidden
        await self.users.delete(user)
        await self.users.commit()
        return {}

    def _user_data(self, user: User) -> dict:
        return UserResponse(
            user_id=user.user_id,
            name=user.nickname,
            email=user.email,
        ).model_dump(by_alias=True)
