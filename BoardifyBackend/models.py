from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship
import uuid


class TicketTagLink(SQLModel, table=True):
    ticket_id: uuid.UUID = Field(foreign_key="ticket.id", primary_key=True)
    tag_board_id: uuid.UUID = Field(foreign_key="tag.board_id", primary_key=True)
    tag_nr: int = Field(foreign_key="tag.nr", primary_key=True)

    ticket: "Ticket" = Relationship(back_populates="tag_links")
    tag: "Tag" = Relationship(back_populates="ticket_links")


class TagBase(SQLModel):
    nr: int = Field(primary_key=True)
    name: str = Field()


class Tag(TagBase, table=True):
    board_id: uuid.UUID = Field(primary_key=True, foreign_key="board.id")
    board: "Board" = Relationship(back_populates="tags")
    ticket_links: list["TicketTagLink"] = Relationship(back_populates="tag")


class TicketBase(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    stage_nr: int = Field()
    is_done: bool = False
    title: str = Field()
    description: str = Field()
    created_at: datetime = Field(default_factory=datetime.now)
    due_at: datetime | None = Field(default=None)


class Ticket(TicketBase, table=True):
    board_id: uuid.UUID | None = Field(default=None, foreign_key="board.id")
    board: "Board" = Relationship(back_populates="tickets")
    tag_links: list["TicketTagLink"] = Relationship(back_populates="ticket",
                                                    sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class StageBase(SQLModel):
    nr: int = Field(primary_key=True)
    name: str = Field()


class Stage(StageBase, table=True):
    board_id: uuid.UUID = Field(primary_key=True, foreign_key="board.id")
    board: "Board" = Relationship(back_populates="stages")


class BoardBase(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field()


class Board(BoardBase, table=True):
    tickets: list[Ticket] = Relationship(back_populates="board", cascade_delete=True)
    stages: list[Stage] = Relationship(back_populates="board", cascade_delete=True)
    tags: list[Tag] = Relationship(back_populates="board", cascade_delete=True)
