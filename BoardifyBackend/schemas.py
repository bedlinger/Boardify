from models import *


class UserBase(SQLModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: uuid.UUID


class Token(SQLModel):
    access_token: str
    token_type: str


class TagPublic(TagBase):
    pass


class TagCreate(SQLModel):
    nr: int
    name: str


class TicketTagInfo(SQLModel):
    nr: int


class TicketPublic(TicketBase):
    tags: list[TagPublic] = []


class TicketCreate(SQLModel):
    stage_nr: int = 0
    title: str
    description: str
    due_at: datetime | None = None
    tag_nrs: list[int] = []


class TicketUpdate(SQLModel):
    stage_nr: int | None = None
    title: str | None = None
    description: str | None = None
    due_at: datetime | None = None
    tag_nrs: list[int] | None = None


class StagePublic(StageBase):
    pass


class BoardPublic(BoardBase):
    tickets: list[TicketPublic] = []
    stages: list[StagePublic]
    tags: list[TagPublic] = []


class BoardOverview(BoardBase):
    tickets_count: int
    done_tickets_count: int


class BoardCreate(BoardBase):
    stages: list[StagePublic]
    tags: list[TagCreate] = []


class BoardUpdate(SQLModel):
    name: str
