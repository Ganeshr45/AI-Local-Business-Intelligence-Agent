from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.db import crud
from app.agents import ask_market

router = APIRouter()


class AskRequest(BaseModel):
    question: str


@router.post("/runs/{run_id}/ask")
def ask_question(run_id: str, payload: AskRequest, db: Session = Depends(get_db)):
    run = crud.get_run(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    result = ask_market.ask(db, run_id, payload.question)
    return result
