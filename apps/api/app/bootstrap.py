import asyncio

from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.entities import (
    ConnectorType,
    Incident,
    IncidentComment,
    IncidentEvent,
    IntegrationConnector,
    RoleEnum,
    ProvenanceEnum,
    SeverityEnum,
    Team,
    TeamMembership,
    User,
)
from app.rag.vector_store import VectorStore


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_data() -> None:
    settings = get_settings()
    async with SessionLocal() as db:
        admin = (await db.execute(select(User).where(User.email == settings.admin_email))).scalar_one_or_none()
        if not admin:
            admin = User(
                email=settings.admin_email,
                full_name="OpsCentreDan Admin",
                hashed_password=hash_password(settings.admin_password),
                role=RoleEnum.ADMIN,
                is_active=True,
            )
            db.add(admin)
            await db.flush()

        team = (await db.execute(select(Team).where(Team.name == "Platform"))).scalar_one_or_none()
        if not team:
            team = Team(name="Platform")
            db.add(team)
            await db.flush()

        membership = (
            await db.execute(
                select(TeamMembership)
                .where(TeamMembership.team_id == team.id)
                .where(TeamMembership.user_id == admin.id)
            )
        ).scalar_one_or_none()
        if not membership:
            db.add(TeamMembership(team_id=team.id, user_id=admin.id))

        connector = (
            await db.execute(
                select(IntegrationConnector).where(IntegrationConnector.name == "Generic Demo Webhook")
            )
        ).scalar_one_or_none()
        if not connector:
            db.add(
                IntegrationConnector(
                    name="Generic Demo Webhook",
                    connector_type=ConnectorType.GENERIC,
                    shared_secret="demo-secret",
                    config_json={"description": "Demo connector for local testing"},
                )
            )

        if settings.demo_mode:
            existing_demo = (
                await db.execute(select(Incident).where(Incident.title == "Checkout API latency spike"))
            ).scalar_one_or_none()
            if not existing_demo:
                incident = Incident(
                    title="Checkout API latency spike",
                    description="P95 latency rose above SLO after deployment.",
                    severity=SeverityEnum.SEV2,
                    priority=2,
                    environment="production",
                    affected_systems=["checkout-api", "postgres"],
                    tags=["latency", "customer-impact"],
                    assignee_id=admin.id,
                    team_id=team.id,
                )
                db.add(incident)
                await db.flush()

                db.add(
                    IncidentEvent(
                        incident_id=incident.id,
                        actor_id=admin.id,
                        event_type="incident_created",
                        message="Seeded demo incident",
                        metadata_json={"seed": True},
                    )
                )
                db.add(
                    IncidentComment(
                        incident_id=incident.id,
                        author_id=admin.id,
                        body="Initial triage: elevated DB wait time detected.",
                        provenance=ProvenanceEnum.HUMAN,
                    )
                )

        await db.commit()


async def init_vector_store() -> None:
    store = VectorStore()
    store.ensure_collection()


async def main() -> None:
    await init_db()
    await seed_data()
    await init_vector_store()


if __name__ == "__main__":
    asyncio.run(main())
