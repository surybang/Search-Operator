from pathlib import Path
import psycopg

DDL_PATH = Path("data_pipeline/sql/schemas.sql")


def _exists(cur, qualname: str) -> bool:
    cur.execute("SELECT to_regclass(%s);", (qualname,))
    return cur.fetchone()[0] is not None


def _schema_exists(cur, schema: str) -> bool:
    cur.execute(
        "SELECT 1 FROM information_schema.schemata WHERE schema_name=%s;",
        (schema,),
    )
    return cur.fetchone() is not None


def test_create_medallion_schemas_and_tables():
    ddl_sql = DDL_PATH.read_text()

    # psycopg.connect() lira PGHOST/PGPORT/PGDATABASE/PGUSER/PGPASSWORD depuis l'env
    with psycopg.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(ddl_sql)  # multiple statements OK
            # Schémas
            assert _schema_exists(cur, "bronze")
            assert _schema_exists(cur, "silver")
            assert _schema_exists(cur, "gold")
            # Tables
            assert _exists(cur, "bronze.arcep_raw")
            assert _exists(cur, "silver.arcep_clean")
            assert _exists(cur, "gold.arcep_summary")
