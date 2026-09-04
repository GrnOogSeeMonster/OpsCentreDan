from pydantic import BaseModel, Field


class AssistantQuestionRequest(BaseModel):
    question: str = Field(min_length=3)
    include_similar_incidents: bool = True


class AssistantCitation(BaseModel):
    source_type: str
    source_ref: str
    chunk_id: str
    excerpt: str
    score: float


class AssistantAnswerResponse(BaseModel):
    answer: str
    evidence_summary: list[str]
    inferences: list[str]
    uncertainty: str
    suggested_next_actions: list[str]
    citations: list[AssistantCitation]
