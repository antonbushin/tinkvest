from decimal import Decimal

import orjson
from pydantic import BaseModel
from typing import List
from pydantic.json import pydantic_encoder


def my_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)

    # Далее можно описывать и другие свои типы, например MyFooFooBar
    # elif isinstance(obj, MyFooFooBar):
    #     return obj.get_super_foo_bar_value()

    # Если не удалось определить тип:
    return str(obj)


def object_to_dict(data: [BaseModel, List[BaseModel]]):
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
