import tasks, userdata
from langchain_openai import ChatOpenAI

scene_generator = userdata.SceneGenerator(llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5))
task_generator = tasks.TaskGenerator(llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5))

user = userdata.User(name="윤형석",
                     residence="서울",
                     birth_date="1990-03-28",
                     occupation="개발자",
                     personality=['Introverted', 'Intuitive', 'Thinking', 'Perceiving'],
                     prompt="")

scenes = scene_generator.generate_scenes(user=user,
                                         scenes=["출퇴근길",
                                                "근무",
                                                "휴식",
                                                "공부",
                                                "게임",
                                                "유튜브 시청",
                                                "애완동물 돌보기"])
user.append_scenes(scenes)
user.collect_tags()

responses = user.generate_prompt()

for i, response in enumerate(responses):
    print(f"{i}: {response}")

prompt_index = input("프롬프트 중 선택할 인덱스를 입력하세요: ")
user.set_prompt(responses=responses, index=int(prompt_index))
print(user)

task = task_generator.generate_task(user=user, task_name="체중 감량을 위해 운동하기", subtask_num=0)
print(task)
subtask_num = input("하위 작업의 개수를 입력하세요: ")
task_generator.generate_subtasks(user=user, task_to_breakdown=task, subtask_num=int(subtask_num))
print(task)
task_to_break = input("하위 작업을 추가할 상위 작업의 인덱스를 입력하세요: ")
task_generator.generate_subtasks(user=user, task_to_breakdown=task.get_subtask(int(task_to_break)-1), subtask_num=3)
print(task)