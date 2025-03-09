from pydantic import BaseModel
from typing import Optional, Union, Any, List
from tasks.Task import Task

class Subtask(BaseModel):
    """
    Represents a subtask within a larger task.
    
    Attributes:
        name (str): The name of the subtask.
        id (Optional[Union[int, str]]): A unique identifier for the subtask.
        index (Optional[int]): The index of the subtask within its parent task.
        context (Optional[str]): A description or context for the subtask.

        location_tags (List[str]): Tags related to the location of the subtask.
        time_tags (List[str]): Tags related to the time of the subtask.
        other_tags (List[str]): Other relevant tags for the subtask.
        estimated_minutes (int): The estimated time in minutes to complete the subtask.

        has_subtasks (bool): Indicates whether the subtask has its own subtasks.
        subtasks (Optional[List['Subtask']]): A list of subtasks belonging to this subtask.

        supertask_id (Optional[Union[int, str]]): The ID of the parent task.
        supertask_type (Optional[str]): The type of the parent task.
    """
    # basic information of the subtask
    name: str
    id: Optional[Union[int, str]] = None
    index: Optional[int] = None
    context: Optional[str] = None
    
    # tags of the subtask
    location_tags: List[str] = []
    time_tags: List[str] = []
    other_tags: List[str] = []
    estimated_minutes: int = 0
    
    # subtasks of the subtask
    has_subtasks: bool = False
    subtasks: Optional[List['Subtask']] = None
    
    # super of the subtask
    supertask_id: Optional[Union[int, str]] = None
    supertask_type: Optional[str] = None
    
    _supertask: Any = None
    
    def get_supertask(self) -> Any:
        """Returns the parent task of this subtask."""
        return self._supertask
    
    def set_supertask(self, task: Any, task_type: str) -> None:
        """Sets the parent task of this subtask.

        Args:
            task (Any): The parent task object.
            task_type (str): The type of the parent task.
        """
        self._supertask = task
        self.supertask_id = getattr(task, 'id', None)
        self.supertask_type = task_type
        
    def set_supertask_of_subtasks(self) -> None:
        """Recursively sets the supertask of all subtasks."""
        if self.has_subtasks and self.subtasks is not None:
            for subtask in self.subtasks:
                subtask.set_supertask(self, 'subtask')
                subtask.set_supertask_of_subtasks()
    
    def add_subtask(self, subtask: 'Subtask') -> None:
        """Adds a subtask to this subtask.

        Args:
            subtask (Subtask): The subtask to add.
        """
        if self.subtasks is None:
            self.subtasks = []
        if not self.has_subtasks:
            self.has_subtasks = True
        self.subtasks.append(subtask)
    
    def set_subtasks_index(self) -> None:
        """Sets the index of each subtask in the subtasks list."""
        if self.subtasks is not None:
            for i, subtask in enumerate(self.subtasks):
                subtask.index = (i + 1)
    
    def print_self(self) -> None:
        """Prints the subtask's details, including its subtasks."""
        print(f"Subtask_{self.index}: {self.name}")
        print(f"- Context: {self.context}")
        print(f"- Location Tags: {self.location_tags}")
        print(f"- Time Tags: {self.time_tags}")
        print(f"- Other Tags: {self.other_tags}")
        print(f"- Estimated Minutes: {self.estimated_minutes}")
        print(f"- Supertask: {self.supertask_id} ({self.supertask_type})")
        print()
        
        if self.has_subtasks and self.subtasks is not None:
            print("Subtasks:")
            for subtask in self.subtasks:
                subtask.print_self()
    
    def get_subtask(self, index: int) -> 'Subtask':
        """Returns a subtask at the given index.

        Args:
            index (int): The index of the subtask to retrieve.

        Returns:
            Subtask: The subtask at the specified index.

        Raises:
            ValueError: If the subtask has no subtasks.
            IndexError: If the index is out of bounds.
        """
        if not self.has_subtasks or self.subtasks is None:
            raise ValueError("This subtask has no subtasks.")
        if index < 0 or index >= len(self.subtasks):
            raise IndexError("Index out of bounds.")
        return self.subtasks[index]
    
    def get_all_subtasks(self) -> List['Subtask']:
        """Returns a list of all subtasks, including sub-subtasks.

        Returns:
            List[Subtask]: A list containing all subtasks.
        """
        subtasks: List['Subtask'] = []
        
        if self.has_subtasks and self.subtasks is not None:
            subtasks = self.subtasks.copy()    
            for subtask in self.subtasks:
                subtasks += subtask.get_all_subtasks()
            
        return subtasks
    
    def set_total_estimated_minutes(self) -> None:
        """Calculates and sets the total estimated minutes based on its subtasks."""
        if self.has_subtasks and self.subtasks is not None:
            self.estimated_minutes = sum([subtask.estimated_minutes for subtask in self.subtasks])
            
            for subtask in self.subtasks:
                subtask.set_total_estimated_minutes()

    def update_subtask(self, index: int, subtask: 'Subtask') -> None:
        """Updates a subtask at the given index with a new subtask.

        Args:
            index (int): The index of the subtask to update.
            subtask (Subtask): The new subtask to replace the old one.

        Raises:
            ValueError: If the subtask has no subtasks.
            IndexError: If the index is out of bounds.
        """
        if not self.has_subtasks or self.subtasks is None:
            raise ValueError("This subtask has no subtasks.")
        if index < 0 or index >= len(self.subtasks):
            raise IndexError("Index out of bounds.")
        self.subtasks[index] = subtask
        subtask.set_supertask(self, 'subtask')
    
    def remove_subtask(self, index: int) -> None:
        """Removes a subtask at the given index.

        Args:
            index (int): The index of the subtask to remove.

        Raises:
            IndexError: If the index is out of bounds.
        """
        if self.subtasks is None:
            raise IndexError("There are no subtasks to remove.")
        if index < 0 or index >= len(self.subtasks):
            raise IndexError("Index out of bounds.")
        del self.subtasks[index]
        self.set_subtasks_index()
    
    def clear_subtasks(self) -> None:
        """Clears all subtasks of this subtask recursively."""
        if self.subtasks is not None:
            for subtask in self.subtasks:
                subtask.clear_subtasks()
        
            self.subtasks.clear()
            self.has_subtasks = False

    def count_subtasks(self) -> int:
        """Counts the number of subtasks of this subtask.

        Returns:
            int: The number of subtasks.
        """
        return len(self.subtasks) if self.subtasks is not None else 0

Subtask.model_rebuild()