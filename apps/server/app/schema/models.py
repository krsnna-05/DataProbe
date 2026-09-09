from pydantic import BaseModel


class ColumnInfo(BaseModel):
    name: str
    data_type: str
    nullable: bool


class ForeignKeyInfo(BaseModel):
    column: str
    referenced_table: str
    referenced_column: str


class TableInfo(BaseModel):
    name: str
    columns: list[ColumnInfo]
    primary_keys: list[str]
    foreign_keys: list[ForeignKeyInfo]


class DatabaseSchema(BaseModel):
    tables: list[TableInfo]
