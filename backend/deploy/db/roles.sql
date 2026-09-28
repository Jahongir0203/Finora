-- Finora: minimal huquqli baza rollari (02-backend.md, 5-bo'lim; 9-bo'lim audit log).
--
-- Ishga tushirish (superuser / DBA, bir marta, migratsiyalardan OLDIN):
--   psql -v owner_pw="'...'" -v app_pw="'...'" -d finora -f deploy/db/roles.sql
-- Parollar Vault'dan olinadi, repoga yozilmaydi.
--
-- Rollar:
--   finora_owner — sxema egasi, faqat Alembic migratsiyalari uchun (CI/CD deploy bosqichi).
--   finora_app   — ilova xizmati: faqat DML (SELECT/INSERT/UPDATE/DELETE). DDL yo'q:
--                  CREATE/DROP/ALTER/TRUNCATE qila olmaydi. audit_log'ga faqat INSERT.

\set ON_ERROR_STOP on

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'finora_owner') THEN
        CREATE ROLE finora_owner LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'finora_app') THEN
        CREATE ROLE finora_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
    END IF;
END
$$;

ALTER ROLE finora_owner PASSWORD :owner_pw;
ALTER ROLE finora_app PASSWORD :app_pw;

-- Hech kim public sxemada o'zicha obyekt yarata olmasin (PG < 15 da standart ruxsat bor edi)
REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON DATABASE finora FROM PUBLIC;
ALTER SCHEMA public OWNER TO finora_owner;
GRANT CONNECT ON DATABASE finora TO finora_owner, finora_app;
GRANT USAGE ON SCHEMA public TO finora_app;

-- Owner yaratadigan KELAJAKDAGI jadvallar uchun standart huquqlar (migratsiyalar owner'dan)
ALTER DEFAULT PRIVILEGES FOR ROLE finora_owner IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO finora_app;
ALTER DEFAULT PRIVILEGES FOR ROLE finora_owner IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO finora_app;

-- Ilova so'rovlari cheklangan vaqtda tugasin (uzun so'rov / qulf DoS'ga qarshi)
ALTER ROLE finora_app SET statement_timeout = '15s';
ALTER ROLE finora_app SET idle_in_transaction_session_timeout = '30s';
