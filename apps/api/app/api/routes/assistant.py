from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import EngineerOrAdminUser
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.models.entities import Incident
from app.rag.service import RagService, get_similar_incidents
from app.schemas.assistant import AssistantAnswerResponse, AssistantQuestionRequest

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/incidents/{incident_id}/ask", response_model=AssistantAnswerResponse)
@limiter.limit("30/minute")
async def ask_incident_question(
    request: Request,
    incident_id: str,
    payload: AssistantQuestionRequest,
    current_user: EngineerOrAdminUser,
    db: AsyncSession = Depends(get_db),
) -> AssistantAnswerResponse:
    incident = (await db.execute(select(Incident).where(Incident.id == incident_id))).scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    service = RagService()
    try:
        result = await service.answer_incident_question(db, incident_id, payload.question)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    if payload.include_similar_incidents:
        result["suggested_next_actions"] = result.get("suggested_next_actions", []) + [
            "Review similar incidents listed in the related incidents panel."
        ]
        result["similar_incidents"] = await get_similar_incidents(db, incident)

    return AssistantAnswerResponse.model_validate(result)
