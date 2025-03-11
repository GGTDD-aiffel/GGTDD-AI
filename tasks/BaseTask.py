from pydantic import BaseModel
from typing import Union, List, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .Task import Task
    from .Subtask import Subtask

class BaseTask(BaseModel):
    """
    Task와 Subtask의 공통 기능을 제공하는 기본 클래스입니다.
    
    Attributes:
        name (str): 작업의 이름.
        id (Union[int, str]): 작업의 고유 식별자.
        context (str): 작업에 대한 설명 또는 컨텍스트.
        location_tags (List[str]): 작업 위치와 관련된 태그.
        time_tags (List[str]): 작업 시간과 관련된 태그.
        other_tags (List[str]): 기타 관련 태그.
        estimated_minutes (int): 작업 완료 예상 시간(분).
    """
    name: str
    id: Union[int, str] = 0
    context: str = ""
    
    location_tags: List[str] = []
    time_tags: List[str] = []
    other_tags: List[str] = []
    estimated_minutes: int = 0
    
    # 타입 힌팅을 위한 subtasks 선언 - 실제 구현은 서브클래스에서
    subtasks: List[Any] = []
    
    def add_subtask(self, subtask: Any) -> None:
        """
        새 하위 작업을 추가합니다.
        
        Args:
            subtask: 추가할 하위 작업.
        """
        self.subtasks.append(subtask)
    
    def set_subtasks_index(self) -> None:
        """
        모든 하위 작업의 인덱스 값을 위치에 따라 업데이트합니다.
        """
        for i, subtask in enumerate(self.subtasks):
            subtask.index = i + 1
            if hasattr(subtask, 'has_subtasks') and subtask.has_subtasks:
                subtask.set_subtasks_index()
    
    def get_subtask(self, index: int) -> Any:
        """
        특정 인덱스의 하위 작업을 반환합니다.
        
        Args:
            index (int): 가져올 하위 작업의 인덱스(0부터 시작).
            
        Returns:
            하위 작업 객체.
            
        Raises:
            IndexError: 인덱스가 범위를 벗어난 경우.
        """
        if index < 0 or index >= len(self.subtasks):
            raise IndexError("Index out of bounds.")
        return self.subtasks[index]
    
    def remove_subtask(self, index: int) -> None:
        """
        특정 인덱스의 하위 작업을 제거합니다.
        
        Args:
            index (int): 제거할 하위 작업의 인덱스.
            
        Raises:
            IndexError: 인덱스가 범위를 벗어난 경우.
        """
        if index < 0 or index >= len(self.subtasks):
            raise IndexError("Index out of bounds.")
        del self.subtasks[index]
        self.set_subtasks_index()
    
    def update_subtask(self, index: int, subtask: Any) -> None:
        """
        특정 인덱스의 하위 작업을 업데이트합니다.
        
        Args:
            index (int): 업데이트할 하위 작업의 인덱스.
            subtask: 새 하위 작업.
            
        Raises:
            IndexError: 인덱스가 범위를 벗어난 경우.
        """
        if index < 0 or index >= len(self.subtasks):
            raise IndexError("Index out of bounds.")
        self.subtasks[index] = subtask
    
    def get_all_subtasks(self) -> List[Any]:
        """
        중첩된 하위 작업을 포함한 모든 하위 작업의 평면화된 목록을 반환합니다.
        
        Returns:
            List: 모든 하위 작업의 목록.
        """
        # 서브클래스에서 구현
        pass
    
    def print_self(self) -> None:
        """
        작업의 세부 정보를 출력합니다.
        """
        # 서브클래스에서 구현
        pass
    
    def clear_subtasks(self) -> None:
        """
        모든 하위 작업을 제거합니다.
        """
        self.subtasks.clear()
    
    def set_supertask_of_subtasks(self) -> None:
        """
        이 작업을 모든 하위 작업의 상위 작업으로 설정하고 하위로 전파합니다.
        """
        # 서브클래스에서 구현
        pass
        
    def update_total_minutes(self) -> None:
        """
        하위 작업을 기반으로 예상 시간을 업데이트합니다.
        """
        # 서브클래스에서 구현
        pass