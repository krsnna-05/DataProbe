import os

import psycopg

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://dataprobe:dataprobe@localhost:5432/chinook",
)


def get_connection():
    return psycopg.connect(DATABASE_URL)
