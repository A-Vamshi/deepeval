# import asyncio
# import os
# from typing import Dict, Any

# from deepeval.dataset import EvaluationDataset, Golden
# from deepeval.metrics import ExactMatchMetric, GEval, StepEfficiencyMetric, TaskCompletionMetric
# from deepeval.test_case import SingleTurnParams
# from deepeval.test_run import hyperparameters
# from deepeval.tracing import observe, update_current_trace
# from deepeval.evaluate.configs import AsyncConfig




# dataset = EvaluationDataset(
#     goldens=[
#         Golden(input="This is a tool call")
#     ]
# )

# @observe(type="agent", name="qa_end_to_end_eval_runner")
# def run_qa_agent(golden: Golden) -> str:
#     user_role = _user_role_from_golden(golden)
#     thread_id = "generate_thread_id()"

#     update_current_trace(
#         name="qa-end-to-end-evals",
#         input=golden.input,
#         expected_output=golden.expected_output,
#         tags=["qa", "end-to-end", "evals_iterator"],
#         metadata={
#             "thread_id": thread_id,
#             "user_role": user_role,
#             "script": os.path.basename(__file__),
#         },
#     )

#     result = f"""orchestrate_agents(
#         query={golden.input},
#         user_role={user_role},
#         thread_id={thread_id},
#     )"""
#     final_response = str(result.get("final_response", ""))

#     update_current_trace(
#         output=final_response,
#         retrieval_context=result.get("retrieval_context"),
#         tools_called=result.get("tool_calls"),
#     )

#     return final_response


# def _user_role_from_golden(golden: Golden) -> str:
#     metadata: Dict[str, Any] = golden.additional_metadata or {}
#     return str(metadata.get("user_role", "QA Internal Employee"))

# metric = GEval(
#     name="Text-SQL Efficiency",
#     criteria="Evaluate the efficiency of the text-to-SQL conversion.",
#     evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.EXPECTED_OUTPUT, SingleTurnParams.ACTUAL_OUTPUT],
# )


# for golden in dataset.evals_iterator(
#     metrics=[TaskCompletionMetric(), StepEfficiencyMetric()],
#     async_config=AsyncConfig(run_async=True, max_concurrent=5),
#     identifier="single-turn-qa",
# ):
#     task = asyncio.create_task(asyncio.to_thread(run_qa_agent, golden))
#     dataset.evaluate(task)


from deepeval.test_case import ToolCall

tool_call = ToolCall(
    name="Something",
    description="Something too",
    input_parameters={
        "yesh": "Nah"
    }
)

print(tool_call.model_dump_json())