import pytest

from app.application.exports.csv_safe import render_csv, sanitize_cell
from app.core.logging import mask_phone, scrub
from app.domain.common.errors import InsufficientFundsError, ValidationFailedError
from app.domain.common.ids import uuid7
from app.domain.common.values import PhoneNumber, ensure_amount
from app.domain.goals.entities import ensure_can_withdraw


def test_uuid7_version_and_order():
    ids = [uuid7() for _ in range(100)]
    assert all(i.version == 7 and i.variant == "specified in RFC 4122" for i in ids)
    assert len(set(ids)) == 100


@pytest.mark.parametrize("value", ["=cmd", "+1", "-1", "@SUM(A1)"])
def test_csv_formula_prefixed(value):
    assert sanitize_cell(value) == "'" + value


def test_csv_render():
    out = render_csv(["a"], [["=cmd"]]).decode("utf-8-sig")
    assert out.splitlines()[1] == "'=cmd"


def test_amount_bounds():
    assert ensure_amount(10**12) == 10**12
    for bad in (0, -1, 10**12 + 1, True):
        with pytest.raises(ValidationFailedError):
            ensure_amount(bad)


def test_withdraw_rule():
    ensure_can_withdraw(100, 100)
    with pytest.raises(InsufficientFundsError):
        ensure_can_withdraw(100, 101)


def test_phone_masking():
    p = PhoneNumber.parse("+998 90 123 45 67")
    assert p.value == "+998901234567"
    assert str(p) == "PhoneNumber(+998 90 *** ** 67)"
    assert mask_phone("+998901234567") == "+998 90 *** ** 67"
    assert scrub({"refresh_token": "abc", "note": "call +998901234567"}) == {
        "refresh_token": "[redacted]", "note": "call +998 90 *** ** 67"}


def test_prod_requires_real_providers():
    from pydantic import ValidationError

    from app.core.config import Settings

    base = {
        "env": "prod", "jwt_private_key": "pem", "otp_hmac_key": "k1" * 16,
        "blind_index_key": "k2" * 16, "field_encryption_key": "k3" * 16,
        "refresh_token_pepper": "k4" * 16, "url_signing_key": "k5" * 16,
    }
    with pytest.raises(ValidationError, match="SMS"):
        Settings(**base)
    with pytest.raises(ValidationError, match="push"):
        Settings(**base, sms_provider="eskiz")
    with pytest.raises(ValidationError, match="S3"):
        Settings(**base, sms_provider="eskiz", fcm_service_account_json="{}")
