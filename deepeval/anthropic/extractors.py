from anthropic.types.message import Message
from anthropic.types import ToolUseBlock
from typing import Any, Dict

from deepeval.anthropic.utils import (
    render_messages_anthropic,
    stringify_anthropic_content,
)
from deepeval.model_integrations.types import InputParameters, OutputParameters
from deepeval.test_case.llm_test_case import ToolCall


def safe_extract_input_parameters(kwargs: Dict[str, Any]) -> InputParameters:
    # guarding against errors to be compatible with legacy APIs
    try:
        return extract_messages_api_input_parameters(kwargs)
    except:
        return InputParameters(model="NA")


def extract_messages_api_input_parameters(
    kwargs: Dict[str, Any],
) -> InputParameters:
    model = kwargs.get("model")
    system = kwargs.get("system")
    max_tokens = kwargs.get("max_tokens")
    tools = kwargs.get("tools")
    messages = kwargs.get("messages")
    tool_descriptions = (
        {tool["name"]: tool["description"] for tool in tools}
        if tools is not None
        else None
    )

    input_argument = ""
    user_messages = []
    for message in messages:
        role = message["role"]
        if role == "user":
            user_messages.append(message["content"])
    if len(user_messages) > 0:
        input_argument = user_messages[0]

    return InputParameters(
        model=model,
        system=system,
        max_tokens=max_tokens,
        input=stringify_anthropic_content(input_argument),
        messages=render_messages_anthropic(messages),
        tools=tools,
        tool_descriptions=tool_descriptions,
    )


def safe_extract_output_parameters(
    message_response: Message,
    input_parameters: InputParameters,
) -> OutputParameters:
    # guarding against errors to be compatible with legacy APIs
    try:
        return extract_messages_api_output_parameters(
            message_response, input_parameters
        )
    except:
        return OutputParameters()


def extract_messages_api_output_parameters(
    message_response: Message,
    input_parameters: InputParameters,
) -> OutputParameters:
    content = message_response.content[0]
    tools_called = None
    anthropic_tool_calls = [
        block
        for block in message_response.content
        if isinstance(block, ToolUseBlock)
    ]
    output = None
    if len(anthropic_tool_calls) == 0:
        output = str(message_response.content[0].text)
    else:
        output = str(message_response.content[0].to_json())
    if anthropic_tool_calls:
        tools_called = []
        tool_descriptions = input_parameters.tool_descriptions or {}
        for tool_call in anthropic_tool_calls:
            tools_called.append(
                ToolCall(
                    name=tool_call.name,
                    input_parameters=tool_call.input,
                    description=tool_descriptions.get(tool_call.name),
                )
            )
    return OutputParameters(
        content=content,
        output=output,
        role=message_response.role,
        type=message_response.type,
        usage={
            "input_tokens": message_response.usage.input_tokens,
            "output_tokens": message_response.usage.output_tokens,
        },
        tools_called=tools_called,
    )
