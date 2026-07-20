"""Minimal offline eval used to exercise the deepeval[bot] PR-comment flow.

Uses a static custom metric so the run needs no LLM/API keys — the point is to
produce a test result that `deepeval test run` posts to the PR, not to measure
anything real.
"""

from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import BaseMetric


class AlwaysPassMetric(BaseMetric):
    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        self.async_mode = False
        self.include_reason = True
        self.strict_mode = False
        self.evaluation_cost = 0.0

    def measure(self, test_case: LLMTestCase, *args, **kwargs) -> float:
        self.score = 1.0
        self.success = self.score >= self.threshold
        self.reason = "Static metric for the PR-comment E2E test."
        return self.score

    async def a_measure(self, test_case: LLMTestCase, *args, **kwargs) -> float:
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return self.success

    @property
    def __name__(self):
        return "Always Pass"


def test_pr_comment():
    test_case = LLMTestCase(
        input="What is the capital of France?",
        actual_output="Paris",
        expected_output="Paris",
    )
    assert_test(test_case, [AlwaysPassMetric()])
