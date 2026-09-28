from app.application.common.interfaces import PushSender, PushSendResult
from app.domain.notifications.entities import PushProvider


class RoutingPushSender:
    """Token provayderiga qarab FCM yoki APNs adapteriga yo'naltiradi."""

    def __init__(self, senders: dict[PushProvider, PushSender]) -> None:
        self._senders = senders

    async def send(self, provider: PushProvider, token: str, title: str,
                   body: str) -> PushSendResult:
        sender = self._senders.get(provider)
        if sender is None:
            return PushSendResult.FAILED
        return await sender.send(provider, token, title, body)
