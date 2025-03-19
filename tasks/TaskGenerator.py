from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from typing import Optional, Dict, Any, List
import json

from .Task import *
from .Subtask import *
from userdata import *

class TaskGenerator:
    def __init__(self, llm: ChatOpenAI):
        """
        Initialize a new task generator with the given LLM instance.
        
        Args:
            llm (ChatOpenAI): The LLM instance to use for generating tasks.
        """
        self.llm = llm
        
        # 프롬프트 기본값 설정
        self.prompt_main: str = """
        다음은 사용자가 입력한 해야 할 일입니다. 이 할 일을 세부적으로 나누어 작성하세요.
        각각의 할 일은 최대한 구체적인 행동으로 작성하고, 이를 수행하는 데 필요한 시간과 노력을 고려하여 작성하세요.
        할 일을 세부적으로 나누면 사용자가 할 일을 더 쉽게 완료할 수 있습니다.

        각각의 할 일은 사용자의 하루를 나타내는 여러 장면을 담은 태그와 함께 저장되고, 사용자가 처한 맥락과 상황을 표현하는 태그에 맞춰 할 일을 추천합니다.
        각각의 할 일은 사용자의 위치, 활동하는 장소, 시간대 등을 고려하여 태그를 부여하세요.

        Task의 context에서는 사용자 정보와 하루 일과에 기반하여 해당 할 일을 언제 하는 것이 좋을지 설명하세요.
        각각의 Subtask에 적절한 태그를 부여하세요.
        """
        
        self.prompt_kwargs: str = """
        사용자의 인적 정보: {bio}
        사용자의 하루 일과: {prompt}
        사용자가 입력한 할 일: {task}
        생성할 서브태스크의 수: {subtask_num}
        지침: {format_instruction}
        """
        
        # 파서 초기화
        self.task_parser = PydanticOutputParser(pydantic_object=Task)
        self.subtask_parser = PydanticOutputParser(pydantic_object=Subtask)
        
        # 프롬프트 템플릿 초기화
        self._prompt_template = self._create_prompt_template()
    
    def _create_prompt_template(self) -> ChatPromptTemplate:
        """
        현재 프롬프트 설정으로 ChatPromptTemplate 객체 생성
        
        Returns:
            ChatPromptTemplate: 현재 설정으로 생성된 프롬프트 템플릿
        """
        template_str = f"{self.prompt_main}\n{self.prompt_kwargs}"
        return ChatPromptTemplate.from_template(template_str)
        
    def set_main_prompt(self, prompt: str) -> None:
        """
        Set the prompt to use for generating tasks.
        
        Args:
            prompt (str): The prompt to use for generating tasks.
        """
        self.prompt_main = prompt
        self._prompt_template = self._create_prompt_template()
    
    def set_context_prompt(self, prompt_context: str) -> None:
        """
        Set the context prompt to use for generating tasks.
        
        Args:
            prompt_context (str): The context prompt to use for generating tasks.
        """
        self.prompt_kwargs = prompt_context
        self._prompt_template = self._create_prompt_template()

    def generate_task(self, user: User, task_name: str, subtask_num = 5) -> Task:
        """
        주어진 사용자 정보와 태스크 이름을 사용하여 태스크를 생성합니다.
        
        Args:
            user (User): 사용자 정보
            task_name (str): 생성할 태스크의 이름
            subtask_num (int): 생성할 서브태스크의 수
            
        Returns:
            Task: 생성된 태스크 객체
        """
        if not task_name or not task_name.strip():
            raise ValueError("태스크 이름은 비어 있을 수 없습니다.")
            
        chain = self._prompt_template | self.llm | self.task_parser
        format_instruction = self.task_parser.get_format_instructions()
                
        task = chain.invoke({
            "bio": user.bio,
            "prompt": user.prompt,
            "task": task_name,
            "subtask_num": subtask_num,
            "format_instruction": format_instruction})
        
        task.set_supertask_of_subtasks()
        task.set_subtasks_index()
        task.update_total_minutes()
        return task

    def generate_subtasks(self, user: User, task_to_breakdown: Task|Subtask, subtask_num=3) -> Task|Subtask:
        """
        주어진 사용자 정보와 태스크를 세부적으로 나눕니다.
        
        Args:
            user (User): 사용자 정보
            task_to_breakdown (Task|Subtask): 세부적으로 나눌 태스크
            subtask_num (int): 생성할 서브태스크의 수
        """
        if not task_to_breakdown:
            raise ValueError("세부적으로 나눌 태스크가 주어지지 않았습니다.")
        
        # LLM에서 문자열 응답 직접 가져오기 
        from langchain_core.output_parsers import StrOutputParser
        str_parser = StrOutputParser()
        chain = self._prompt_template | self.llm | str_parser
        format_instruction = self.subtask_parser.get_format_instructions()
        
        # LLM 호출 및 응답 가져오기
        raw_output = chain.invoke({
            "bio": user.bio,
            "prompt": user.prompt, 
            "task": str(task_to_breakdown),
            "subtask_num": subtask_num,
            "format_instruction": format_instruction
        })
        
        # 커스텀 파서로 응답 처리
        subtasks = SubtaskParser.parse(raw_output)
        
        # 생성된 subtasks 설정
        task_to_breakdown.subtasks = subtasks
        task_to_breakdown.has_subtasks = len(subtasks) > 0
        
        # 관계 설정
        task_to_breakdown.set_supertask_of_subtasks()
        task_to_breakdown.set_subtasks_index()
        task_to_breakdown.update_total_minutes()
        
        # 전체 태스크 소요시간 업데이트
        if isinstance(task_to_breakdown, Subtask):
            supermosttask = task_to_breakdown.get_supermosttask()
        else:
            supermosttask = task_to_breakdown
        supermosttask.update_total_minutes()
        
        return task_to_breakdown

