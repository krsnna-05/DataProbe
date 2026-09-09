from app.db.connection import get_connection
from app.schema.models import (
    ColumnInfo,
    DatabaseSchema,
    ForeignKeyInfo,
    TableInfo,
)


def get_schema() -> DatabaseSchema:
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

        table_rows = cursor.fetchall()

        tables = []

        for (table_name,) in table_rows:
            # Columns
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

            column_rows = cursor.fetchall()

            columns = [
                ColumnInfo(
                    name=column_name,
                    data_type=data_type,
                    nullable=is_nullable == "YES",
                )
                for column_name, data_type, is_nullable in column_rows
            ]

            # Primary keys
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

            primary_key_rows = cursor.fetchall()

            primary_keys = [row[0] for row in primary_key_rows]

            # Foreign keys
            cursor.execute(
                """
                    SELECT
                        kcu.column_name,
                        ccu.table_name AS referenced_table,
                        ccu.column_name AS referenced_column
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                     AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                     AND ccu.table_schema = tc.table_schema
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                      AND tc.table_schema = 'public'
                      AND tc.table_name = %s
                    ORDER BY kcu.ordinal_position;
                    """,
                (table_name,),
            )

            foreign_key_rows = cursor.fetchall()

            foreign_keys = [
                ForeignKeyInfo(
                    column=column_name,
                    referenced_table=referenced_table,
                    referenced_column=referenced_column,
                )
                for (
                    column_name,
                    referenced_table,
                    referenced_column,
                ) in foreign_key_rows
            ]

            tables.append(
                TableInfo(
                    name=table_name,
                    columns=columns,
                    primary_keys=primary_keys,
                    foreign_keys=foreign_keys,
                )
            )

    return DatabaseSchema(tables=tables)
