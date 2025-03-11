from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from .Scene import *
from .Userdata import *

class SceneGenerator:
    llm: ChatOpenAI

    ### Prompt for generating tasks    
    _prompt: ChatPromptTemplate
    
    prompt_main: str = """
        다음은 사용자의 하루를 구성하는 장면들입니다.
        사용자의 정보와 이 장면들을 바탕으로, 각각의 장면에 어울리는 시간, 공간, 기타 태그를 3~5개씩 필요에 따라 작성하고, 아래 지침에 따라 json 포맷으로 반환하세요.

        태그를 붙이는 목적은 할 일을 관리하기 위한 데이터베이스에 사용하기 위해서입니다.
        각각의 할 일은 사용자의 하루를 나타내는 여러 장면을 담은 태그와 함께 저장되고, 사용자가 처한 맥락과 상황을 표현하는 태그에 맞춰 할 일을 추천합니다.

        시간 태그에는 휴일 여부, 요일, 하루 중의 시간대 등의 정보를 포함하세요.
        공간 태그에는 사용자의 위치, 활동하는 장소 등의 정보를 포함하세요.
        기타 태그에는 시간과 공간 태그에 포함되지 않지만 할 일의 맥락과 상황을 검색하기에 좋은 정보를 포함하세요.
        """
    prompt_context: str = """
        사용자 정보: {bio}
        장면: {scenes}
        지침: {format_instruction}
        """
    
    def __init__(self, llm: ChatOpenAI):
        """
        Initialize a new task generator with the given LLM instance.
        
        Args:
            llm (ChatOpenAI): The LLM instance to use for generating tasks.
        """
        self.llm = llm
        self._prompt = ChatPromptTemplate.from_template(self.get_prompt_string())
        self.scene_parser = PydanticOutputParser(pydantic_object=Scenes)
        
    def set_main_prompt(self, prompt: str) -> None:
        """
        Set the prompt to use for generating tasks.
        
        Args:
            prompt (str): The prompt to use for generating tasks.
        """
        
        self.prompt_main = prompt
    
    def set_context_prompt(self, prompt_context: str) -> None:
        """
        Set the context prompt to use for generating tasks.
        
        Args:
            prompt_context (str): The context prompt to use for generating tasks.
        """
        
        self.prompt_context = prompt_context
    
    def get_prompt_template(self):
        """
        Get the ChatPromptTemplate object for generating tasks.
        
        Returns:
            ChatPromptTemplate: The prompt template object.
        """
        template_str = f"{self.prompt_main}\n{self.prompt_context}"
        return ChatPromptTemplate.from_template(template_str)

    def get_prompt_string(self):
        """
        Get the raw prompt string.
        
        Returns:
            str: The raw prompt string.
        """
        return f"{self.prompt_main}\n{self.prompt_context}"

    def generate_scenes(self, user: User, scenes: list[str]) -> Scenes:
        chain = self.get_prompt_template() | self.llm | self.scene_parser
        format_instruction = self.scene_parser.get_format_instructions()
        scenes = chain.invoke({"bio": user.bio,
                               "scenes": scenes,
                               "format_instruction": format_instruction})
        
        return scenes.scenes