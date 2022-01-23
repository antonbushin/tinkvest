"""Утилиты"""

from decimal import Decimal
from typing import List
import orjson
from pydantic import BaseModel


def my_default(obj):
    """Правила преобразования типов к json-serializable виду"""
    if isinstance(obj, Decimal):
        return float(obj)

    # Если не удалось определить тип:
    return str(obj)


def object_to_dict(data: [BaseModel, List[BaseModel]]):
    """BaseModel -> dict"""
    print("data:", type(data), data)
    new_data = orjson.dumps([ob.dict() for ob in data], default=my_default)
    result = orjson.loads(new_data)
    print("result:", type(result), result)
    # if isinstance(data, List):
    #     new_data = orjson.loads([x.json() for x in data])
    # else:
    # new_data = orjson.loads(data.json())
    # dumped_object = orjson.dumps(data, default=pydantic_encoder)
    # loaded_object = orjson.loads(dumped_object)
    return new_data


def prepare_filename(filename: str) -> str:
    """Генерация filename-безопасной строки"""
    return "".join([c for c in filename if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
