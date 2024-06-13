import inspect
from typing import Any, Optional, Union
from pydantic import BaseModel

def optional(*fields: Any):
    def dec(_cls):
        for field in fields:
            if field in _cls.__annotations__:
                annotation = _cls.__annotations__[field]
                if hasattr(annotation, '__origin__') and annotation.__origin__ is Union:
                    if type(None) not in annotation.__args__:
                        _cls.__annotations__[field] = Union[annotation.__args__ + (type(None),)]
                else:
                    _cls.__annotations__[field] = Optional[annotation]
        return _cls

    if fields and inspect.isclass(fields[0]) and issubclass(fields[0], BaseModel):
        cls = fields[0]
        fields = cls.model_fields
        return dec(cls)

    return dec
