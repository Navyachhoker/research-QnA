from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas.qa import AskRequest, AskResponse
from app.db.database import get_db
from app.db.models import User
from app.services import auth_service, chat_service, generator_service, paper_service, retriever_service

router = APIRouter(prefix="/qa", tags=["qa"])


@router.post("/ask", response_model=AskResponse)
def ask(
    payload: AskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    if payload.paper:
        # Raises 404 if the paper doesn't exist or belongs to another
        # user — the caller can't probe for other users' paper_ids by
        # trying them here.
        paper_service.get_paper(payload.paper, db, owner_id=current_user.user_id)

    chunks = retriever_service.retrieve_chunks(
        query=payload.question,
        owner_id=current_user.user_id,
        top_k=payload.top_k,
        paper_id=payload.paper,
    )

    if payload.session_id:
        session = chat_service.get_owned_session(db, payload.session_id, owner_id=current_user.user_id)
        history = chat_service.get_recent_history(db, session.session_id)
        result = generator_service.answer_query_with_history(payload.question, chunks, history)
        chat_service.add_message(db, session.session_id, role="user", content=payload.question)
        chat_service.add_message(db, session.session_id, role="assistant", content=result["answer"])
    else:
        result = generator_service.answer_query(payload.question, chunks)

    return AskResponse(**result)
