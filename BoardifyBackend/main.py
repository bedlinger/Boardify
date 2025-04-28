import os
from datetime import timedelta
from typing import Annotated

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import func, delete
from sqlmodel import Session, select

from auth import (get_password_hash, verify_password, create_access_token, get_current_user,
                  ACCESS_TOKEN_EXPIRE_MINUTES)
from database import create_db_and_tables, get_session
from schemas import *

app = FastAPI()

DbSession = Annotated[Session, Depends(get_session)]


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    load_dotenv()


@app.post("/users/register", response_model=UserResponse)
async def register(user: UserCredentials, session: DbSession):
    is_registration_disabled = os.getenv("DISABLE_REGISTRATION", "false").lower() == "true"
    if is_registration_disabled:
        raise HTTPException(status_code=403, detail="Registration is disabled")
    db_user = session.exec(select(User).where(User.username == user.username)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@app.post("/users/login", response_model=Token)
async def login(credentials: UserCredentials, session: DbSession):
    user = session.exec(select(User).where(User.username == credentials.username)).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}, )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@app.get("/boards", response_model=list[BoardOverview])
async def read_boards(session: DbSession,
                  current_user: Annotated[User, Depends(get_current_user)]):
    results = session.exec(select(Board, func.count(Ticket.id).label("total_tickets"),
                                  func.count(func.nullif(Ticket.is_done, False)).label("done_tickets")).join(Ticket,
                                                                                                             isouter=True).group_by(
        Board.id)).all()

    boards = []
    for board, total_tickets, done_tickets in results:
        board_data = BoardOverview(**board.model_dump(), tickets_count=total_tickets, done_tickets_count=done_tickets)
        boards.append(board_data)

    return boards


@app.get("/boards/{board_id}", response_model=BoardPublic)
async def read_board(board_id: uuid.UUID, session: DbSession,
                  current_user: Annotated[User, Depends(get_current_user)]):
    board = session.get(Board, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board


@app.post("/boards", response_model=BoardPublic)
def create_board(board: BoardCreate, session: DbSession, current_user: Annotated[User, Depends(get_current_user)]):
    db_board = Board(**board.model_dump(exclude={'stages', 'tags'}))
    db_board.stages = [Stage(**stage.model_dump(), board_id=db_board.id) for stage in board.stages]
    db_board.tags = [Tag(**tag.model_dump(), board_id=db_board.id) for tag in board.tags]
    session.add(db_board)
    session.commit()
    session.refresh(db_board)
    return db_board


@app.patch("/boards/{board_id}", response_model=BoardPublic)
def update_board(board_id: uuid.UUID, board: BoardUpdate, session: DbSession,
                 current_user: Annotated[User, Depends(get_current_user)]):
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
def delete_board(board_id: uuid.UUID, session: DbSession, current_user: Annotated[User, Depends(get_current_user)]):
    board = session.get(Board, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    session.delete(board)
    session.commit()
    return {}


@app.post("/tickets", response_model=TicketPublic)
def create_ticket(board_id: uuid.UUID, ticket: TicketCreate, session: DbSession,
                  current_user: Annotated[User, Depends(get_current_user)]):
    ticket_data = ticket.model_dump(exclude={"tag_nrs"})
    db_ticket = Ticket(**ticket_data)
    db_board = session.get(Board, board_id)
    if not db_board:
        raise HTTPException(status_code=404, detail="Board not found")

    db_ticket.is_done = ticket.stage_nr == max([s.nr for s in db_board.stages])
    db_ticket.board_id = board_id
    session.add(db_ticket)
    session.flush()

    for tag_nr in ticket.tag_nrs:
        tag = session.exec(select(Tag).where(Tag.board_id == board_id, Tag.nr == tag_nr)).first()
        if tag:
            link = TicketTagLink(ticket_id=db_ticket.id, tag_board_id=board_id, tag_nr=tag_nr)
            session.add(link)

    session.commit()
    session.refresh(db_ticket)
    return db_ticket


@app.patch("/tickets/{ticket_id}", response_model=TicketPublic)
def update_ticket(ticket_id: uuid.UUID, ticket: TicketUpdate, session: DbSession,
                  current_user: Annotated[User, Depends(get_current_user)]):
    db_ticket = session.get(Ticket, ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket.stage_nr:
        db_ticket.is_done = ticket.stage_nr == max([s.nr for s in db_ticket.board.stages])

    ticket_data = ticket.model_dump(exclude_unset=True, exclude_none=True, exclude={"tag_nrs"})
    db_ticket.sqlmodel_update(ticket_data)

    if ticket.tag_nrs is not None and len(ticket.tag_nrs) > 0:
        session.exec(delete(TicketTagLink).where(TicketTagLink.ticket_id == ticket_id))

        for tag_nr in ticket.tag_nrs:
            tag = session.exec(select(Tag).where(Tag.board_id == db_ticket.board_id, Tag.nr == tag_nr)).first()
            if tag:
                link = TicketTagLink(ticket_id=db_ticket.id, tag_board_id=db_ticket.board_id, tag_nr=tag_nr)
                session.add(link)
    elif ticket.tag_nrs is not None and len(ticket.tag_nrs) == 0:
        session.exec(delete(TicketTagLink).where(TicketTagLink.ticket_id == ticket_id))

    session.add(db_ticket)
    session.commit()
    session.refresh(db_ticket)
    return db_ticket


@app.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: uuid.UUID, session: DbSession, current_user: Annotated[User, Depends(get_current_user)]):
    ticket_db = session.get(Ticket, ticket_id)
    if not ticket_db:
        raise HTTPException(status_code=404, detail="Ticket not found")
    session.delete(ticket_db)
    session.commit()
    return {}
