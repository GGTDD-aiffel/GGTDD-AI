from typing import Union, Any, List, TYPE_CHECKING, Optional
from .BaseTask import BaseTask

if TYPE_CHECKING:
    from .Task import Task

class Subtask(BaseTask):
    """
    상위 작업(Task 또는 다른 Subtask) 내의 하위 작업을 나타내는 클래스입니다.
    
    Subtask는 BaseTask를 상속받아 기본 속성(이름, 태그 등)을 포함하며,
    상위 작업과의 관계 관리 및 중첩된 하위 작업 지원 기능을 추가합니다.
    
    Attributes:
        모든 BaseTask 속성을 상속받습니다.
        
        index (int): 상위 작업 내에서의 순서를 나타내는 인덱스 (기본값: 0).
        supertask_id (Union[int, str]): 상위 작업의 ID (기본값: 0).
        supertask_type (str): 상위 작업의 유형 ('task' 또는 'subtask') (기본값: "").
        _supertask (Any): 상위 작업에 대한 내부 참조 (기본값: None).
    
    Methods:
        get_supertask: 상위 작업 객체를 반환합니다.
        get_supermosttask: 재귀적으로 최상위 Task를 반환합니다.
        set_supertask: 상위 작업 참조와 관련 정보를 설정합니다.
        set_supertask_of_subtasks: 이 Subtask를 하위 Subtask들의 상위 작업으로 설정합니다.
        add_subtask: 새 Subtask를 이 Subtask의 하위 작업으로 추가합니다.
        get_all_subtasks: 모든 중첩된 하위 Subtask의 평면화된 목록을 반환합니다.
        update_total_minutes: 모든 하위 Subtask의 예상 시간을 합산하여 자신의 예상 시간을 업데이트합니다.
        count_subtasks: 직접적인 하위 Subtask의 수를 반환합니다.
    """
    # 하위 작업의 기본 정보
    index: int = 0
    supertask_id: Union[int, str] = 0
    supertask_type: str = ""
    
    # 하위 작업의 하위 작업
    subtasks: List['Subtask'] = []
    
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
    
    def get_supermosttask(self) -> 'Task':
        """이 하위 작업의 최상위 작업을 반환합니다."""
        from .Task import Task
        
        supertask = self.get_supertask()
        
        if supertask is None:
            raise ValueError("This subtask has no supertask.")
        
        while not isinstance(supertask, Task):
            if not hasattr(supertask, 'get_supertask'):
                raise ValueError(f"Unexpected supertask type: {type(supertask)}")

            supertask = supertask.get_supertask()
            
            if supertask is None:
                raise ValueError("Supertask chain broken before reaching Task")
            
        return supertask

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
    
    def __str__(self) -> str:
        """
        하위 작업의 문자열 표현을 반환합니다.
        """
        result = [f"Subtask_{self.index}: {self.name}"]
        result.append(f"- Context: {self.context}")
        result.append(f"- Location Tags: {self.location_tags}")
        result.append(f"- Time Tags: {self.time_tags}")
        result.append(f"- Other Tags: {self.other_tags}")
        result.append(f"- Estimated Minutes: {self.estimated_minutes}")
        result.append(f"- Supertask: {self.supertask_id} ({self.supertask_type})")
        result.append("")
        
        if self.has_subtasks and self.subtasks:
            result.append("Subtasks:")
            for subtask in self.subtasks:
                # 들여쓰기를 적용하여 계층 구조 표현
                subtask_str = str(subtask).replace("\n", "\n  ")
                result.append(f"  {subtask_str}")
        
        return "\n".join(result)
    
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