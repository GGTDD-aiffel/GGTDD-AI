from LLMs.BaseLLMProcessor import BaseLLMProcessor
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import Optional, Dict, Any, List

from tasks.Task import *
from tasks.Subtask import *
from userdata import *

class TaskCommenter(BaseLLMProcessor):
    def __init__(self, llm: ChatOpenAI):
        super().__init__(llm)
        
        self.prompt_main = """
        다음은 사용자의 할 일입니다. 사용자는 해당 할 일을 수행하는 데에 도움이 되는 조언을 얻고자 합니다.
        사용자의 인적 정보와 하루 일과를 고려하여, 사용자에게 유용한 조언을 작성해주세요.
        """
        
        self.prompt_kwargs = """
        사용자의 인적 정보: {bio}
        사용자의 하루 일과: {prompt}
        사용자가 입력한 할 일: {task}
        """
    
        self.comment_parser = StrOutputParser()
        self._prompt_template = self._create_prompt_template()
    
    def _process_default(self, user: User, task_to_comment: Task|Subtask) -> str:
        """
        주어진 사용자 정보와 할 일 정보를 사용하여 사용자에게 도움이 될 수 있는 코멘트를 생성합니다.
        
        Args:
            user (User): 사용자 정보
            task_to_comment (Task|Subtask): 코멘트를 생성할 태스크 또는 서브태스크
           
        Returns:
            str: 생성된 코멘트
        """
        if not task_to_comment or not task_to_comment.name.strip():
            raise ValueError("태스크 또는 서브태스크 이름은 비어 있을 수 없습니다.")
            
        chain = self._prompt_template | self.llm | self.comment_parser
                
        comment = chain.invoke({
            "bio": user.bio,
            "prompt": user.prompt,
            "task": task_to_comment,
        })
        
        task_to_comment.comments.append(comment)
        
        return comment