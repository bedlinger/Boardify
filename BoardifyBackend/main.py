from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import func, delete
from sqlmodel import Session, select

from database import create_db_and_tables, get_session
from schemas import *

app = FastAPI()

DbSession = Annotated[Session, Depends(get_session)]


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/boards", response_model=list[BoardOverview])
async def read_boards(session: DbSession):
    results = session.exec(
        select(
            Board,
            func.count(Ticket.id).label("total_tickets"),
            func.count(func.nullif(Ticket.is_done, False)).label("done_tickets")
        )
        .join(Ticket, isouter=True)
        .group_by(Board.id)
    ).all()

    boards = []
    for board, total_tickets, done_tickets in results:
        board_data = BoardOverview(**board.model_dump(), tickets_count=total_tickets, done_tickets_count=done_tickets)
        boards.append(board_data)

    return boards


@app.get("/boards/{board_id}", response_model=BoardPublic)
async def read_board(board_id: uuid.UUID, session: DbSession):
    board = session.get(Board, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board


@app.post("/boards", response_model=BoardPublic)
def create_board(board: BoardCreate, session: DbSession):
    db_board = Board(**board.model_dump(exclude={'stages', 'tags'}))
    db_board.stages = [Stage(**stage.model_dump(), board_id=db_board.id) for stage in board.stages]
    db_board.tags = [Tag(**tag.model_dump(), board_id=db_board.id) for tag in board.tags]
    session.add(db_board)
    session.commit()
    session.refresh(db_board)
    return db_board


@app.patch("/boards/{board_id}", response_model=BoardPublic)
def update_board(board_id: uuid.UUID, board: BoardUpdate, session: DbSession):
    board_db = session.get(Board, board_id)
    if not board_db:
        raise HTTPException(status_code=404, detail="Ticket not found")
    board_data = board.model_dump(exclude_unset=True)
    board_db.sqlmodel_update(board_data)
    session.add(board_db)
    session.commit()
    session.refresh(board_db)
    return board_db


@app.delete("/boards/{board_id}")
def delete_board(board_id: uuid.UUID, session: DbSession):
    board = session.get(Board, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    session.delete(board)
    session.commit()
    return {}


@app.post("/tickets", response_model=TicketPublic)
def create_ticket(board_id: uuid.UUID, ticket: TicketCreate, session: DbSession):
    # Create ticket without tags
    ticket_data = ticket.model_dump(exclude={"tags"})
    db_ticket = Ticket(**ticket_data)
    db_board = session.get(Board, board_id)
    if not db_board:
        raise HTTPException(status_code=404, detail="Board not found")

    db_ticket.is_done = ticket.stage_nr == max([s.nr for s in db_board.stages])
    db_ticket.board_id = board_id
    session.add(db_ticket)
    session.flush()

    for tag_nr in ticket.tags:
        tag = session.exec(select(Tag).where(
            Tag.board_id == board_id,
            Tag.nr == tag_nr
        )).first()
        if tag:
            link = TicketTagLink(
                ticket_id=db_ticket.id,
                tag_board_id=board_id,
                tag_nr=tag_nr
            )
            session.add(link)

    session.commit()
    session.refresh(db_ticket)
    return db_ticket


@app.patch("/tickets/{ticket_id}", response_model=TicketPublic)
def update_ticket(ticket_id: uuid.UUID, ticket: TicketUpdate, session: DbSession):
    db_ticket = session.get(Ticket, ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket.stage_nr:
        db_ticket.is_done = ticket.stage_nr == max([s.nr for s in db_ticket.board.stages])

    ticket_data = ticket.model_dump(exclude_unset=True, exclude_none=True, exclude={"tags"})
    db_ticket.sqlmodel_update(ticket_data)

    if ticket.tags is not None:
        session.exec(delete(TicketTagLink).where(TicketTagLink.ticket_id == ticket_id))

        for tag_nr in ticket.tags:
            tag = session.exec(select(Tag).where(
                Tag.board_id == db_ticket.board_id,
                Tag.nr == tag_nr
            )).first()
            if tag:
                link = TicketTagLink(
                    ticket_id=db_ticket.id,
                    tag_board_id=db_ticket.board_id,
                    tag_nr=tag_nr
                )
                session.add(link)

    session.add(db_ticket)
    session.commit()
    session.refresh(db_ticket)
    return db_ticket


@app.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: uuid.UUID, session: DbSession):
    ticket_db = session.get(Ticket, ticket_id)
    if not ticket_db:
        raise HTTPException(status_code=404, detail="Ticket not found")
    session.delete(ticket_db)
    session.commit()
    return {}
