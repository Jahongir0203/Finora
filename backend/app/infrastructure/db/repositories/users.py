from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.users.entities import User
from app.infrastructure.db.models import (
    BudgetModel,
    DeviceModel,
    ExportModel,
    GoalEntryModel,
    GoalModel,
    IdempotencyKeyModel,
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
                created_at=m.created_at)


class SqlUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get(self, user_id: UUID) -> User | None:
        m = await self._s.get(UserModel, user_id)
        return _to_entity(m) if m else None

    async def get_by_phone_index(self, phone_index: str) -> User | None:
        m = await self._s.scalar(select(UserModel).where(UserModel.phone_index == phone_index))
        return _to_entity(m) if m else None

    async def add(self, user: User) -> None:
        self._s.add(UserModel(id=user.id, phone_ciphertext=user.phone_ciphertext,
                              phone_index=user.phone_index, created_at=user.created_at))
        # SQLAlchemy 2.1 relationship'siz FK tartibini kafolatlamaydi — ota qatorni darhol yozamiz
        await self._s.flush()

    async def purge(self, user_id: UUID) -> None:
        # ON DELETE CASCADE bor, lekin DB'dan qat'i nazar aniq tartibda o'chiramiz
        session_ids = select(SessionModel.id).where(SessionModel.user_id == user_id)
        await self._s.execute(
            delete(RefreshTokenModel).where(RefreshTokenModel.session_id.in_(session_ids))
        )
        for model in (SessionModel, DeviceModel, GoalEntryModel, GoalModel, TransactionModel,
                      ExportModel, ReceiptModel, ReminderModel, NotificationModel, BudgetModel,
                      IdempotencyKeyModel):
            await self._s.execute(delete(model).where(model.user_id == user_id))
        await self._s.execute(delete(UserModel).where(UserModel.id == user_id))
