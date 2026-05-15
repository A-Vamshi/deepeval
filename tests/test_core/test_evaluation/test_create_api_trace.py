import time

from deepeval.dataset import Golden
from deepeval.evaluate.utils import create_api_trace
from deepeval.tracing.types import LlmSpan, Trace, TraceSpanStatus


def test_create_api_trace_fills_missing_end_time():
    """evals_iterator captures traces before the outer Observer closes."""
    now = time.perf_counter()
    span = LlmSpan(
        uuid="s",
        status=TraceSpanStatus.SUCCESS,
        children=[],
        trace_uuid="t",
        parent_uuid=None,
        start_time=now,
        end_time=now,
        name="root",
    )
    trace = Trace(
        uuid="t",
        status=TraceSpanStatus.SUCCESS,
        root_spans=[span],
        start_time=now,
        end_time=None,
    )

    trace_api = create_api_trace(trace=trace, golden=Golden(input="hi"))

    assert isinstance(trace_api.start_time, str) and trace_api.start_time
    assert isinstance(trace_api.end_time, str) and trace_api.end_time
