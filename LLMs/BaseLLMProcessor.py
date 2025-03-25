from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import Any, Optional
import concurrent.futures
from concurrent.futures import TimeoutError

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
        
    def process(self, processor_func=None, timeout: Optional[float] = None, **kwargs) -> Any:
        """
        LLM을 사용하여 주어진 입력을 처리합니다.
        
        Args:
            processor_func (Callable): 실행할 처리 함수, None이면 기본 처리 사용
            timeout (Optional[float]): 처리 작업이 완료되어야 하는 최대 시간(초)
            **kwargs: 처리에 필요한 추가 매개변수
        """
        # 기본 처리 함수 설정
        if processor_func is None:
            processor_func = self._process_default
        
        if timeout is None:
            return processor_func(**kwargs)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(processor_func, **kwargs)
            try:
                return future.result(timeout=timeout)
            except concurrent.futures.TimeoutError:
                raise TimeoutError(f"처리 작업이 {timeout}초 내에 완료되지 않았습니다.")
                
    def _process_default(self, **kwargs) -> Any:
        """기본 처리 로직"""
        raise NotImplementedError("기본 처리 로직이 구현되지 않았습니다.")