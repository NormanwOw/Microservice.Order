import json
from typing import Any, cast

from pydantic import BaseModel


class PydanticBase(BaseModel):
    def to_dict(self) -> dict[str, Any]:
        return cast(dict[str, Any], json.loads(self.model_dump_json()))
