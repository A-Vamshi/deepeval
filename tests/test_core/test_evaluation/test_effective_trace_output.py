import time

from deepeval.constants import PYTEST_TRACE_TEST_WRAPPER_SPAN_NAME
from deepeval.evaluate.execute._common import (
    get_effective_trace_output,
    get_true_root_span_recursively,
)
from deepeval.tracing.types import BaseSpan, Trace, TraceSpanStatus


def _wrapper_span(*, children):
    return BaseSpan(
        uuid="wrapper",
        name=PYTEST_TRACE_TEST_WRAPPER_SPAN_NAME,
        status=TraceSpanStatus.SUCCESS,
        children=children,
        trace_uuid="t",
        parent_uuid=None,
        start_time=time.perf_counter(),
        end_time=time.perf_counter(),
    )


def _user_span(*, output: str):
    return BaseSpan(
        uuid="user",
        name="health_advisor_agent",
        status=TraceSpanStatus.SUCCESS,
        children=[],
        trace_uuid="t",
        parent_uuid="wrapper",
        start_time=time.perf_counter(),
        end_time=time.perf_counter(),
        output=output,
    )


def test_get_effective_trace_output_skips_nested_pytest_wrappers():
    user = _user_span(output="advice text")
    inner_wrapper = _wrapper_span(children=[user])
    outer_wrapper = _wrapper_span(children=[inner_wrapper])
    trace = Trace(
        uuid="t",
        status=TraceSpanStatus.SUCCESS,
        root_spans=[outer_wrapper],
        start_time=time.perf_counter(),
        end_time=None,
    )

    assert get_true_root_span_recursively(trace) is user
    assert get_effective_trace_output(trace) == "advice text"
