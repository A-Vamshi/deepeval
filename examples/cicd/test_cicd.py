from deepeval.dataset import EvaluationDataset, Golden
from deepeval.evaluate.configs import AsyncConfig, DisplayConfig
from deepeval.metrics import TaskCompletionMetric
from deepeval.tracing import observe

_QUIET_DISPLAY = DisplayConfig(show_indicator=False, print_results=False)

golden = Golden(
    input="I have a persistent cough and fever. Should I be worried?",
)
dataset = EvaluationDataset(goldens=[golden])

task_completion_metric = TaskCompletionMetric(async_mode=False)


@observe()
def health_advisor_agent(user_input: str):
    """Replace this with your traced LLM application."""
    return "Nah get lost"


def test_task_completion_cicd():
    for golden in dataset.evals_iterator(
        metrics=[task_completion_metric],
        display_config=_QUIET_DISPLAY,
        async_config=AsyncConfig(run_async=False),
    ):
        health_advisor_agent(golden.input)
