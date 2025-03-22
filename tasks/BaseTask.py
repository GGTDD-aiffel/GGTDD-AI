from pydantic import BaseModel
from typing import Union, List, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .Task import Task
    from .Subtask import Subtask

class BaseTask(BaseModel):
    """
    Task와 Subtask의 공통 기능과 구조를 제공하는 추상 기본 클래스입니다.
    
    이 클래스는 작업 관리 시스템의 기반이 되는 공통 속성과 메서드를 정의합니다.
    직접 인스턴스화하지 않으며, 항상 Task나 Subtask 클래스를 통해 사용합니다.
    
    Attributes:
        name (str): 작업의 이름.
        id (Union[int, str]): 작업의 고유 식별자 (기본값: 0).
        context (str): 작업에 대한 설명이나 배경 정보 (기본값: "").
        
        location_tags (List[str]): 작업 수행 위치와 관련된 태그 (기본값: []).
        time_tags (List[str]): 작업 수행 시간과 관련된 태그 (기본값: []).
        other_tags (List[str]): 기타 관련 태그 (기본값: []).
        estimated_minutes (int): 작업 완료 예상 시간(분) (기본값: 0).
        
        has_subtasks (bool): 이 작업에 하위 작업이 있는지 여부 (기본값: False).
        subtasks (List["Subtask"]): 이 작업에 속하는 하위 작업 목록 (기본값: []).
    
    Notes:
        'get_all_subtasks', 'set_supertask_of_subtasks' 메서드는 서브클래스에서 구현해야 합니다.
    """
    name: str
    id: Union[int, str] = 0
    context: str = ""
    
    location_tags: List[str] = []
    time_tags: List[str] = []
    other_tags: List[str] = []
    estimated_minutes: int = 0

    has_subtasks: bool = False
    subtasks: List["Subtask"] = []
    
    comments: List[str] = []
    
    def add_subtask(self, subtask: "Subtask") -> None:
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
        
    def update_estimated_minutes(self) -> int:
        """자신을 포함한 모든 하위작업의 estimated_minutes를 하위작업 기반으로 업데이트합니다.
        
        Returns:
            int: 업데이트된 총 예상 시간(분).
        """
        if not self.has_subtasks or not self.subtasks:
            return self.estimated_minutes
            
        # 후위 순회(post-order traversal) 방식으로 구현
        stack = []
        visited = set()  # 객체 ID를 저장할 셋
        current = self
        
        # 깊이 우선 탐색으로 모든 노드 처리
        while True:
            # 현재 노드의 모든 첫번째 자식 노드를 스택에 추가
            if current.has_subtasks and id(current) not in visited:
                stack.append(current)
                visited.add(id(current))  # 객체 대신 ID 저장
                if current.subtasks:
                    current = current.subtasks[0]
                    continue # 다음 자식 노드로 이동
            
            # 현재 노드가 하위 작업을 가지고 있다면, 모든 하위 작업의 시간 합계로 업데이트
            if current.has_subtasks:
                current.estimated_minutes = sum(subtask.estimated_minutes for subtask in current.subtasks)
            
            # 스택이 비어있으면 종료
            if not stack:
                break
                
            # 다음 처리할 노드 결정
            parent = stack[-1]
            if parent.subtasks.index(current) + 1 < len(parent.subtasks):
                # 다음 형제 노드로 이동
                current = parent.subtasks[parent.subtasks.index(current) + 1]
            else:
                # 부모 노드로 돌아감
                current = stack.pop()
        
        return self.estimated_minutes
    
    def add_comments(self, comment: str) -> None:
        """
        주어진 댓글을 작업에 추가합니다.
        
        Args:
            comment (str): 추가할 댓글.
        """
       
        self.comments.append(comment)
    
    def clear_comments(self) -> None:
        """
        모든 댓글을 제거합니다.
        """
        self.comments.clear()
    
    def delete_comments(self, index: int) -> None:
        """
        특정 인덱스의 댓글을 제거합니다.
        
        Args:
            index (int): 제거할 댓글의 인덱스.
        """
        if index < 0 or index >= len(self.comments):
            raise IndexError("Index out of bounds.")
        del self.comments[index]
    
    def update_comments(self, index: int, comment: str) -> None:
        """
        특정 인덱스의 댓글을 업데이트합니다.
        
        Args:
            index (int): 업데이트할 댓글의 인덱스.
            comment (str): 새 댓글.
        """
        if index < 0 or index >= len(self.comments):
            raise IndexError("Index out of bounds.")
        self.comments[index] = comment
    
    def get_comments(self, index: int) -> str:
        """
        특정 인덱스의 댓글을 반환합니다.
        
        Args:
            index (int): 가져올 댓글의 인덱스.
            
        Returns:
            str: 댓글.
        """
        if index < 0 or index >= len(self.comments):
            raise IndexError("Index out of bounds.")
        return self.comments[index]
    
    def get_all_commnets(self) -> List[str]:
        """
        모든 댓글을 반환합니다.
        
        Returns:
            List[str]: 모든 댓글.
        """
        return self.comments