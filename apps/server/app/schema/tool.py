from app.db.connection import get_connection


def list_tables() -> list[str]:
    """
    Return all user tables in the public schema.
    """

    with get_connection() as conn, conn.cursor() as cursor:
        cursor.execute(
            """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_type = 'BASE TABLE'
                ORDER BY table_name;
                """
        )

        return [row[0] for row in cursor.fetchall()]


def get_table_schema(table_name: str) -> dict:
    """
    Return detailed schema information for a single table.

    Includes:
    - columns
    - data types
    - nullability
    - primary keys
    - foreign keys
    """

    with get_connection() as conn, conn.cursor() as cursor:
        # ---------------------------------------------------------
        # 1. Verify table exists
        # ---------------------------------------------------------

        cursor.execute(
            """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                      AND table_name = %s
                      AND table_type = 'BASE TABLE'
                );
                """,
            (table_name,),
        )

        exists_row = cursor.fetchone()
        exists = exists_row is not None and exists_row[0]

        if not exists:
            raise ValueError(f"Table '{table_name}' does not exist")

        # ---------------------------------------------------------
        # 2. Columns
        # ---------------------------------------------------------

        cursor.execute(
            """
                SELECT
                    column_name,
                    data_type,
                    is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = %s
                ORDER BY ordinal_position;
                """,
            (table_name,),
        )

        columns = [
            {
                "name": row[0],
                "data_type": row[1],
                "nullable": row[2] == "YES",
            }
            for row in cursor.fetchall()
        ]

        # ---------------------------------------------------------
        # 3. Primary keys
        # ---------------------------------------------------------

        cursor.execute(
            """
                SELECT kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                  ON tc.constraint_name = kcu.constraint_name
                 AND tc.table_schema = kcu.table_schema
                WHERE tc.table_schema = 'public'
                  AND tc.table_name = %s
                  AND tc.constraint_type = 'PRIMARY KEY'
                ORDER BY kcu.ordinal_position;
                """,
            (table_name,),
        )

        primary_keys = [row[0] for row in cursor.fetchall()]

        # ---------------------------------------------------------
        # 4. Foreign keys
        # ---------------------------------------------------------

        cursor.execute(
            """
                SELECT
                    kcu.column_name,
                    ccu.table_name AS referenced_table,
                    ccu.column_name AS referenced_column
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                  ON tc.constraint_name = kcu.constraint_name
                 AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage ccu
                  ON ccu.constraint_name = tc.constraint_name
                 AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                  AND tc.table_schema = 'public'
                  AND tc.table_name = %s
                ORDER BY kcu.ordinal_position;
                """,
            (table_name,),
        )

        foreign_keys = [
            {
                "column": row[0],
                "referenced_table": row[1],
                "referenced_column": row[2],
            }
            for row in cursor.fetchall()
        ]

    return {
        "table": table_name,
        "columns": columns,
        "primary_keys": primary_keys,
        "foreign_keys": foreign_keys,
    }
