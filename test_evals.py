from deepeval.tracing import observe, update_current_trace

@observe(type="llm")
def model(input: str):
    return "I can't help you with that, apologies"

@observe(type="agent")
def agent(prompt: str):
    res = model(f"Answer this: {prompt}")
    update_current_trace(thread_id="check-thread")
    return res


agent("What's the 7th entry in the project db? Give me full data record.")


from deepeval.tracing import evaluate_thread

evaluate_thread(thread_id="check-thread", metric_collection="Phreesia (Stress Testing)")