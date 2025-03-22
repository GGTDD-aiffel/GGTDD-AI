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
        다음은 사용자가 입력한 해야 할 일입니다. 이 할 일에 대한 구체적인 서브태스크를 주어진 숫자에 맞추어 작성하세요.
        단, 생성할 서브태스크의 수가 0으로 주어진다면 서브태스크를 생성하지 않고, 태스크만 생성합니다.
        서브태스크에만 존재하는 필드를 태스크에 생성하지 않도록 주의하세요.

        Context는 사용자의 하루에 비추어 해당하는 할 일을 수행하는 맥락을 나타냅니다.
        시간 태그에는 휴일 여부, 요일, 하루 중의 시간대 등의 정보를 포함하세요.
        공간 태그에는 사용자의 위치, 활동하는 장소 등의 정보를 포함하세요.
        기타 태그에는 시간과 공간 태그에 포함되지 않지만 할 일의 맥락과 상황을 검색하기에 좋은 정보를 포함하세요.
        각각의 태그는 되도록이면 사용자의 인적 정보에 포함되어 있는 태그 정보를 활용하여 작성하세요.
        위 내용은 태스크와 서브태스크에 공통으로 적용됩니다.
        
        서브태스크를 생성할 때에는, 각 서브태스크를 수행하는 데에 필요한 노력과 시간을 고려하세요.
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
        할 일을 생성하기 위한 프롬프트를 설정합니다.
        
        Args:
            prompt (str): 할 일을 생성하기 위한 프롬프트트
        """
        self.prompt_main = prompt
        self._prompt_template = self._create_prompt_template()
    
    def set_context_prompt(self, prompt_context: str) -> None:
        """
        할 일을 생성하기 위한 컨텍스트 프롬프트를 설정합니다.
        
        Args:
            prompt_context (str): 할 일을 생성하기 위한 컨텍스트 프롬프트
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
        task.update_estimated_minutes()
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
        task_to_breakdown.update_estimated_minutes()
        
        # 전체 태스크 소요시간 업데이트
        if isinstance(task_to_breakdown, Subtask):
            task_to_breakdown.update_estimated_minutes_all()
        else:
            task_to_breakdown.update_estimated_minutes()
        
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