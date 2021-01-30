"""
functions outside the interface defn
"""

import asyncpg  # type: ignore
import dataclasses
from typing import Callable
from typing import TypeVar

T = TypeVar("T")


DBRecordConvertor = Callable[[asyncpg.Record], T]


def get_data_class_convertor(clazz: type[T]) -> DBRecordConvertor[T]:
    "factory function returning map from asyncpg record to named tuple type"
    field_names = [field.name for field in dataclasses.fields(clazz)]

    def converter(record: asyncpg.Record):
        return clazz(**dict([(field, record.get(field)) for field in field_names]))  # type: ignore

    return converter
