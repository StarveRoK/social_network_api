from pydantic import BaseModel, conint, constr
from typing import Optional


TELEGRAM_ID_REGEX = r'^[0-9]{5,}$'
VIN_REGEX = r'^[A-HJ-NPR-Z0-9]{17}$'


class DataBaseStateModel(BaseModel):
    chat_id: Optional[str | None] = None
    key: Optional[str | None] = None
    value: Optional[str | list | None] = None
    vin: Optional[str | list | None] = None
    trucks_list: Optional[list | None] = None
    statuses: Optional[list | None] = None
    timing_values: Optional[dict | list | None] = None
    name: Optional[str | None] = None
    func_message_id: Optional[conint(ge=0) | None] = None
    is_inline_button_enabled: Optional[bool | None] = None


class DataBaseStateModelTgId(BaseModel):
    tg_id: conint(ge=0)


class User(BaseModel):
    id: int
    telegram_id: Optional[conint(ge=0)] = None
    authentication: Optional[bool] = None
    selected_trucks: Optional[list] = None
    price_n: Optional[bool] = None
    status_n: Optional[bool] = None
    all_n: Optional[bool] = None
    role_id: Optional[conint(ge=0)] = None
    name: Optional[str] = None
    on_line: Optional[bool] = None
    state: Optional[dict] = None


class Trucks(BaseModel):
    id: Optional[int] = None
    vin: Optional[constr(pattern=VIN_REGEX)] = None
    name: Optional[str] = None
    price: Optional[int] = None
    status: Optional[int] = None


class TelegramRoles(BaseModel):
    id: Optional[int] = None
    code: Optional[str] = None
    name: Optional[str] = None


class Status(BaseModel):
    id: Optional[int] = None
    code: Optional[str] = None
    name: Optional[str] = None


class ChatStatus(BaseModel):
    id: Optional[int] = None
    code: Optional[str] = None
    name: Optional[str] = None


class Images(BaseModel):
    id: Optional[int] = None
    trucks_id: Optional[int] = None
    url: Optional[str] = None
    code: Optional[str] = None


class ChatWithManager(BaseModel):
    id: Optional[int] = None
    user_tg_id: Optional[conint(ge=0)] = None
    manager_tg_id: Optional[conint(ge=0)] = None
    user_name: Optional[str] = None
    question: Optional[str] = None
    unique_chat_id: Optional[str] = None
    status: Optional[int] = None


class ChatWithManagerHistory(BaseModel):
    id: Optional[int] = None
    user_message: Optional[str] = None
    manager_message: Optional[str] = None
    chat_id: Optional[str] = None


__all__ = ['DataBaseStateModel', 'DataBaseStateModelTgId', 'User', 'Trucks', 'TelegramRoles', 'Status', 'ChatStatus',
           'Images', 'ChatWithManager', 'ChatWithManagerHistory']
