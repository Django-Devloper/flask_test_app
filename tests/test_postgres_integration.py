import os
import time

import pytest


def _pg_env():
    # Defaults match the Postgres service container in `.github/workflows/deploy.yml`
    return {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", "sa_password!123456"),
        "dbname": os.getenv("POSTGRES_DB", "flask_app_test"),
    }


def _connect(dbname: str):
    # Lazy import so unit tests can run without the dependency.
    import psycopg2  # type: ignore

    env = _pg_env()
    return psycopg2.connect(
        host=env["host"],
        port=env["port"],
        user=env["user"],
        password=env["password"],
        dbname=dbname,
    )


def _wait_for_postgres(timeout_s: int = 30) -> bool:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            with _connect("postgres") as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1;")
            return True
        except Exception:
            time.sleep(1)
    return False


def _ensure_database_exists():
    env = _pg_env()
    try:
        with _connect(env["dbname"]) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
        return
    except Exception:
        pass

    # Create the DB from the default `postgres` database.
    with _connect("postgres") as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            try:
                cur.execute(f'CREATE DATABASE "{env["dbname"]}";')
            except Exception:
                # If another process created it first, that's fine.
                pass


@pytest.mark.integration
def test_postgres_smoke():
    # If Postgres isn't available (e.g., local run without docker), skip instead of failing.
    if not _wait_for_postgres(timeout_s=30):
        pytest.skip("Postgres not reachable; set POSTGRES_* env vars or run with the CI service.")

    _ensure_database_exists()
    env = _pg_env()

    with _connect(env["dbname"]) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS healthcheck (
                    id SERIAL PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )
            cur.execute("INSERT INTO healthcheck(value) VALUES (%s) RETURNING id;", ("ok",))
            new_id = cur.fetchone()[0]
            cur.execute("SELECT value FROM healthcheck WHERE id = %s;", (new_id,))
            value = cur.fetchone()[0]
            conn.commit()

    assert value == "ok"
