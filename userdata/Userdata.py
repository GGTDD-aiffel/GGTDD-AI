from datetime import datetime
from pydantic import BaseModel
from typing import TYPE_CHECKING, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import BaseOutputParser
from langchain_openai import ChatOpenAI

if TYPE_CHECKING:
    from .Scene import *

class User(BaseModel):
    name: str
    user_id: int = 0 # 0 means not registered
    email: str = ""

    residence: str
    birth_date: datetime
    occupation: str
    personality: list[str]
    scenes: list['Scene'] = []

    positives: list[str]
    negatives: list[str]
    prompt: str

    status: str = "active"
    is_admin: bool = False

    
    @property
    def bio(self):
        return self.model_dump_json()
    
    def generate_prompt(self):
        prompt_template = ChatPromptTemplate.from_template("""
        다음은 사용자 정보입니다. 이 정보를 바탕으로, 사용자의 성격과 하루 일과, 주요 관심사를를 상상해서 1문단으로 작성하세요.
        이를 작성하는 이유는 사용자의 할 일을 사용자의 생활패턴과 맥락에 맞게 구체화하여 추천하기 위해서입니다.
        사용자에 대한 이해가 깊어질수록 사용자에게 더 유용한 할 일을 추천할 수 있습니다.
        사용자의 긍정적인 면과 부정적인 면을 모두 포함할 수 있도록 작성하세요.

        작성된 내용 중 사용자가 적합한 것을 선택할 수 있도록, 서로 다른 내용의 답변을 3~5개 생성하세요.
        각각의 답변은 사용자 정보의 다른 부분에 집중하며, 서로 비슷하지 않은 내용이어야 합니다.
        예를 들어 한 답변이 "대중교통"이라는 키워드에 집중한다면, 다른 답변은 "도서관" 등 다른 맥락에 집중할 수 있습니다.
        만약 비슷한 답변이 생성된다면 생략하세요.

        {format_instruction}

        사용자 정보: {bio}
        """).partial(format_instruction=response_parser.get_format_instructions())

        llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5)

        chain = prompt_template | llm | response_parser
        responses = chain.invoke({"bio": self.bio})
        
        return responses
    
    def set_prompt(self, responses: list[str], index: int):
        self.prompt = responses[index]
        
    def append_scenes(self, scenes: list['Scene']):
        for scene in scenes:
            self.scenes.append(scene)
            
    def print_self(self):
        print(f"User: {self.name}")
        print(f"- Location: {self.residence}")
        print(f"- Birthdate: {self.birth_date}")
        print(f"- Occupation: {self.occupation}")
        print(f"- Personality: {self.personality}")
        print(f"- Positives: {self.positives}")
        print(f"- Negatives: {self.negatives}")
        print(f"- Prompt: {self.prompt}")
        print(f"Daily Scenes of {self.name}:")
        for scene in self.scenes:
            scene.print_self()

class CustomListOutputParser(BaseOutputParser):
    def parse(self, text: str) -> list[str]:
        responses = text.split("---")
        items = [response.strip() for response in responses]
        return items

    def get_format_instructions(self) -> str:
        return '서로 다른 답변은 "---"로 구분하세요.'

# 파서 초기화
response_parser = CustomListOutputParser()