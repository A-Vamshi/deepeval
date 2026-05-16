from deepeval.evaluate.utils import create_metric_data, metric_matches_required
from deepeval.metrics import TaskCompletionMetric


def test_create_metric_data_includes_metric_class_name():
    metric = TaskCompletionMetric(async_mode=False)
    metric_data = create_metric_data(metric)

    assert metric_data.name == "Task Completion"
    assert metric_data.metric_class_name == "TaskCompletionMetric"
    dumped = metric_data.model_dump(by_alias=True)
    assert "metricClassName" not in dumped
    assert "metric_class_name" not in dumped


def test_metric_matches_required_uses_class_name():
    metric = TaskCompletionMetric(async_mode=False)
    metric_data = create_metric_data(metric)

    assert metric_matches_required(metric_data, ["TaskCompletionMetric"])
    assert not metric_matches_required(metric_data, ["Task Completion"])
