from ninja import Schema
from pydantic import UUID4


class MessageOut(Schema):
    message: str


class Token(Schema):
    access_token: str
    token_type: str


class UUIDSchema(Schema):
    id: UUID4


class TokenAuth(Schema):
    id: str
    exp: str
    sub: str


class Paginated(Schema):
    total_count: int
    per_page: int
    from_record: int
    to_record: int
    previous_page: int
    current_page: int
    next_page: int
    page_count: int