class SubtaskParser:
    """Subtask 객체를 생성하는 커스텀 파서 클래스"""
    
    @staticmethod
    def _create_subtask_from_dict(data: Dict[str, Any]) -> Subtask:
        """딕셔너리에서 Subtask 객체 생성"""
        # subtasks 필드를 임시로 빈 리스트로 설정
        has_nested_subtasks = False
        nested_subtasks_data = []
        
        if "subtasks" in data and data["subtasks"] and isinstance(data["subtasks"], list):
            has_nested_subtasks = True
            # subtasks는 나중에 처리하기 위해 임시 저장
            nested_subtasks_data = data["subtasks"]
        
        # 필수 필드가 없으면 기본값 제공
        name = data.get("name", "Unnamed Subtask")
        
        # Subtask 객체 생성
        subtask = Subtask(
            name=name,
            id=data.get("id", 0),
            index=data.get("index", 0),
            context=data.get("context", ""),
            location_tags=data.get("location_tags", []),
            time_tags=data.get("time_tags", []),
            other_tags=data.get("other_tags", []),
            estimated_minutes=data.get("estimated_minutes", 0),
            has_subtasks=has_nested_subtasks,
            subtasks=[],  # 빈 리스트로 초기화
            supertask_id=data.get("supertask_id", 0),
            supertask_type=data.get("supertask_type", "")
        )
        
        # 중첩된 subtasks 처리
        if has_nested_subtasks:
            for nested_data in nested_subtasks_data:
                nested_subtask = SubtaskParser._create_subtask_from_dict(nested_data)
                subtask.add_subtask(nested_subtask)
        
        return subtask
    
    @staticmethod
    def parse(llm_output: str) -> List[Subtask]:
        """LLM 출력을 파싱하여 Subtask 객체 목록 반환"""
        try:
            # 마크다운 코드 블록에서 JSON 추출
            import re
            json_match = re.search(r'```(?:json)?\s*([\s\S]+?)\s*```', llm_output)
            if json_match:
                # 코드 블록 내용만 추출
                json_str = json_match.group(1)
            else:
                # 코드 블록이 없으면 원래 문자열 사용
                json_str = llm_output
            
            # 공백 제거 및 JSON 파싱
            json_str = json_str.strip()
            data = json.loads(json_str)
            subtasks = []
            
            # 응답이 직접 subtasks 목록을 포함하는 경우
            if isinstance(data, dict) and "subtasks" in data and isinstance(data["subtasks"], list):
                for subtask_data in data["subtasks"]:
                    subtask = SubtaskParser._create_subtask_from_dict(subtask_data)
                    subtasks.append(subtask)
            # 응답 자체가 subtask 목록인 경우
            elif isinstance(data, list):
                for subtask_data in data:
                    subtask = SubtaskParser._create_subtask_from_dict(subtask_data)
                    subtasks.append(subtask)
            # 응답 자체가 단일 subtask인 경우
            else:
                subtask = SubtaskParser._create_subtask_from_dict(data)
                subtasks.append(subtask)
                    
            return subtasks
        except Exception as e:
            print(f"파싱 오류: {e}")
            # 디버깅용 출력
            print(f"LLM 출력: {llm_output}")
            return []