from pydantic import BaseModel

class Scene(BaseModel):
    name: str
    location_tags: list[str]
    time_tags: list[str]
    other_tags: list[str]

class Scenes(BaseModel):
    scenes: list[Scene]