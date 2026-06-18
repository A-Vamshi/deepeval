from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric
from deepeval import evaluate

test_case = LLMTestCase(
    input="What is 1+1?",
    actual_output="It's either 3 or 2. And I like science better"
)

metric = AnswerRelevancyMetric()

metric.measure(test_case)
print(metric.score)
print(metric.reason)
evaluate([test_case], [metric])
