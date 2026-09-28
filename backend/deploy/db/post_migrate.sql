-- Har `alembic upgrade head`dan KEYIN finora_owner nomidan ishga tushiriladi.
-- Default privileges yangi jadvallarga DML beradi; bu fayl istisnolarni qat'iylashtiradi.

\set ON_ERROR_STOP on

-- Audit log: append-only (02-backend.md, 9-bo'lim). Ilova faqat yozadi, o'qimaydi ham.
REVOKE ALL ON TABLE audit_log FROM finora_app;
GRANT INSERT ON TABLE audit_log TO finora_app;

-- Hatto owner ham UPDATE qila olmasin: o'zgartirishga urinish xato beradi.
CREATE OR REPLACE FUNCTION audit_log_immutable() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'audit_log o''zgartirib bo''lmaydi';
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS audit_log_no_update ON audit_log;
CREATE TRIGGER audit_log_no_update BEFORE UPDATE ON audit_log
    FOR EACH ROW EXECUTE FUNCTION audit_log_immutable();

-- 1 yillik saqlash: faqat 1 yildan eski yozuvlarni o'chirish ruxsat etiladi.
CREATE OR REPLACE FUNCTION audit_log_retention_guard() RETURNS trigger AS $$
BEGIN
    IF OLD.created_at > now() - interval '1 year' THEN
        RAISE EXCEPTION 'audit_log: 1 yildan yangi yozuvni o''chirib bo''lmaydi';
    END IF;
    RETURN OLD;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS audit_log_retention ON audit_log;
CREATE TRIGGER audit_log_retention BEFORE DELETE ON audit_log
    FOR EACH ROW EXECUTE FUNCTION audit_log_retention_guard();

-- Kunlik retention (pg_cron yoki DBA cron, finora_owner nomidan):
--   DELETE FROM audit_log WHERE created_at < now() - interval '1 year';
