try:
    import anthropic  # noqa: F401
except ImportError:
    raise ModuleNotFoundError(
        "Please install anthropic to use this feature: 'pip install anthropic'"
    )

try:
    from anthropic import Anthropic, AsyncAnthropic  # noqa: F401
except ImportError:
    Anthropic = None  # type: ignore
    AsyncAnthropic = None  # type: ignore

if Anthropic or AsyncAnthropic:
    from deepeval.anthropic.patch import patch_anthropic_classes  # type: ignore

    patch_anthropic_classes()
