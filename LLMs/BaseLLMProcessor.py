from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import Any, Optional

class BaseLLMProcessor:
    """
    LLM을 활용한 처리를 위한 기본 클래스입니다.
    
    이 클래스는 LLM 기반 처리기의 공통 기능인 프롬프트 관리, 
    LLM 호출 및 결과 처리를 위한 기본 구조를 제공합니다.
    """
    
    def __init__(self, llm: ChatOpenAI):
        """
        LLM 처리기를 초기화합니다.
        
        Args:
            llm (ChatOpenAI): 사용할 LLM 인스턴스
        """
        self.llm = llm
        self.prompt_main = ""
        self.prompt_kwargs = ""
        self._prompt_template = self._create_prompt_template()
    
    def _create_prompt_template(self) -> ChatPromptTemplate:
        """
        현재 프롬프트 설정으로 ChatPromptTemplate 객체를 생성합니다.
        
        Returns:
            ChatPromptTemplate: 현재 설정으로 생성된 프롬프트 템플릿
        """
        template_str = f"{self.prompt_main}\n{self.prompt_kwargs}"
        return ChatPromptTemplate.from_template(template_str)
    
    def set_main_prompt(self, prompt: str) -> None:
        """
        메인 프롬프트를 설정합니다.
        
        Args:
            prompt (str): 메인 프롬프트
        """
        self.prompt_main = prompt
        self._prompt_template = self._create_prompt_template()
    
    def set_context_prompt(self, prompt_context: str) -> None:
        """
        컨텍스트 프롬프트를 설정합니다.
        
        Args:
            prompt_context (str): 컨텍스트 프롬프트
        """
        self.prompt_kwargs = prompt_context
        self._prompt_template = self._create_prompt_template()
        
    def process(self, **kwargs) -> Any:
        """
        LLM을 사용하여 주어진 입력을 처리합니다.
        하위 클래스에서 구현해야 합니다.
        
        Returns:
            Any: 처리 결과
        """
        raise NotImplementedError("이 메서드는 하위 클래스에서 구현해야 합니다.")