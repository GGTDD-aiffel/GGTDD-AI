from pydantic import BaseModel

class Scene(BaseModel):
    name: str
    location_tags: list[str]
    time_tags: list[str]
    other_tags: list[str]
    
    def print_self(self):
        print(f"Scene: {self.name}")
        print(f"- Location Tags: {self.location_tags}")
        print(f"- Time Tags: {self.time_tags}")
        print(f"- Other Tags: {self.other_tags}")

class Scenes(BaseModel):
    scenes: list[Scene]