import tasks, userdata
from langchain_openai import ChatOpenAI

scene_generator = userdata.SceneGenerator(llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5))
task_generator = tasks.TaskGenerator(llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5))

user = userdata.User(name="윤형석",
                     location="서울",
                     birthdate="1990-03-28",
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

for scene in scenes.scenes:
    user.scenes.append(scene)
    
user.set_prompt()
task = task_generator.generate_task(user=user, task_name="파이썬 패키지 작성하기")

# subtask_of_subtask = tasks.Subtask("Subtask of Subtask 1")
# subtask.add_subtask(subtask_of_subtask)

# subtask.set_subtasks_index()

task.set_supertask_of_subtasks()
task.set_subtasks_index()
task.print_self()