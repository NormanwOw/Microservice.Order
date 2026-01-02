import json

from pydantic import BaseModel


class PydanticBase(BaseModel):
    pass

    def to_dict(self) -> dict:
        return json.loads(self.model_dump_json())
