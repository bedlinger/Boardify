from models import *


class TicketPublic(TicketBase):
    pass


class TicketCreate(SQLModel):
    stage_nr: int = 0
    title: str
    description: str
    due_at: datetime | None = None


class TicketStageUpdate(SQLModel):
    stage_nr: int


class StagePublic(StageBase):
    pass


class BoardPublic(BoardBase):
    tickets: list[TicketPublic] = []
    stages: list[StagePublic]


class BoardOverview(BoardBase):
    tickets_count: int
    done_tickets_count: int


class BoardCreate(BoardBase):
    stages: list[StagePublic]
