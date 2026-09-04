from pydantic import BaseModel


class OnboardingStepUpdate(BaseModel):
    step: str
    payload: dict


class OnboardingStatusResponse(BaseModel):
    completed_steps: list[str]
    checks: list[dict]
