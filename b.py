from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

test_case = LLMTestCase(
    input="ఫ్రాన్స్ రాజధాని ఏది?",
    actual_output="పారిస్",
)

answer_relevancy_metric = AnswerRelevancyMetric()
answer_relevancy_metric.measure(test_case)

print(answer_relevancy_metric.score, answer_relevancy_metric.reason)


# from deepeval.test_case import ArenaTestCase, LLMTestCase, SingleTurnParams, Contestant
# from deepeval.metrics import ArenaGEval
# from deepeval import compare

# a_test_case = ArenaTestCase(
#     contestants=[
#         Contestant(
#             name="GPT-4",
#             hyperparameters={"model": "gpt-4"},
#             test_case=LLMTestCase(
#                 input="เมืองหลวงของประเทศฝรั่งเศสคือเมืองอะไร?",
#                 actual_output="ปารีส",
#             ),
#         ),
#         Contestant(
#             name="Claude-4",
#             hyperparameters={"model": "claude-4"},
#             test_case=LLMTestCase(
#                 input="เมืองหลวงของประเทศฝรั่งเศสคือเมืองอะไร?",
#                 actual_output="เมืองหลวงของประเทศฝรั่งเศสคือกรุงปารีสครับ",
#             ),
#         )
#     ]
# )

# metric = ArenaGEval(
#     name="Friendly",
#     # Criteria translated to Thai: Focuses on friendliness and natural politeness
#     criteria="เลือกผู้ชนะจากผู้เข้าแข่งขันที่ตอบคำถามได้ดูเป็นกันเองและมีความสุภาพมากกว่า โดยพิจารณาจากการใช้ภาษาที่สละสลวยและการใช้หางเสียงในภาษาไทย",
#     evaluation_params=[
#         SingleTurnParams.INPUT,
#         SingleTurnParams.ACTUAL_OUTPUT,
#     ],
# )

# metric.measure(a_test_case)

# print(metric.winner, metric.reason)
