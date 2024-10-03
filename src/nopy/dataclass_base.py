import dataclasses
import datetime
import json
import typing

import colour


@dataclasses.dataclass
class DataclassBase:
    @classmethod
    def from_json(cls, json_obj: str | dict[str, typing.Any]) -> typing.Self:
        if type(json_obj) is str:
            json_obj = json.loads(json_obj)
        props = {}
        for field in dataclasses.fields(cls):
            value = json_obj[field.name]
            if hasattr(field.type, "from_json") and value is not None:
                props[field.name] = field.type.from_json(value)
            elif hasattr(field.type, "fromisoformat"):
                props[field.name] = field.type.fromisoformat(value)
            elif field.type is colour.Color:
                props[field.name] = colour.Color(f"#{value}")
            else:
                props[field.name] = value
        return cls(**props)

    def to_json(self) -> dict[str, typing.Any]:
        ret = {}
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            if value is None:
                continue
            elif hasattr(value, "to_json"):
                ret[field.name] = value.to_json()
            elif hasattr(value, "isoformat"):
                ret[field.name] = value.isoformat()
            elif field.type is colour.Color:
                ret[field.name] = value.hex_l[1:]
            else:
                ret[field.name] = value
        return ret

