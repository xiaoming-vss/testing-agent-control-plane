from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel, ConfigDict

DataT = TypeVar("DataT")


class ApiResponse[DataT](BaseModel):
    code: int = 0
    message: str = "ok"
    data: DataT


class ListResponse[DataT](BaseModel):
    total: int = 0
    items: list[DataT]


class EmptyData(BaseModel):
    model_config = ConfigDict(extra="forbid")


class MessageData(BaseModel):
    message: str


class StatusData(BaseModel):
    status: str


class UrlData(BaseModel):
    url: str
