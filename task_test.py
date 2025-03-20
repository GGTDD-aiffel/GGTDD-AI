import tasks, userdata
from langchain_openai import ChatOpenAI

scene_generator = userdata.SceneGenerator(llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5))
task_generator = tasks.TaskGenerator(llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5))

user = userdata.User(name="윤형석",
                     residence="서울",
                     birth_date="1990-03-28",
                     occupation="개발자",
                     personality=['Introverted', 'Intuitive', 'Thinking', 'Perceiving'],
                     prompt="",
                     positives=["지적 호기심", "사고력", "창의력"],
                     negatives=["ADHD", "불안", "피로감"])

scenes = scene_generator.generate_scenes(user=user,
                                         scenes=["출퇴근길",
                                                "근무",
                                                "휴식",
                                                "공부",
                                                "게임",
                                                "유튜브 시청",
                                                "애완동물 돌보기"])
user.append_scenes(scenes)
    
responses = user.generate_prompt()
user.set_prompt(responses=responses, index=0)

task = task_generator.generate_task(user=user, task_name="체중 감량을 위해 운동하기", subtask_num=0)
task_generator.generate_subtasks(user=user, task_to_breakdown=task, subtask_num=5)
task_generator.generate_subtasks(user=user, task_to_breakdown=task.get_subtask(2), subtask_num=3)

print(task)