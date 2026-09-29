"""Use-case fabrikalari: router'lar container'dan servis yig'ish tafsilotini bilmaydi."""

from app.application.accounts.use_cases import AccountService, OnboardingBalance
from app.application.auth.otp import OtpChecker, RequestOtp
from app.application.categories.use_cases import CategoryService
from app.application.exports.use_cases import ExportService
from app.application.goals.use_cases import GoalService
from app.application.insights.use_cases import InsightService
from app.application.receipts.use_cases import ReceiptService
from app.application.reminders.use_cases import ReminderService
from app.application.telegram.use_cases import TelegramOtpChannel
from app.application.transactions.use_cases import TransactionService, TransferService
from app.container import Container
from app.infrastructure.files.images import sniff_image_format


def transactions(c: Container) -> TransactionService:
    return TransactionService(c.uow(), c.clock, c.settings, c.ledger, c.notifier)


def transfers(c: Container) -> TransferService:
    return TransferService(c.uow(), c.clock, c.settings, c.ledger)


def accounts(c: Container) -> AccountService:
    return AccountService(c.uow(), c.clock, c.settings, c.ledger)


def onboarding(c: Container) -> OnboardingBalance:
    return OnboardingBalance(c.uow(), c.clock, c.ledger)


def categories(c: Container) -> CategoryService:
    return CategoryService(c.uow(), c.clock, c.settings, c.ledger)


def goals(c: Container) -> GoalService:
    return GoalService(c.uow(), c.clock, c.settings, c.ledger, c.notifier)


def reminders(c: Container) -> ReminderService:
    return ReminderService(c.uow(), c.clock, c.settings, c.ledger)


def insights(c: Container) -> InsightService:
    return InsightService(c.uow, c.kv, c.clock)


def exports(c: Container) -> ExportService:
    return ExportService(c.uow, c.storage, c.signer, c.limiter, c.clock, c.settings,
                         c.renderers)


def receipts(c: Container) -> ReceiptService:
    return ReceiptService(c.uow(), c.storage, c.scanner, c.sanitizer, c.signer, c.limiter,
                          c.clock, c.settings, sniff_image_format, c.ocr, c.fiscal)


def request_otp(c: Container) -> RequestOtp:
    telegram = TelegramOtpChannel(c.uow, c.telegram) if c.telegram is not None else None
    return RequestOtp(c.kv, c.limiter, c.hasher, c.sms, c.clock, c.settings, c.attestation,
                      telegram)


def otp_checker(c: Container) -> OtpChecker:
    return OtpChecker(c.kv, c.hasher, c.clock, c.settings)
