from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.users.entities import Theme, User
from app.infrastructure.db.models import (
    AccountModel,
    CategoryModel,
    CategoryPrefModel,
    DeviceModel,
    ExportModel,
    GoalEntryModel,
    GoalModel,
    IdempotencyKeyModel,
    InsightModel,
    NotificationModel,
    ReceiptModel,
    RefreshTokenModel,
    ReminderModel,
    SessionModel,
    TransactionModel,
    UserModel,
)


def _to_entity(m: UserModel) -> User:
    return User(id=m.id, phone_ciphertext=m.phone_ciphertext, phone_index=m.phone_index,
                created_at=m.created_at, first_name=m.first_name, last_name=m.last_name,
                language=m.language, currency=m.currency, theme=Theme(m.theme),
                notifications_enabled=m.notifications_enabled, timezone=m.timezone,
                balance_set=m.balance_set)


class SqlUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get(self, user_id: UUID) -> User | None:
        m = await self._s.get(UserModel, user_id, populate_existing=True)
        return _to_entity(m) if m else None

    async def get_by_phone_index(self, phone_index: str) -> User | None:
        m = await self._s.scalar(select(UserModel).where(UserModel.phone_index == phone_index))
        return _to_entity(m) if m else None

    async def add(self, user: User) -> None:
        self._s.add(UserModel(
            id=user.id, phone_ciphertext=user.phone_ciphertext, phone_index=user.phone_index,
            created_at=user.created_at, first_name=user.first_name, last_name=user.last_name,
            language=user.language, currency=user.currency, theme=user.theme.value,
            notifications_enabled=user.notifications_enabled, timezone=user.timezone,
            balance_set=user.balance_set,
        ))
        # SQLAlchemy 2.1 relationship'siz FK tartibini kafolatlamaydi — ota qatorni darhol yozamiz
        await self._s.flush()

    async def update(self, user: User) -> None:
        await self._s.execute(
            update(UserModel).where(UserModel.id == user.id).values(
                first_name=user.first_name, last_name=user.last_name, language=user.language,
                currency=user.currency, theme=user.theme.value,
                notifications_enabled=user.notifications_enabled, timezone=user.timezone,
                balance_set=user.balance_set,
            )
        )

    async def set_phone_ciphertext(self, user_id: UUID, ciphertext: bytes) -> None:
        await self._s.execute(
            update(UserModel).where(UserModel.id == user_id).values(phone_ciphertext=ciphertext)
        )

    async def list_ids(self, *, after: UUID | None, limit: int) -> list[User]:
        stmt = select(UserModel).order_by(UserModel.id).limit(limit)
        if after is not None:
            stmt = stmt.where(UserModel.id > after)
        return [_to_entity(m) for m in await self._s.scalars(stmt)]

    async def purge(self, user_id: UUID) -> None:
        # ON DELETE CASCADE bor, lekin DB'dan qat'i nazar aniq tartibda o'chiramiz
        session_ids = select(SessionModel.id).where(SessionModel.user_id == user_id)
        await self._s.execute(
            delete(RefreshTokenModel).where(RefreshTokenModel.session_id.in_(session_ids))
        )
        for model in (SessionModel, DeviceModel, GoalEntryModel, GoalModel, TransactionModel,
                      ExportModel, ReceiptModel, ReminderModel, NotificationModel,
                      CategoryPrefModel, CategoryModel, AccountModel, InsightModel,
                      IdempotencyKeyModel):
            await self._s.execute(delete(model).where(model.user_id == user_id))
        await self._s.execute(delete(UserModel).where(UserModel.id == user_id))
