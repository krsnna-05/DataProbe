from app.schema.introspector import get_schema
from app.schema.models import DatabaseSchema


class SchemaService:
    def __init__(self):
        self._schema = get_schema()

    def get_schema(self) -> DatabaseSchema:
        return self._schema
