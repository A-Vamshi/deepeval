
"""
5. TypeScript support: npx deepeval test run sending git details, and a TypeScript link-ci.
6. GitLab.
7. deepeval link-ci --datasets, which sets up the existing eval gate from the CLI.
8. Smaller items:
"""

from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams


def test_refund_answer():
    test_case = LLMTestCase(
        input="What if these shoes don't fit?",
        # Replace this with the actual output of your LLM application
        actual_output="We offer a 30-day full refund at no extra cost.",
        expected_output="You're eligible for a free full refund within 30 days of purchase.",
    )
    correctness_metric = GEval(
        name="Correctness",
        criteria="Determine if the actual output is correct according to the expected output.",
        evaluation_params=[
            SingleTurnParams.ACTUAL_OUTPUT,
            SingleTurnParams.EXPECTED_OUTPUT,
        ],
        threshold=0.5,
    )
    assert_test(test_case, [correctness_metric])
