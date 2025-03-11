from typing import Union, Any, List, TYPE_CHECKING, Optional
from .BaseTask import BaseTask

if TYPE_CHECKING:
    from .Task import Task

class Subtask(BaseTask):
    """
    더 큰 작업 내의 하위 작업을 나타냅니다.
    
    Attributes:
        name (str): 하위 작업의 이름.
        id (Optional[Union[int, str]]): 하위 작업의 고유 식별자.
        index (Optional[int]): 상위 작업 내 하위 작업의 인덱스.
        context (Optional[str]): 하위 작업에 대한 설명 또는 컨텍스트.

        location_tags (List[str]): 하위 작업 위치와 관련된 태그.
        time_tags (List[str]): 하위 작업 시간과 관련된 태그.
        other_tags (List[str]): 기타 관련 태그.
        estimated_minutes (int): 하위 작업 완료 예상 시간(분).

        has_subtasks (bool): 하위 작업에 자체 하위 작업이 있는지 여부.
        subtasks (Optional[List['Subtask']]): 이 하위 작업에 속하는 하위 작업 목록.

        supertask_id (Optional[Union[int, str]]): 상위 작업의 ID.
        supertask_type (Optional[str]): 상위 작업의 유형.
    """
    # 하위 작업의 기본 정보
    index: int = 0
    
    # 하위 작업의 하위 작업
    has_subtasks: bool = False
    subtasks: List['Subtask'] = []
    
    # 하위 작업의 상위
    supertask_id: Union[int, str] = 0
    supertask_type: str = ""
    
    _supertask: Any = None
    
    def __init__(self, name: str, **kwargs):
        """
        주어진 이름으로 새 하위 작업을 초기화합니다.

        Args:
            name (str): 하위 작업의 이름.
        """
        super().__init__(name=name, **kwargs)
    
    def get_supertask(self) -> Any:
        """이 하위 작업의 상위 작업을 반환합니다."""
        return self._supertask
    
    def set_supertask(self, task: Any, task_type: str) -> None:
        """이 하위 작업의 상위 작업을 설정합니다.

        Args:
            task (Any): 상위 작업 객체.
            task_type (str): 상위 작업의 유형.
        """
        self._supertask = task
        self.supertask_id = getattr(task, 'id', None)
        self.supertask_type = task_type
    
    def set_supertask_of_subtasks(self) -> None:
        """모든 하위 작업의 상위 작업을 재귀적으로 설정합니다."""
        if self.has_subtasks:
            for subtask in self.subtasks:
                subtask.set_supertask(self, 'subtask')
                subtask.set_supertask_of_subtasks()
    
    def add_subtask(self, subtask: 'Subtask') -> None:
        """이 하위 작업에 하위 작업을 추가합니다.

        Args:
            subtask (Subtask): 추가할 하위 작업.
        """
        if not self.has_subtasks:
            self.subtasks = []
            self.has_subtasks = True
        super().add_subtask(subtask)
        subtask.set_supertask(self, 'subtask')
    
    def print_self(self) -> None:
        """하위 작업의 세부 정보(하위 작업 포함)를 출력합니다."""
        print(f"Subtask_{self.index}: {self.name}")
        print(f"- Context: {self.context}")
        print(f"- Location Tags: {self.location_tags}")
        print(f"- Time Tags: {self.time_tags}")
        print(f"- Other Tags: {self.other_tags}")
        print(f"- Estimated Minutes: {self.estimated_minutes}")
        print(f"- Supertask: {self.supertask_id} ({self.supertask_type})")
        print()
        
        if self.has_subtasks:
            print("Subtasks:")
            for subtask in self.subtasks:
                subtask.print_self()
    
    def get_subtask(self, index: int) -> 'Subtask':
        """주어진 인덱스의 하위 작업을 반환합니다.

        Args:
            index (int): 검색할 하위 작업의 인덱스.

        Returns:
            Subtask: 지정된 인덱스의 하위 작업.

        Raises:
            ValueError: 하위 작업에 하위 작업이 없는 경우.
            IndexError: 인덱스가 범위를 벗어난 경우.
        """
        if not self.has_subtasks:
            raise ValueError("This subtask has no subtasks.")
        return super().get_subtask(index)
    
    def get_all_subtasks(self) -> List['Subtask']:
        """하위 하위 작업을 포함한 모든 하위 작업 목록을 반환합니다.

        Returns:
            List[Subtask]: 모든 하위 작업이 포함된 목록.
        """
        all_subtasks: List['Subtask'] = []
        
        if self.has_subtasks:
            all_subtasks = self.subtasks.copy()    
            for subtask in self.subtasks:
                all_subtasks += subtask.get_all_subtasks()
            
        return all_subtasks
    
    def update_total_minutes(self) -> None:
        """하위 작업을 기반으로 총 예상 시간을 계산하고 설정합니다."""
        if self.has_subtasks:
            self.estimated_minutes = sum([subtask.estimated_minutes for subtask in self.subtasks])
            
            for subtask in self.subtasks:
                subtask.update_total_minutes()
    
    def update_subtask(self, index: int, subtask: 'Subtask') -> None:
        """주어진 인덱스의 하위 작업을 새 하위 작업으로 업데이트합니다.

        Args:
            index (int): 업데이트할 하위 작업의 인덱스.
            subtask (Subtask): 이전 항목을 대체할 새 하위 작업.

        Raises:
            ValueError: 하위 작업에 하위 작업이 없는 경우.
            IndexError: 인덱스가 범위를 벗어난 경우.
        """
        if not self.has_subtasks:
            raise ValueError("This subtask has no subtasks.")
        super().update_subtask(index, subtask)
        subtask.set_supertask(self, 'subtask')

    def remove_subtask(self, index: int) -> None:
        """주어진 인덱스의 하위 작업을 제거합니다.

        Args:
            index (int): 제거할 하위 작업의 인덱스.

        Raises:
            IndexError: 제거할 하위 작업이 없거나 인덱스가 범위를 벗어난 경우.
        """
        if not self.has_subtasks:
            raise IndexError("There are no subtasks to remove.")
        super().remove_subtask(index)
    
    def clear_subtasks(self) -> None:
        """이 하위 작업의 모든 하위 작업을 재귀적으로 지웁니다."""
        if self.has_subtasks:
            for subtask in self.subtasks:
                subtask.clear_subtasks()
        
            super().clear_subtasks()
            self.has_subtasks = False

    def count_subtasks(self) -> int:
        """이 하위 작업의 하위 작업 수를 계산합니다.

        Returns:
            int: 하위 작업 수.
        """
        return len(self.subtasks) if self.has_subtasks else 0