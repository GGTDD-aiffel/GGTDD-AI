from datetime import datetime
from pydantic import BaseModel
from typing import TYPE_CHECKING, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import BaseOutputParser
from langchain_openai import ChatOpenAI

if TYPE_CHECKING:
    from .Scene import *

class User(BaseModel):
    """사용자의 기본적인 정보를 나타내는 클래스입니다.

    Attributes:
        name (str): 사용자의 이름.
        user_id (int): 사용자의 고유 식별자. 0은 등록되지 않은 사용자를 의미합니다.
        email (str): 사용자의 이메일 주소.
        
        residence (str): 사용자의 거주지.
        birth_date (datetime): 사용자의 생년월일.
        occupation (str): 사용자의 직업.
        personality (list[str]): ["Introverted", "Intuitive", "Thinking", "Perceiving"]와 같은 형태로 MBTI를 나타내는 문자열 리스트.
        scenes (list[Scene]): 사용자의 하루 일과를 나타내는 Scene 객체의 리스트.

        positives (list[str]): 사용자의 긍정적인 특성.
        negatives (list[str]): 사용자의 부정적인 특성.
        prompt (str): 사용자 정보를 바탕으로 생성된 프롬프트.

        status (str): 사용자의 상태.
        is_admin (bool): 사용자가 관리자인지 여부.
    """
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
            
    def __str__(self) -> str:
        result = [f"User: {self.name}"]
        result.append(f"- Location: {self.residence}")
        result.append(f"- Birthdate: {self.birth_date}")
        result.append(f"- Occupation: {self.occupation}")
        result.append(f"- Personality: {self.personality}")
        result.append(f"- Positives: {self.positives}")
        result.append(f"- Negatives: {self.negatives}")
        result.append(f"- Prompt: {self.prompt}")
        result.append("Daily Scenes:")
        for scene in self.scenes:
            scene_str = str(scene).replace("\n", "\n  ")
            result.append(f"  {scene_str}")
        return "\n".join(result)

class CustomListOutputParser(BaseOutputParser):
    def parse(self, text: str) -> list[str]:
        responses = text.split("---")
        items = [response.strip() for response in responses]
        return items

    def get_format_instructions(self) -> str:
        return '서로 다른 답변은 "---"로 구분하세요.'

# 파서 초기화
response_parser = CustomListOutputParser()