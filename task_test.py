import userdata, utils
from langchain_openai import ChatOpenAI
from LLMs import SceneGenerator, TaskGenerator, TaskCommenter

scene_generator = SceneGenerator(llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5))
task_generator = TaskGenerator(llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5))
task_commenter = TaskCommenter(llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5))

tracker = utils.PerformanceTracker()

user = userdata.User(name="윤형석",
                     residence="서울",
                     birth_date="1990-03-28",
                     occupation="개발자",
                     personality=['Introverted', 'Intuitive', 'Thinking', 'Perceiving'],
                     prompt="")

scenes = scene_generator.process(user=user,
                                 timeout=15,
                                 scenes=["출퇴근길",
                                         "근무",
                                         "휴식",
                                         "공부",
                                         "게임",
                                         "유튜브 시청",
                                         "애완동물 돌보기"])
user.append_scenes(scenes)
user.collect_tags()

responses = tracker.measure(user.generate_prompt, timeout=60)

for i, response in enumerate(responses):
    print(f"{i}: {response}")

prompt_index = input("프롬프트 중 선택할 인덱스를 입력하세요: ")
user.set_prompt(responses=responses, index=int(prompt_index))
print(user)

print(task_generator._process_paraphrase(user=user, input_to_paraphrase="자동차 정비소 방문하기"))

# task = tracker.measure(task_generator.process,
#                        timeout=15,
#                        user=user,
#                        task_name="에견카페 방문하기",
#                        subtask_num=5)

# print(task)
# subtask_num = input("하위 작업의 개수를 입력하세요: ")
# task_generator.process(timeout=15,
#                        processor_func=task_generator._process_subtasks,
#                        user=user,
#                        task_to_breakdown=task,
#                        subtask_num=int(subtask_num))
# print(task)
# task_to_break = input("하위 작업을 추가할 상위 작업의 인덱스를 입력하세요: ")
# tracker.measure(task_generator.process,
#                 timeout=15,
#                 processor_func=task_generator._process_subtasks,
#                 user=user,
#                 task_to_breakdown=task.get_subtask(int(task_to_break)-1),
#                 subtask_num=3)
# print(task)

# tracker.measure(task_commenter.process, 
#                 user=user, 
#                 task_to_comment=task)
# # task_commenter.process(user=user, task_to_comment=task.get_subtask(4))

# print(task)

# print(tracker.get_summary())