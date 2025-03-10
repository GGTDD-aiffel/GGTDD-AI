from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from .Task import *
from .Subtask import *
from userdata import *

class TaskGenerator:
    llm: ChatOpenAI

    ### Prompt for generating tasks    
    _prompt: ChatPromptTemplate
    
    prompt_main: str = """
        다음은 사용자가 입력한 해야 할 일입니다. 이 할 일을 세부적으로 나누어 작성하세요.
        각각의 할 일은 최대한 구체적인 행동으로 작성하고, 이를 수행하는 데 필요한 시간과 노력을 고려하여 작성하세요.
        할 일을 세부적으로 나누면 사용자가 할 일을 더 쉽게 완료할 수 있습니다.

        각각의 할 일은 사용자의 하루를 나타내는 여러 장면을 담은 태그와 함께 저장되고, 사용자가 처한 맥락과 상황을 표현하는 태그에 맞춰 할 일을 추천합니다.
        각각의 할 일은 사용자의 위치, 활동하는 장소, 시간대 등을 고려하여 태그를 부여하세요.

        Task의 context에서는 사용자 정보와 하루 일과에 기반하여 해당 할 일을 언제 하는 것이 좋을지 설명하세요.
        각각의 Subtask에 적절한 태그를 부여하세요.
        """
    prompt_context: str = """
        사용자의 인적 정보: {bio}
        사용자의 하루 일과: {prompt}
        사용자가 입력한 할 일: {task}
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
        self.task_parser = PydanticOutputParser(pydantic_object=Task)
        self.subtask_parser = PydanticOutputParser(pydantic_object=Subtask)
        
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

    def generate_task(self, user: User, task_name: str) -> Task:
        chain = self.get_prompt_template() | self.llm | self.task_parser
        format_instruction = self.task_parser.get_format_instructions()
                
        return chain.invoke({"bio": user.bio,
                            "prompt": user.prompt,
                            "task": task_name,
                            "format_instruction": format_instruction})

    def generate_subtask(self, subtask_name: str, supertask: Task | Subtask) -> Subtask:
        chain = self.get_prompt_template() | self.llm | self.subtask_parser
        format_instruction = self.subtask_parser.get_format_instructions()
        
        subtask = chain.invoke({"bio": Userdata.bio,
                            "scenes": Userdata.scenes,
                            "task": subtask_name,
                            "format_instruction": format_instruction})
        
        subtask.set_supertask(supertask, 'task')
        return subtask