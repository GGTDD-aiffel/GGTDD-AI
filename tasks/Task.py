from pydantic import BaseModel
from typing import Optional, Union, List, TYPE_CHECKING

# 타입 체킹 시에만 import
if TYPE_CHECKING:
    from .Subtask import Subtask

class Task(BaseModel):
    """
    Represents a task with a name, optional ID, context, tags, estimated time, and subtasks.

    Attributes:
        name (str): The name of the task.
        id (Optional[Union[int, str]]): A unique identifier for the task.
        context (str): A description or context for the task.
        
        location_tags (List[str]): Tags related to the location of the task.
        time_tags (List[str]): Tags related to the time of the task.
        other_tags (List[str]): Other relevant tags for the task.
        estimated_minutes (int): The estimated time in minutes to complete the task.

        subtasks (List[Subtask]): A list of subtasks belonging to this task.
    """
    name: str
    id: Union[int, str] = 0
    context: str = ""

    location_tags: List[str] = []
    time_tags: List[str] = []
    other_tags: List[str] = []
    estimated_minutes: int = 0

    # 문자열 기반 타입 어노테이션 사용
    subtasks: List['Subtask'] = []
    
    def __init__(self, task_name: str):
        """
        Initialize a new task with the given name.

        Args:
            task_name (str): The name of the task.
        """
        super().__init__(name=task_name)
    
    def set_supertask_of_subtask(self) -> None:
        """
        Set this task as the parent of all its subtasks and propagate downward.
        """
        for subtask in self.subtasks:
            subtask.set_supertask(self, 'task')
            subtask.set_supertask_of_subtasks()
    
    def add_subtask(self, subtask: 'Subtask') -> None:
        """
        Add a new subtask to this task.

        Args:
            subtask (Subtask): The subtask to add.
        """
        self.subtasks.append(subtask)
        subtask.set_supertask(self, 'task')
        
    def set_subtask_index(self) -> None:
        """
        Update the index values for all subtasks based on their position.
        """
        for i, subtask in enumerate(self.subtasks):
            subtask.index = (i + 1)
        
    def get_subtask(self, index: int) -> 'Subtask':
        """
        Get a specific subtask by its index (zero-based).

        Args:
            index (int): The index of the subtask to retrieve.

        Returns:
            Subtask: The subtask at the given index.

        Raises:
            IndexError: If the index is out of bounds.
        """
        if index < 0 or index >= len(self.subtasks):
            raise IndexError("Index out of bounds.")
        return self.subtasks[index]
    
    def get_all_subtasks(self) -> List['Subtask']:
        """
        Get all subtasks including nested subtasks in a flattened list.

        Returns:
            List[Subtask]: All subtasks at any nesting level.
        """
        all_subtasks: List['Subtask'] = []
        for subtask in self.subtasks:
            all_subtasks.append(subtask)
            all_subtasks.extend(subtask.get_all_subtasks())
        return all_subtasks
    
    def set_supertask(self) -> None:
        """
        Set the supertask for all subtasks.
        """
        for subtask in self.subtasks:
            subtask.supertask = self
            subtask.set_supertask()
    
    def print_self(self) -> None:
        """
        Print the task's details, including its subtasks.
        """
        print(f"Task: {self.name}")
        print(f"- Context: {self.context}")
        print(f"- Location Tags: {self.location_tags}")
        print(f"- Time Tags: {self.time_tags}")
        print(f"- Other Tags: {self.other_tags}")
        print(f"- Estimated Minutes: {self.estimated_minutes}")
        print()
        
        print("Subtasks:")
        for subtask in self.subtasks:
            subtask.print_self()
    
    def calculate_total_minutes(self) -> int:
        """
        Calculate the total estimated minutes from all subtasks without modifying self.

        Returns:
            int: Total estimated minutes.
        """
        total_minutes = 0
        for subtask in self.subtasks:
            subtask.set_total_estimated_minutes()
            total_minutes += subtask.estimated_minutes
        return total_minutes
    
    def update_total_minutes(self) -> None:
        """
        Update the estimated_minutes based on subtasks.
        """
        self.estimated_minutes = self.calculate_total_minutes()
    
    def update_subtask(self, index: int, subtask: 'Subtask') -> None:
        """
        Update a subtask at the given index with a new subtask.

        Args:
            index (int): The index of the subtask to update.
            subtask (Subtask): The new subtask to replace the old one.

        Raises:
            IndexError: If the index is out of bounds.
        """
        if index < 0 or index >= len(self.subtasks):
            raise IndexError("Index out of bounds.")
        self.subtasks[index] = subtask

    def remove_subtask(self, index: int) -> None:
        """
        Remove a subtask at the given index.

        Args:
            index (int): The index of the subtask to remove.

        Raises:
            IndexError: If the index is out of bounds.
        """
        if index < 0 or index >= len(self.subtasks):
            raise IndexError("Index out of bounds.")
        del self.subtasks[index]
        self.set_subtask_index()

    def clear_subtasks(self) -> None:
        """
        Clear all subtasks.
        """
        self.subtasks.clear()