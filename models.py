import json
from pydantic import BaseModel
from dataclasses import dataclass
from openai.types import Moderation
from openai.types import ModerationMultiModalInputParam
from discord import Embed

from typing import Dict, Literal, cast


class Config(BaseModel):
    report_channels: Dict[int, int]

    def set_report_channel(
        self,
        guild_id: int,
        channel_id: int,
    ):
        self.report_channels[guild_id] = channel_id
        self._save()

    def _save(self):
        with open("config.json", "w") as f:
            json.dump(self.model_dump(), f, indent=4)

    @classmethod
    def load(cls) -> "Config":
        with open("config.json", "r") as f:
            data = json.load(f)
            return Config.model_validate(data)


class ModerationResult:
    def __init__(
        self,
        model_response: Moderation,
        model_input: ModerationMultiModalInputParam,
    ) -> None:
        self.flagged: bool = model_response.flagged
        self.type: Literal["image_url", "text"] = model_input.get("type")
        self.category_scores: Dict[str, float] = cast(
            Dict[str, float], model_response.category_scores.to_dict()
        )
        self.content: str = "NOT_FOUND"
        if model_input["type"] == "text":
            self.content = model_input["text"]
        elif model_input["type"] == "image_url":
            self.content = model_input["image_url"]["url"]


@dataclass
class ViolationField:
    name: str
    value: float

    def add_field(self, embed: Embed):
        embed.add_field(name=self.name, value=f"{self.value}%")
