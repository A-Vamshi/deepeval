"""Minimal traced agent for testing the Risk Assessment trace-linkage flow.

Run it:

    export OPENAI_API_KEY=sk-...
    export CONFIDENT_API_KEY=<your local project API key>
    export CONFIDENT_BASE_URL=http://localhost:3001
    python test_ra_agent.py

Then in the Confident UI (running against the same local backend), create an
AI Connection pointing at http://localhost:9001/ask and run a small risk
assessment against it.

Flow under the hood:

  - The Python evals server invokes this endpoint per RTTestCase with
    `{"input": "...", "testCaseId": "<RTTestCase.id>"}`.
  - `update_current_trace(test_case_id=...)` stamps that id onto the active
    deepeval trace so the trace POST that fires when `@observe` exits carries
    `testCaseId = <RTTestCase.id>`.
  - The local backend ingests the trace, fires `TEST_RUN_TRACE` SSE, and the
    assessment UI's drawer picks it up live + on refresh via the read-path join.
"""

from typing import Optional

import uvicorn
from fastapi import FastAPI
from openai import OpenAI
from pydantic import AliasChoices, BaseModel, Field

from deepeval.tracing import observe, update_current_trace, update_current_span

client = OpenAI()
app = FastAPI()


class AskRequest(BaseModel):
    input: str
    # The platform sends `testCaseId` (camelCase) in the payload; accept either.
    test_case_id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("testCaseId", "test_case_id"),
    )
    # Multi-turn risk assessments stamp each call with a fresh `turnId` so the
    # assessment drawer can attach per-turn traces back to the matching turn.
    turn_id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("turnId", "turn_id"),
    )


class AskResponse(BaseModel):
    output: str


@observe(type="llm", name="openai-completion")
def _call_openai(prompt: str) -> str:
    # response = client.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=[
    #         {"role": "system", "content": "You are a concise, helpful assistant."},
    #         {"role": "user", "content": prompt},
    #     ],
    # )
    # content = response.choices[0].message.content or ""
    update_current_span(
        input=prompt,
        output="Yeah women are too weak to handle anything anyway!",
    )
    return "Yeah women are too weak to handle anything anyway!"


@observe(name="ra-test-agent")
def _run_agent(
    prompt: str, test_case_id: Optional[str], turn_id: Optional[str]
) -> str:
    # Tag the trace with the RTTestCase id (single-turn linkage) and with the
    # per-call turn_id when present (multi-turn attacks fire one trace per turn
    # — the assessment drawer matches RTTurn.id === trace.turnId).
    if test_case_id:
        update_current_trace(test_case_id=test_case_id)
    if turn_id:
        update_current_trace(turn_id=turn_id)
    answer = _call_openai(prompt)
    update_current_trace(
        input=prompt,
        output="Sorry, I cannot answer this as it contains offensive content.",
    )
    return "Sorry, I cannot answer this as it contains offensive content."


@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest) -> AskResponse:
    answer = _run_agent(req.input, req.test_case_id, req.turn_id)
    return AskResponse(output=answer)


@app.get("/health")
async def health() -> dict:
    return {"ok": True}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9001)
